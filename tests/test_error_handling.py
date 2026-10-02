import os
import tempfile
import pytest
from typer.testing import CliRunner
from rover_slim.cli import app
from rover_slim.config import load_config
from rover_slim.parsers.req_parser import RequirementsParser
from rover_slim.parsers.ast_parser import ASTDependencyParser

runner = CliRunner()

def test_cli_handles_non_existent_path():
    res = runner.invoke(app, ["audit", "invalid/non/existent/path/xyz"])
    assert res.exit_code != 0
    assert "does not exist" in res.stdout

def test_cli_optimize_handles_non_existent_path():
    res = runner.invoke(app, ["optimize", "invalid/path"])
    assert res.exit_code != 0
    assert "does not exist" in res.stdout

def test_cli_diff_handles_non_existent_path():
    res = runner.invoke(app, ["diff", "invalid/path"])
    assert res.exit_code != 0
    assert "does not exist" in res.stdout

def test_cli_verify_handles_non_existent_path():
    res = runner.invoke(app, ["verify", "invalid/path"])
    assert res.exit_code != 0
    assert "does not exist" in res.stdout

def test_config_handles_corrupt_yaml():
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_yaml = os.path.join(tmpdir, "corrupt.yaml")
        with open(bad_yaml, "w", encoding="utf-8") as f:
            f.write("version: [unclosed list\n  bad: {:\n")
        
        cfg = load_config(bad_yaml)
        assert cfg is not None
        assert cfg.version == "1.0"

def test_config_handles_non_dict_yaml():
    with tempfile.TemporaryDirectory() as tmpdir:
        scalar_yaml = os.path.join(tmpdir, "scalar.yaml")
        with open(scalar_yaml, "w", encoding="utf-8") as f:
            f.write("just a string scalar\n")
        
        cfg = load_config(scalar_yaml)
        assert cfg is not None
        assert cfg.version == "1.0"

def test_req_parser_handles_comments_and_editable():
    parser = RequirementsParser(".")
    
    # Inline comment
    r1 = parser.parse_requirement_line("fastapi>=0.100.0 # primary api framework")
    assert r1 is not None
    assert r1.name == "fastapi"

    # Environment marker
    r2 = parser.parse_requirement_line("importlib-metadata>=4.0; python_version < '3.8'")
    assert r2 is not None
    assert r2.name == "importlib-metadata"

    # Editable with egg fragment
    r3 = parser.parse_requirement_line("-e git+https://github.com/org/repo.git#egg=custom-lib")
    assert r3 is not None
    assert r3.name == "custom-lib"

    # Option flag to ignore
    r4 = parser.parse_requirement_line("--extra-index-url https://custom.pypi.org")
    assert r4 is None

def test_ast_parser_handles_corrupt_python_syntax():
    with tempfile.TemporaryDirectory() as tmpdir:
        broken_file = os.path.join(tmpdir, "broken.py")
        with open(broken_file, "w", encoding="utf-8") as f:
            f.write("def broken_syntax(:\n    import fastapi\n")
        
        parser = ASTDependencyParser(tmpdir)
        # Should gracefully return empty set without crashing
        imports = parser.extract_imports_from_file(broken_file)
        assert isinstance(imports, set)

def test_ast_parser_handles_latin1_encoding():
    with tempfile.TemporaryDirectory() as tmpdir:
        latin1_file = os.path.join(tmpdir, "latin1.py")
        # Write bytes invalid in UTF-8
        with open(latin1_file, "wb") as f:
            f.write(b"# Author: Ren\xe9\nimport requests\n")
        
        parser = ASTDependencyParser(tmpdir)
        imports = parser.extract_imports_from_file(latin1_file)
        assert "requests" in imports
