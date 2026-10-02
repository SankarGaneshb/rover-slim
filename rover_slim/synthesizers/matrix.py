from typing import List, Dict, Any, Set
from rover_slim.parsers.ast_parser import ASTDependencyParser

# Packages with known difficult C-extensions or glibc requirements on Linux
GLIBC_RECOMMENDED_PACKAGES: Set[str] = {
    "torch", "torchvision", "torchaudio", "tensorflow", "grpcio", "scipy",
    "numpy", "pandas", "pyarrow", "duckdb", "polars", "psycopg2",
    "opencv-python", "pillow", "cryptography", "uvloop", "asyncpg"
}

class BaseImageRecommender:
    """Evaluates project dependencies and recommends the leanest, most secure Docker base image."""

    def __init__(self, detected_packages: List[str]):
        self.packages = {p.lower().replace("_", "-") for p in detected_packages}

    def recommend(self, python_version: str = "3.11") -> Dict[str, Any]:
        has_heavy_binary = any(p in self.packages for p in GLIBC_RECOMMENDED_PACKAGES)

        if has_heavy_binary:
            recommended_base = f"python:{python_version}-slim"
            distro = "Debian Slim (glibc)"
            rationale = (
                "Detected binary C-extensions/scientific wheels (e.g. numpy, pandas, cryptography). "
                "Debian slim provides pre-compiled glibc manylinux wheels without compiling from source."
            )
            estimated_base_mb = 145.0
        else:
            recommended_base = f"python:{python_version}-alpine"
            distro = "Alpine Linux (musl)"
            rationale = (
                "Pure Python or lightweight dependencies detected. "
                "Alpine Linux provides the ultra-leanest footprint (<65 MB uncompressed)."
            )
            estimated_base_mb = 65.0

        return {
            "recommended_base_image": recommended_base,
            "distribution": distro,
            "estimated_base_size_mb": estimated_base_mb,
            "rationale": rationale,
            "requires_glibc": has_heavy_binary,
            "supported_architectures": ["linux/amd64", "linux/arm64"]
        }
