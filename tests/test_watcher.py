import os
import tempfile
from rover_slim.core.watcher import ProjectWatcher

def test_project_watcher_tracks_and_syncs():
    with tempfile.TemporaryDirectory() as tmpdir:
        req_file = os.path.join(tmpdir, "requirements.txt")
        app_file = os.path.join(tmpdir, "app.py")
        
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("fastapi==0.100.0\npytest==7.4.0\n")
        with open(app_file, "w", encoding="utf-8") as f:
            f.write("import fastapi\n")

        watcher = ProjectWatcher(root_dir=tmpdir)
        tracked = watcher._get_tracked_files()

        assert any("requirements.txt" in p for p in tracked)
        assert any("app.py" in p for p in tracked)

        # Test single sync
        synced = watcher.sync_once()
        assert synced is True
        assert os.path.exists(os.path.join(tmpdir, "requirements-prod.txt"))
