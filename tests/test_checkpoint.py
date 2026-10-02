import os
import tempfile
from rover_slim.core.checkpoint import CheckpointSentinel

def test_checkpoint_creation_and_restore():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an initial file
        req_file = os.path.join(tmpdir, "requirements.txt")
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("fastapi==0.100.0\n")

        sentinel = CheckpointSentinel(tmpdir)
        chk_id = sentinel.create_checkpoint("test_backup")

        assert chk_id == "test_backup"
        checkpoints = sentinel.list_checkpoints()
        assert len(checkpoints) == 1

        # Overwrite file with bad content
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("corrupted_state\n")

        # Restore checkpoint
        success = sentinel.restore_checkpoint(chk_id)
        assert success is True

        with open(req_file, "r", encoding="utf-8") as f:
            restored_content = f.read()
            assert restored_content == "fastapi==0.100.0\n"
