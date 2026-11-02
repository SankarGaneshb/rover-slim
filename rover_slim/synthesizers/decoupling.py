"""
Cloud-Native Decoupling Synthesizer for Rover-Slim.

Generates:
1. Kubernetes Pod and Deployment manifest patches with shared emptyDir volumes and init containers.
2. ORAS (OCI Registry as Storage) CLI commands to push/pull non-container static artifacts to/from OCI registries.
3. Automated Dockerfile static asset pruning recommendations.
"""

import os
import re
from typing import List, Dict, Any, Optional
import yaml
from pydantic import BaseModel, Field, field_validator
from rover_slim.models import RoverSlimConfig


class AssetSpec(BaseModel):
    """Specification for a static heavy asset decoupled from the runtime container image."""

    name: str = Field(..., description="Unique alphanumeric identifier for the asset (e.g. frontend-dist, ml-weights)")
    source_path: str = Field(..., description="Local repository path containing the asset (e.g. dist/, static/, models/model.bin)")
    mount_path: str = Field(..., description="Target mount path inside the application container (e.g. /app/static, /app/models)")
    remote_artifact_ref: str = Field(..., description="OCI artifact reference in container registry (e.g. registry.enterprise.local/assets/frontend:v1.0.0)")
    media_type: Optional[str] = Field("application/vnd.oci.image.layer.v1.tar+gzip", description="OCI layer media type")
    volume_name: Optional[str] = Field(None, description="Kubernetes volume name (defaults to sanitized '<name>-volume')")
    size_mb: Optional[float] = Field(0.0, description="Estimated size in MB for telemetry and optimization metrics")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not re.match(r"^[a-zA-Z0-9][-a-zA-Z0-9_.]*$", v):
            raise ValueError(f"Asset name '{v}' must be alphanumeric and conform to Kubernetes naming conventions.")
        return v

    @field_validator("mount_path")
    @classmethod
    def validate_mount_path(cls, v: str) -> str:
        if not v or not v.startswith("/"):
            raise ValueError(f"Mount path '{v}' must be an absolute Unix path starting with '/'.")
        return v

    @field_validator("remote_artifact_ref")
    @classmethod
    def validate_remote_artifact_ref(cls, v: str) -> str:
        if not v or not re.match(r"^[a-zA-Z0-9_./:@-]+$", v):
            raise ValueError(
                f"Remote artifact reference '{v}' must be a valid OCI reference matching '^[a-zA-Z0-9_./:@-]+$'."
            )
        return v

    @property
    def effective_volume_name(self) -> str:
        if self.volume_name:
            return self.volume_name
        sanitized = re.sub(r"[^a-zA-Z0-9-]", "-", self.name.lower()).strip("-")
        return f"{sanitized}-volume"


class InitContainerConfig(BaseModel):
    """Configuration for the Kubernetes init container responsible for asset hydration."""

    image: str = Field("ghcr.io/oras-project/oras:v1.2.2", description="Container image used for asset fetching")
    pull_policy: str = Field("IfNotPresent", description="Image pull policy: IfNotPresent, Always, Never")
    cpu_request: str = Field("50m", description="CPU request for init container")
    cpu_limit: str = Field("200m", description="CPU limit for init container")
    memory_request: str = Field("64Mi", description="Memory request for init container")
    memory_limit: str = Field("256Mi", description="Memory limit for init container")
    run_as_user: int = Field(10001, description="Non-root user ID for execution")
    run_as_non_root: bool = Field(True, description="Enforce non-root execution")
    allow_privilege_escalation: bool = Field(False, description="Disallow privilege escalation")
    read_only_root_filesystem: bool = Field(False, description="Whether root filesystem is read-only")


class OrasConfig(BaseModel):
    """Configuration options for ORAS CLI commands."""

    registry_prefix: Optional[str] = Field(None, description="Default registry prefix (e.g. registry.enterprise.local/assets)")
    plain_http: bool = Field(False, description="Use HTTP instead of HTTPS")
    insecure: bool = Field(False, description="Allow insecure SSL connections")
    concurrency: int = Field(3, description="Concurrent layer transfer threads")


