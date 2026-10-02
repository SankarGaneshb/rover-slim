import os
import shutil
import time
from typing import List, Optional, Dict, Any

TRACKED_FILES = [
    "Dockerfile",
    ".dockerignore",
    "requirements.txt",
    "requirements-prod.txt",
    "requirements-dev.txt",
    ".rover-slim.yaml"
]

class CheckpointSentinel:
    """Manages atomic file snapshots and automatic rollbacks upon GoA verification failure."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.backup_root = os.path.join(self.root_dir, ".rover-slim", "backups")

    def create_checkpoint(self, tag: Optional[str] = None) -> str:
        """Saves current state of tracked files to a timestamped backup directory."""
        checkpoint_id = tag or time.strftime("checkpoint_%Y%m%d_%H%M%S", time.gmtime())
        checkpoint_dir = os.path.join(self.backup_root, checkpoint_id)
        os.makedirs(checkpoint_dir, exist_ok=True)

        saved_count = 0
        for fname in TRACKED_FILES:
            src = os.path.join(self.root_dir, fname)
            if os.path.exists(src):
                dst = os.path.join(checkpoint_dir, fname)
                shutil.copy2(src, dst)
                saved_count += 1

        metadata_file = os.path.join(checkpoint_dir, "metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(f'{{"checkpoint_id": "{checkpoint_id}", "timestamp": "{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}", "files_saved": {saved_count}}}')

        # Retention pruning: retain at most 10 latest checkpoints
        self._prune_checkpoints(max_retain=10)

        return checkpoint_id

    def _prune_checkpoints(self, max_retain: int = 10):
        """Retains at most max_retain latest checkpoints and deletes older ones."""
        try:
            checkpoints = self.list_checkpoints()
            if len(checkpoints) > max_retain:
                for old in checkpoints[max_retain:]:
                    if os.path.exists(old["path"]):
                        shutil.rmtree(old["path"], ignore_errors=True)
        except Exception:
            pass

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Lists all existing checkpoints sorted by newest first."""
        if not os.path.exists(self.backup_root):
            return []
        checkpoints = []
        for name in os.listdir(self.backup_root):
            p = os.path.join(self.backup_root, name)
            if os.path.isdir(p):
                checkpoints.append({
                    "id": name,
                    "path": p,
                    "created_at": time.ctime(os.path.getmtime(p))
                })
        checkpoints.sort(key=lambda x: x["id"], reverse=True)
        return checkpoints

    def restore_checkpoint(self, checkpoint_id: Optional[str] = None) -> bool:
        """Restores tracked files from the specified or latest checkpoint."""
        if not os.path.exists(self.backup_root):
            return False

        if not checkpoint_id:
            checkpoints = self.list_checkpoints()
            if not checkpoints:
                return False
            checkpoint_dir = checkpoints[0]["path"]
        else:
            checkpoint_dir = os.path.join(self.backup_root, checkpoint_id)

        if not os.path.exists(checkpoint_dir):
            return False

        for fname in TRACKED_FILES:
            backup_file = os.path.join(checkpoint_dir, fname)
            target_file = os.path.join(self.root_dir, fname)
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, target_file)

        return True
