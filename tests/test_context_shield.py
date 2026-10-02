import os
import tempfile
from rover_slim.parsers.context_shield import ContextShield

def test_context_shield_detects_git_and_venv():
    with tempfile.TemporaryDirectory() as tmpdir:
        git_dir = os.path.join(tmpdir, ".git")
        venv_dir = os.path.join(tmpdir, "venv")
        os.makedirs(git_dir)
        os.makedirs(venv_dir)

        with open(os.path.join(git_dir, "config"), "w") as f:
            f.write("git data " * 1000)

        with open(os.path.join(venv_dir, "lib.py"), "w") as f:
            f.write("venv data " * 1000)

        shield = ContextShield(tmpdir)
        audit = shield.audit_context_leakage()

        assert audit["has_dockerignore"] is False
        assert ".git" in audit["leaked_directories"]
        assert "venv" in audit["leaked_directories"]

        # Test writing .dockerignore
        ignore_path, created = shield.write_dockerignore()
        assert os.path.exists(ignore_path)
        assert created is True

        with open(ignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert ".git" in content
            assert "node_modules/" in content
            assert "venv/" in content
