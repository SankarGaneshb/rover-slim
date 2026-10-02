import os
import sys
import yaml
from typing import Optional
from rover_slim.models import RoverSlimConfig

def load_config(config_path: Optional[str] = None, root_dir: Optional[str] = None) -> RoverSlimConfig:
    """Loads configuration from YAML file with robust error handling and fallback."""
    base_dir = os.path.abspath(root_dir) if root_dir else os.getcwd()
    fallback_name = os.path.basename(base_dir) or "rover-slim-project"

    if config_path:
        target_path = config_path if os.path.isabs(config_path) else os.path.join(base_dir, config_path)
    else:
        default_yaml = os.path.join(base_dir, ".rover-slim.yaml")
        default_yml = os.path.join(base_dir, ".rover-slim.yml")
        if os.path.exists(default_yaml):
            target_path = default_yaml
        elif os.path.exists(default_yml):
            target_path = default_yml
        else:
            target_path = default_yaml

    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    if not data.get("project_name") or data.get("project_name") in ("default-project", "my-service"):
                        data["project_name"] = fallback_name
                    return RoverSlimConfig(**data)
                else:
                    sys.stderr.write(f"[WARN] Config at {target_path} is not a valid YAML mapping. Using defaults.\n")
        except yaml.YAMLError as ye:
            sys.stderr.write(f"[WARN] Failed to parse YAML config at {target_path}: {ye}. Using defaults.\n")
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to load config at {target_path}: {e}. Using defaults.\n")

    return RoverSlimConfig(project_name=fallback_name)
