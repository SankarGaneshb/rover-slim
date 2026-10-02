import os
import tempfile
import json
from rover_slim.auditors.sbom_generator import SBOMGenerator
from rover_slim.parsers.req_parser import RequirementEntry

def test_sbom_generator_spdx_and_cyclonedx():
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = SBOMGenerator("test-service")
        entries = [
            RequirementEntry("fastapi>=0.100.0", "fastapi", ">=0.100.0"),
            RequirementEntry("pydantic==2.0.0", "pydantic", "==2.0.0")
        ]

        paths = generator.write_sboms(entries, output_dir=tmpdir)
        assert os.path.exists(paths["spdx"])
        assert os.path.exists(paths["cyclonedx"])

        # Validate SPDX JSON format
        with open(paths["spdx"], "r", encoding="utf-8") as f:
            spdx_data = json.load(f)
            assert spdx_data["spdxVersion"] == "SPDX-2.3"
            assert len(spdx_data["packages"]) == 3  # Root + 2 packages
            assert any(p["name"] == "fastapi" for p in spdx_data["packages"])

        # Validate CycloneDX JSON format
        with open(paths["cyclonedx"], "r", encoding="utf-8") as f:
            cyclone_data = json.load(f)
            assert cyclone_data["bomFormat"] == "CycloneDX"
            assert len(cyclone_data["components"]) == 2
