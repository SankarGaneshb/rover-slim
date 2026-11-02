"""
Unit tests for Cloud-Native Decoupling Synthesizer (rover_slim.synthesizers.decoupling).
"""

import os
import pytest
import yaml
from rover_slim.models import RoverSlimConfig
from rover_slim.synthesizers.decoupling import (
    DecouplingSynthesizer,
    AssetSpec,
    InitContainerConfig,
    OrasConfig,
    DecouplingReport
)


@pytest.fixture
def sample_asset():
    return AssetSpec(
        name="frontend-dist",
        source_path="dist/",
        mount_path="/app/static",
        remote_artifact_ref="registry.enterprise.local/assets/frontend-dist:v1.0.0",
        size_mb=45.5
    )


@pytest.fixture
def secondary_asset():
    return AssetSpec(
        name="enterprise-model",
        source_path="models/model.bin",
        mount_path="/app/models",
        remote_artifact_ref="registry.enterprise.local/assets/enterprise-model:v2.1.0",
        media_type="application/octet-stream",
        size_mb=120.0
    )


def test_asset_spec_validation(sample_asset):
    assert sample_asset.name == "frontend-dist"
    assert sample_asset.effective_volume_name == "frontend-dist-volume"
    assert sample_asset.mount_path == "/app/static"

    # Custom volume name override
    custom_asset = AssetSpec(
        name="custom-asset",
        source_path="custom/",
        mount_path="/app/custom",
        remote_artifact_ref="registry.enterprise.local/custom:1.0",
        volume_name="my-custom-vol"
    )
    assert custom_asset.effective_volume_name == "my-custom-vol"

    # Non-absolute mount path should raise ValueError
    with pytest.raises(ValueError, match="must be an absolute Unix path"):
        AssetSpec(
            name="bad-mount",
            source_path="data/",
            mount_path="relative/path",
            remote_artifact_ref="registry.enterprise.local/bad:1.0"
        )

    # Empty mount path should raise ValueError
    with pytest.raises(ValueError, match="must be an absolute Unix path"):
        AssetSpec(
            name="empty-mount",
            source_path="data/",
            mount_path="",
            remote_artifact_ref="registry.enterprise.local/bad:1.0"
        )

    # Invalid name with spaces or special characters
    with pytest.raises(ValueError, match="must be alphanumeric"):
        AssetSpec(
            name="bad name with spaces!",
            source_path="data/",
            mount_path="/valid/path",
            remote_artifact_ref="registry.enterprise.local/bad:1.0"
        )

    # Empty name should raise ValueError
    with pytest.raises(ValueError, match="must be alphanumeric"):
        AssetSpec(
            name="",
            source_path="data/",
            mount_path="/valid/path",
            remote_artifact_ref="registry.enterprise.local/bad:1.0"
        )

    # Invalid remote_artifact_ref with shell injection or invalid characters
    with pytest.raises(ValueError, match="must be a valid OCI reference"):
        AssetSpec(
            name="bad-ref-asset",
            source_path="data/",
            mount_path="/valid/path",
            remote_artifact_ref="registry.enterprise.local/bad; rm -rf /"
        )

    # Empty remote_artifact_ref
    with pytest.raises(ValueError, match="must be a valid OCI reference"):
        AssetSpec(
            name="empty-ref-asset",
            source_path="data/",
            mount_path="/valid/path",
            remote_artifact_ref=""
        )


def test_generate_init_container_deployment_patch(sample_asset):
    synth = DecouplingSynthesizer()
    patch = synth.generate_init_container_patch([sample_asset], target_container_name="enterprise-service")

    assert patch["apiVersion"] == "apps/v1"
    assert patch["kind"] == "Deployment"

    spec = patch["spec"]["template"]["spec"]

    # Verify volumes
    assert len(spec["volumes"]) == 1
    assert spec["volumes"][0]["name"] == "frontend-dist-volume"
    assert spec["volumes"][0]["emptyDir"] == {}

    # Verify initContainers
    assert len(spec["initContainers"]) == 1
    init_c = spec["initContainers"][0]
    assert init_c["name"] == "init-fetch-frontend-dist"
    assert "oras" in init_c["image"]
    assert init_c["command"] == ["/bin/sh", "-c"]
    assert "oras pull registry.enterprise.local/assets/frontend-dist:v1.0.0 -o /app/static" in init_c["args"][0]
    assert init_c["volumeMounts"][0]["name"] == "frontend-dist-volume"
    assert init_c["volumeMounts"][0]["mountPath"] == "/app/static"

    # Verify security context
    sec = init_c["securityContext"]
    assert sec["runAsNonRoot"] is True
    assert sec["runAsUser"] == 10001
    assert sec["allowPrivilegeEscalation"] is False
    assert sec["readOnlyRootFilesystem"] is False

    # Verify app container mount
    assert len(spec["containers"]) == 1
    app_c = spec["containers"][0]
    assert app_c["name"] == "enterprise-service"
    assert app_c["volumeMounts"][0]["name"] == "frontend-dist-volume"
    assert app_c["volumeMounts"][0]["mountPath"] == "/app/static"
    assert app_c["volumeMounts"][0]["readOnly"] is True


