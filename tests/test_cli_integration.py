from typer.testing import CliRunner
from rover_slim.cli import app
import tempfile
import os

runner = CliRunner()

def test_cli_init_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = runner.invoke(app, ["init", tmpdir])
        assert res.exit_code == 0
        assert os.path.exists(os.path.join(tmpdir, ".rover-slim.yaml"))

def test_cli_audit_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = runner.invoke(app, ["audit", tmpdir])
        assert res.exit_code == 0
        assert "ROVER-SLIM OPTIMIZATION REPORT" in res.stdout

def test_cli_optimize_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock server.py and requirements.txt
        with open(os.path.join(tmpdir, "server.py"), "w") as f:
            f.write("import requests\n")
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("requests==2.31.0\npytest==7.4.0\n")

        res = runner.invoke(app, ["optimize", tmpdir])
        assert res.exit_code == 0
        assert os.path.exists(os.path.join(tmpdir, "requirements-prod.txt"))
        assert os.path.exists(os.path.join(tmpdir, "requirements-dev.txt"))
        assert os.path.exists(os.path.join(tmpdir, ".dockerignore"))
        assert os.path.exists(os.path.join(tmpdir, "Dockerfile"))
        assert os.path.exists(os.path.join(tmpdir, ".rover-slim", "report.json"))
        assert os.path.exists(os.path.join(tmpdir, ".rover-slim", "report.html"))

def test_cli_optimize_project_name_from_target_dir():
    with tempfile.TemporaryDirectory() as base_tmp:
        election_dir = os.path.join(base_tmp, "electionRover")
        os.makedirs(election_dir, exist_ok=True)
        with open(os.path.join(election_dir, "server.py"), "w") as f:
            f.write("import requests\n")
        with open(os.path.join(election_dir, "requirements.txt"), "w") as f:
            f.write("requests==2.31.0\npytest==7.4.0\n")

        res = runner.invoke(app, ["optimize", election_dir])
        assert res.exit_code == 0
        assert "ROVER-SLIM OPTIMIZATION REPORT: ELECTIONROVER" in res.stdout