class DecouplingReport(BaseModel):
    """Result payload containing generated Kubernetes patches, ORAS commands, and metrics."""

    assets: List[AssetSpec]
    pod_patch: Dict[str, Any]
    pod_patch_yaml: str
    deployment_patch: Dict[str, Any]
    deployment_patch_yaml: str
    kustomize_patch_yaml: str
    oras_push_commands: List[str]
    oras_pull_commands: List[str]
    dockerfile_pruning_directives: List[str]
    estimated_savings_mb: float


class DecouplingSynthesizer:
    """
    Synthesizes Cloud-Native Decoupling Patterns:
    - Kubernetes Init Container manifest patches mounting shared emptyDir volumes.
    - ORAS (OCI Registry as Storage) commands for pushing and pulling non-container static assets.
    - Automated Dockerfile static asset pruning recommendations.
    """

    def __init__(
        self,
        config: Optional[RoverSlimConfig] = None,
        init_container_config: Optional[InitContainerConfig] = None,
        oras_config: Optional[OrasConfig] = None,
    ):
        self.config = config or RoverSlimConfig(project_name="enterprise-app")
        self.init_config = init_container_config or InitContainerConfig()
        self.oras_config = oras_config or OrasConfig()

    @classmethod
    def from_config(cls, config: RoverSlimConfig) -> "DecouplingSynthesizer":
        """Instantiates synthesizer using settings from RoverSlimConfig."""
        return cls(config=config)

    def generate_init_container_patch(
        self,
        assets: List[AssetSpec],
        target_container_name: Optional[str] = "app",
        base_workload_type: str = "Deployment",
        single_init_container: bool = True,
    ) -> Dict[str, Any]:
        """
        Generates a Kubernetes JSON/dictionary patch with shared emptyDir volumes,
        ORAS-powered init containers, and target container volume mounts.
        """
        if not assets:
            raise ValueError("At least one AssetSpec is required to generate a decoupling patch.")

        allowed_workloads = ("Deployment", "Pod", "StatefulSet", "DaemonSet")
        if base_workload_type not in allowed_workloads:
            raise ValueError(f"Unsupported workload type '{base_workload_type}'. Supported: {allowed_workloads}")

        # 1. Deduplicate shared volumes by effective_volume_name
        volumes = []
        seen_volumes = set()
        for asset in assets:
            vol_name = asset.effective_volume_name
            if vol_name not in seen_volumes:
                volumes.append({
                    "name": vol_name,
                    "emptyDir": {},
                })
                seen_volumes.add(vol_name)

        # 2. Build init container(s)
        flags = ""
        if self.oras_config.plain_http:
            flags += " --plain-http"
        if self.oras_config.insecure:
            flags += " --insecure"

        init_containers = []
        if single_init_container:
            pull_cmds = []
            init_mounts = []
            seen_mounts = set()
            for asset in assets:
                pull_cmds.append(f"oras pull {asset.remote_artifact_ref} -o {asset.mount_path}{flags}")
                if asset.mount_path not in seen_mounts:
                    init_mounts.append({
                        "name": asset.effective_volume_name,
                        "mountPath": asset.mount_path,
                    })
                    seen_mounts.add(asset.mount_path)

            combined_command = " && ".join(pull_cmds)
            init_container_name = "init-fetch-assets" if len(assets) > 1 else f"init-fetch-{assets[0].name}"

            init_containers.append({
                "name": init_container_name,
                "image": self.init_config.image,
                "imagePullPolicy": self.init_config.pull_policy,
                "command": ["/bin/sh", "-c"],
                "args": [combined_command],
                "volumeMounts": init_mounts,
                "resources": {
                    "limits": {
                        "cpu": self.init_config.cpu_limit,
                        "memory": self.init_config.memory_limit,
                    },
                    "requests": {
                        "cpu": self.init_config.cpu_request,
                        "memory": self.init_config.memory_request,
                    },
                },
                "securityContext": {
                    "allowPrivilegeEscalation": self.init_config.allow_privilege_escalation,
                    "readOnlyRootFilesystem": self.init_config.read_only_root_filesystem,
                    "runAsNonRoot": self.init_config.run_as_non_root,
                    "runAsUser": self.init_config.run_as_user,
                },
            })
        else:
            for asset in assets:
                cmd = f"oras pull {asset.remote_artifact_ref} -o {asset.mount_path}{flags}"
                init_containers.append({
                    "name": f"init-fetch-{asset.name}",
                    "image": self.init_config.image,
                    "imagePullPolicy": self.init_config.pull_policy,
                    "command": ["/bin/sh", "-c"],
                    "args": [cmd],
                    "volumeMounts": [{
                        "name": asset.effective_volume_name,
                        "mountPath": asset.mount_path,
                    }],
                    "resources": {
                        "limits": {
                            "cpu": self.init_config.cpu_limit,
                            "memory": self.init_config.memory_limit,
                        },
                        "requests": {
                            "cpu": self.init_config.cpu_request,
                            "memory": self.init_config.memory_request,
                        },
                    },
                    "securityContext": {
                        "allowPrivilegeEscalation": self.init_config.allow_privilege_escalation,
                        "readOnlyRootFilesystem": self.init_config.read_only_root_filesystem,
                        "runAsNonRoot": self.init_config.run_as_non_root,
                        "runAsUser": self.init_config.run_as_user,
                    },
                })

        # 3. Build target container volume mounts (readOnly: true)
        app_mounts = []
        seen_app_mounts = set()
        for asset in assets:
            if asset.mount_path not in seen_app_mounts:
                app_mounts.append({
                    "name": asset.effective_volume_name,
                    "mountPath": asset.mount_path,
                    "readOnly": True,
                })
                seen_app_mounts.add(asset.mount_path)

        containers = [{
            "name": target_container_name or "app",
            "volumeMounts": app_mounts,
        }]

        # 4. Construct workload structure
        pod_spec = {
            "volumes": volumes,
            "initContainers": init_containers,
            "containers": containers,
        }

        if base_workload_type == "Pod":
            return {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {
                    "name": f"{self.config.project_name}-pod",
                },
                "spec": pod_spec,
            }
        else:
            return {
                "apiVersion": "apps/v1",
                "kind": base_workload_type,
                "metadata": {
                    "name": self.config.project_name,
                },
                "spec": {
                    "template": {
                        "spec": pod_spec,
                    },
                },
            }

    def generate_init_container_patch_yaml(
        self,
        assets: List[AssetSpec],
        target_container_name: Optional[str] = "app",
        base_workload_type: str = "Deployment",
        single_init_container: bool = True,
    ) -> str:
        """Renders the Kubernetes patch as a clean YAML manifest."""
        patch_dict = self.generate_init_container_patch(
            assets=assets,
            target_container_name=target_container_name,
            base_workload_type=base_workload_type,
            single_init_container=single_init_container,
        )
        return yaml.dump(patch_dict, sort_keys=False, default_flow_style=False)

    def generate_oras_push_commands(
        self,
        assets: List[AssetSpec],
        registry_prefix: Optional[str] = None,
        plain_http: Optional[bool] = None,
        insecure: Optional[bool] = None,
    ) -> List[str]:
        """Generates ORAS CLI commands to push non-container static artifacts to an OCI registry."""
        commands = []
        use_plain_http = self.oras_config.plain_http if plain_http is None else plain_http
        use_insecure = self.oras_config.insecure if insecure is None else insecure

        flags = []
        if use_plain_http:
            flags.append("--plain-http")
        if use_insecure:
            flags.append("--insecure")
        flag_str = f" {' '.join(flags)}" if flags else ""

        prefix = registry_prefix if registry_prefix is not None else self.oras_config.registry_prefix

        for asset in assets:
            ref = asset.remote_artifact_ref
            if prefix and not ("/" in ref and ("." in ref.split("/")[0] or ":" in ref.split("/")[0])):
                ref = f"{prefix.rstrip('/')}/{ref.lstrip('/')}"

            media_type_spec = f":{asset.media_type}" if asset.media_type else ""
            commands.append(f"oras push{flag_str} {ref} {asset.source_path}{media_type_spec}")

        return commands

    def generate_oras_pull_commands(
        self,
        assets: List[AssetSpec],
        output_dir: Optional[str] = None,
        plain_http: Optional[bool] = None,
        insecure: Optional[bool] = None,
    ) -> List[str]:
        """Generates ORAS CLI commands to pull non-container static artifacts from an OCI registry."""
        commands = []
        use_plain_http = self.oras_config.plain_http if plain_http is None else plain_http
        use_insecure = self.oras_config.insecure if insecure is None else insecure

        flags = []
        if use_plain_http:
            flags.append("--plain-http")
        if use_insecure:
            flags.append("--insecure")
        flag_str = f" {' '.join(flags)}" if flags else ""

        prefix = self.oras_config.registry_prefix

        for asset in assets:
            ref = asset.remote_artifact_ref
            if prefix and not ("/" in ref and ("." in ref.split("/")[0] or ":" in ref.split("/")[0])):
                ref = f"{prefix.rstrip('/')}/{ref.lstrip('/')}"

            target = output_dir or asset.mount_path
            commands.append(f"oras pull{flag_str} {ref} -o {target}")

        return commands

    def generate_kustomize_patch_yaml(
        self,
        assets: List[AssetSpec],
        target_container_name: Optional[str] = "app",
        base_workload_type: str = "Deployment",
    ) -> str:
        """Generates a Kustomize-compatible strategic merge patch YAML."""
        return self.generate_init_container_patch_yaml(
            assets=assets,
            target_container_name=target_container_name,
            base_workload_type=base_workload_type,
        )

    def generate_decoupling_bundle(
        self,
        assets: List[AssetSpec],
        target_container_name: str = "app",
        base_workload_type: str = "Deployment",
    ) -> DecouplingReport:
        """Generates a complete decoupling package with manifests, CLI scripts, and metrics."""
        pod_patch = self.generate_init_container_patch(
            assets=assets,
            target_container_name=target_container_name,
            base_workload_type="Pod",
        )
        pod_yaml = yaml.dump(pod_patch, sort_keys=False, default_flow_style=False)

        dep_patch = self.generate_init_container_patch(
            assets=assets,
            target_container_name=target_container_name,
            base_workload_type=base_workload_type,
        )
        dep_yaml = yaml.dump(dep_patch, sort_keys=False, default_flow_style=False)

        kustomize_yaml = self.generate_kustomize_patch_yaml(
            assets=assets,
            target_container_name=target_container_name,
            base_workload_type=base_workload_type,
        )

        push_cmds = self.generate_oras_push_commands(assets)
        pull_cmds = self.generate_oras_pull_commands(assets)

        directives = []
        for asset in assets:
            directives.append(
                f"# Prune static asset '{asset.name}': Remove 'COPY {asset.source_path} {asset.mount_path}' from Dockerfile"
            )
            directives.append(
                f"# Asset will be dynamically mounted at runtime via init container volume '{asset.effective_volume_name}' at '{asset.mount_path}'"
            )

        estimated_savings = sum(a.size_mb or 0.0 for a in assets)

        return DecouplingReport(
            assets=assets,
            pod_patch=pod_patch,
            pod_patch_yaml=pod_yaml,
            deployment_patch=dep_patch,
            deployment_patch_yaml=dep_yaml,
            kustomize_patch_yaml=kustomize_yaml,
            oras_push_commands=push_cmds,
            oras_pull_commands=pull_cmds,
            dockerfile_pruning_directives=directives,
            estimated_savings_mb=estimated_savings,
        )

    def write_manifests(
        self,
        output_dir: str,
        assets: List[AssetSpec],
        target_container_name: str = "app",
    ) -> Dict[str, str]:
        """Writes Kubernetes patch manifests and executable ORAS scripts to disk."""
        os.makedirs(output_dir, exist_ok=True)
        bundle = self.generate_decoupling_bundle(assets, target_container_name=target_container_name)

        deployment_patch_path = os.path.join(output_dir, "init-container-deployment-patch.yaml")
        with open(deployment_patch_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(bundle.deployment_patch_yaml)

        pod_patch_path = os.path.join(output_dir, "init-container-pod-patch.yaml")
        with open(pod_patch_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(bundle.pod_patch_yaml)

        push_script_path = os.path.join(output_dir, "oras-push.sh")
        with open(push_script_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("#!/bin/sh\nset -e\n\n" + "\n".join(bundle.oras_push_commands) + "\n")

        pull_script_path = os.path.join(output_dir, "oras-pull.sh")
        with open(pull_script_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("#!/bin/sh\nset -e\n\n" + "\n".join(bundle.oras_pull_commands) + "\n")

        return {
            "deployment_patch": deployment_patch_path,
            "pod_patch": pod_patch_path,
            "oras_push_script": push_script_path,
            "oras_pull_script": pull_script_path,
        }