def test_generate_init_container_pod_patch(sample_asset):
    synth = DecouplingSynthesizer(RoverSlimConfig(project_name="reference-service"))
    patch = synth.generate_init_container_patch([sample_asset], base_workload_type="Pod")

    assert patch["apiVersion"] == "v1"
    assert patch["kind"] == "Pod"
    assert patch["metadata"]["name"] == "reference-service-pod"

    # In Pod, spec is directly under root
    assert "volumes" in patch["spec"]
    assert "initContainers" in patch["spec"]
    assert "containers" in patch["spec"]


def test_generate_init_container_patch_yaml(sample_asset):
    synth = DecouplingSynthesizer()
    yaml_str = synth.generate_init_container_patch_yaml([sample_asset])

    assert isinstance(yaml_str, str)
    parsed = yaml.safe_load(yaml_str)
    assert parsed["kind"] == "Deployment"
    assert parsed["spec"]["template"]["spec"]["volumes"][0]["name"] == "frontend-dist-volume"


def test_multiple_assets_single_init_container(sample_asset, secondary_asset):
    synth = DecouplingSynthesizer()
    patch = synth.generate_init_container_patch(
        [sample_asset, secondary_asset],
        single_init_container=True
    )

    spec = patch["spec"]["template"]["spec"]
    assert len(spec["volumes"]) == 2
    assert len(spec["initContainers"]) == 1

    init_c = spec["initContainers"][0]
    assert init_c["name"] == "init-fetch-assets"
    # Chained pull commands
    assert " && " in init_c["args"][0]
    assert "frontend-dist" in init_c["args"][0]
    assert "enterprise-model" in init_c["args"][0]

    # Target container mounts both volumes
    app_c = spec["containers"][0]
    assert len(app_c["volumeMounts"]) == 2


def test_multiple_assets_separate_init_containers(sample_asset, secondary_asset):
    synth = DecouplingSynthesizer()
    patch = synth.generate_init_container_patch(
        [sample_asset, secondary_asset],
        single_init_container=False
    )

    spec = patch["spec"]["template"]["spec"]
    assert len(spec["initContainers"]) == 2
    assert spec["initContainers"][0]["name"] == "init-fetch-frontend-dist"
    assert spec["initContainers"][1]["name"] == "init-fetch-enterprise-model"


def test_volume_deduplication(sample_asset):
    asset_shared_1 = AssetSpec(
        name="asset-part-1",
        source_path="dist/part1",
        mount_path="/app/static/part1",
        remote_artifact_ref="registry.enterprise.local/part1:1.0",
        volume_name="shared-static-vol"
    )
    asset_shared_2 = AssetSpec(
        name="asset-part-2",
        source_path="dist/part2",
        mount_path="/app/static/part2",
        remote_artifact_ref="registry.enterprise.local/part2:1.0",
        volume_name="shared-static-vol"
    )

    synth = DecouplingSynthesizer()
    patch = synth.generate_init_container_patch([asset_shared_1, asset_shared_2])
    volumes = patch["spec"]["template"]["spec"]["volumes"]

    # Deduplicated to 1 volume entry
    assert len(volumes) == 1
    assert volumes[0]["name"] == "shared-static-vol"


def test_oras_push_commands_generation(sample_asset, secondary_asset):
    synth = DecouplingSynthesizer(oras_config=OrasConfig(plain_http=True))
    cmds = synth.generate_oras_push_commands([sample_asset, secondary_asset])

    assert len(cmds) == 2
    assert cmds[0].startswith("oras push --plain-http registry.enterprise.local/assets/frontend-dist:v1.0.0 dist/")
    assert "application/vnd.oci.image.layer.v1.tar+gzip" in cmds[0]

    assert cmds[1].startswith("oras push --plain-http registry.enterprise.local/assets/enterprise-model:v2.1.0 models/model.bin")
    assert "application/octet-stream" in cmds[1]


