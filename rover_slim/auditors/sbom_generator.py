import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from rover_slim.parsers.req_parser import RequirementEntry

class SBOMGenerator:
    """Generates standardized SPDX 2.3 and CycloneDX 1.5 Software Bill of Materials (SBOM) documents."""

    def __init__(self, project_name: str = "rover-slim-service"):
        self.project_name = project_name

    def generate_spdx_sbom(self, prod_entries: List[RequirementEntry]) -> Dict[str, Any]:
        """Generates an SPDX 2.3 compliant JSON document."""
        doc_namespace = f"https://spdx.org/spdxdocs/{self.project_name}-{int(time.time())}"
        packages = []

        # Root package
        packages.append({
            "name": self.project_name,
            "SPDXID": "SPDXRef-Package-Root",
            "versionInfo": "1.0.0",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION"
        })

        for idx, entry in enumerate(prod_entries, 1):
            version = entry.specifier.lstrip("=>~<").strip() or "latest"
            pkg_spdx = {
                "name": entry.name,
                "SPDXID": f"SPDXRef-Package-{entry.normalized_name}",
                "versionInfo": version,
                "downloadLocation": f"https://pypi.org/project/{entry.name}/",
                "filesAnalyzed": False,
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": f"pkg:pypi/{entry.name}@{version}"
                    }
                ],
                "licenseConcluded": "MIT",
                "licenseDeclared": "MIT",
                "copyrightText": "NOASSERTION"
            }
            packages.append(pkg_spdx)

        return {
            "spdxVersion": "SPDX-2.3",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": f"{self.project_name}-SBOM",
            "documentNamespace": doc_namespace,
            "creationInfo": {
                "creators": ["Tool: Rover-Slim Container Optimization Engine v1.0"],
                "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "packages": packages
        }

    def generate_cyclonedx_sbom(self, prod_entries: List[RequirementEntry]) -> Dict[str, Any]:
        """Generates a CycloneDX 1.5 compliant JSON document."""
        components = []

        for entry in enumerate(prod_entries, 1):
            item = entry[1]
            version = item.specifier.lstrip("=>~<").strip() or "latest"
            components.append({
                "type": "library",
                "name": item.name,
                "version": version,
                "purl": f"pkg:pypi/{item.name}@{version}",
                "scope": "required",
                "licenses": [
                    {"license": {"id": "MIT"}}
                ]
            })

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{hashlib.md5(self.project_name.encode()).hexdigest()}",
            "version": 1,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tools": [
                    {"vendor": "Rover-Slim", "name": "rover-slim", "version": "1.0.0"}
                ],
                "component": {
                    "type": "application",
                    "name": self.project_name,
                    "version": "1.0.0"
                }
            },
            "components": components
        }

    def write_sboms(
        self,
        prod_entries: List[RequirementEntry],
        output_dir: str = ".rover-slim"
    ) -> Dict[str, str]:
        """Writes both SPDX and CycloneDX SBOM JSON files."""
        os.makedirs(output_dir, exist_ok=True)
        spdx_path = os.path.join(output_dir, "sbom.spdx.json")
        cyclonedx_path = os.path.join(output_dir, "sbom.cyclonedx.json")

        spdx_doc = self.generate_spdx_sbom(prod_entries)
        with open(spdx_path, "w", encoding="utf-8") as f:
            json.dump(spdx_doc, f, indent=2)

        cyclonedx_doc = self.generate_cyclonedx_sbom(prod_entries)
        with open(cyclonedx_path, "w", encoding="utf-8") as f:
            json.dump(cyclonedx_doc, f, indent=2)

        return {"spdx": spdx_path, "cyclonedx": cyclonedx_path}