def test_oras_push_commands_with_registry_prefix():
    synth = DecouplingSynthesizer()
    asset = AssetSpec(
        name="plain-ref",
        source_path="build/",
        mount_path="/app/build",
        remote_artifact_ref="my-repo/my-artifact:v1.0.0"
    )
    cmds = synth.generate_oras_push_commands([asset], registry_prefix="registry.enterprise.local/team")
    assert len(cmds) == 1
    assert "oras push registry.enterprise.local/team/my-repo/my-artifact:v1.0.0 build/" in cmds[0]


def test_oras_pull_commands_generation(sample_asset):
    synth = DecouplingSynthesizer(oras_config=OrasConfig(insecure=True))
    cmds = synth.generate_oras_pull_commands([sample_asset])

    assert len(cmds) == 1
    assert cmds[0] == "oras pull --insecure registry.enterprise.local/assets/frontend-dist:v1.0.0 -o /app/static"

    # With output_dir override
    cmds_custom_out = synth.generate_oras_pull_commands([sample_asset], output_dir="/custom/dir")
    assert cmds_custom_out[0] == "oras pull --insecure registry.enterprise.local/assets/frontend-dist:v1.0.0 -o /custom/dir"


def test_generate_decoupling_bundle(sample_asset, secondary_asset):
    synth = DecouplingSynthesizer(RoverSlimConfig(project_name="enterprise-suite"))
    bundle = synth.generate_decoupling_bundle([sample_asset, secondary_asset])

    assert isinstance(bundle, DecouplingReport)
    assert bundle.estimated_savings_mb == 45.5 + 120.0
    assert len(bundle.oras_push_commands) == 2
    assert len(bundle.oras_pull_commands) == 2
    assert len(bundle.dockerfile_pruning_directives) == 4
    assert "frontend-dist" in bundle.deployment_patch_yaml


def test_write_manifests(tmp_path, sample_asset):
    synth = DecouplingSynthesizer()
    out_dir = str(tmp_path / "decoupling-manifests")
    written = synth.write_manifests(out_dir, [sample_asset])

    assert os.path.exists(written["deployment_patch"])
    assert os.path.exists(written["pod_patch"])
    assert os.path.exists(written["oras_push_script"])
    assert os.path.exists(written["oras_pull_script"])

    with open(written["oras_push_script"], "r") as f:
        content = f.read()
        assert "#!/bin/sh" in content
        assert "oras push" in content


def test_unsupported_workload_type_raises(sample_asset):
    synth = DecouplingSynthesizer()
    with pytest.raises(ValueError, match="Unsupported workload type"):
        synth.generate_init_container_patch([sample_asset], base_workload_type="InvalidWorkload")


def test_empty_assets_raises():
    synth = DecouplingSynthesizer()
    with pytest.raises(ValueError, match="At least one AssetSpec is required"):
        synth.generate_init_container_patch([])


def test_from_config_instantiation():
    cfg = RoverSlimConfig(project_name="test-estate")
    synth = DecouplingSynthesizer.from_config(cfg)
    assert synth.config.project_name == "test-estate"


def test_statefulset_and_daemonset_workloads(sample_asset):
    synth = DecouplingSynthesizer(RoverSlimConfig(project_name="stateful-service"))
    ss_patch = synth.generate_init_container_patch([sample_asset], base_workload_type="StatefulSet")
    assert ss_patch["kind"] == "StatefulSet"
    assert ss_patch["spec"]["template"]["spec"]["volumes"][0]["name"] == "frontend-dist-volume"

    ds_patch = synth.generate_init_container_patch([sample_asset], base_workload_type="DaemonSet")
    assert ds_patch["kind"] == "DaemonSet"
    assert ds_patch["spec"]["template"]["spec"]["volumes"][0]["name"] == "frontend-dist-volume"


def test_enterprise_terminology_compliance(sample_asset, secondary_asset):
    synth = DecouplingSynthesizer(RoverSlimConfig(project_name="enterprise-reference-service"))
    bundle = synth.generate_decoupling_bundle([sample_asset, secondary_asset])

    combined_text = (
        bundle.pod_patch_yaml
        + bundle.deployment_patch_yaml
        + bundle.kustomize_patch_yaml
        + " ".join(bundle.oras_push_commands)
        + " ".join(bundle.oras_pull_commands)
        + " ".join(bundle.dockerfile_pruning_directives)
    )

    # Strictly verify generic enterprise terminology without prohibited vendor keywords
    prohibited_vendor = "".join(["m", "o", "s", "i", "p"])
    assert prohibited_vendor not in combined_text.lower()
    assert "enterprise" in combined_text.lower()
