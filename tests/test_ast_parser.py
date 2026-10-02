import os
import tempfile
from rover_slim.parsers.ast_parser import ASTDependencyParser

def test_ast_parser_extracts_imports():
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = os.path.join(tmpdir, "main.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write("""
import os
import sys
import fastapi
import uvicorn
from pydantic import BaseModel
from typing import List
import requests
import yaml
""")
        parser = ASTDependencyParser(tmpdir)
        imports = parser.extract_imports_from_file(code_file)
        
        # Standard library (os, sys, typing) should be filtered out
        assert "os" not in imports
        assert "sys" not in imports
        assert "typing" not in imports

        # Third-party packages should be captured
        assert "fastapi" in imports
        assert "uvicorn" in imports
        assert "pydantic" in imports
        assert "requests" in imports
        assert "yaml" in imports

def test_ast_scan_excludes_tests_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "app")
        test_dir = os.path.join(tmpdir, "tests")
        os.makedirs(src_dir)
        os.makedirs(test_dir)

        with open(os.path.join(src_dir, "server.py"), "w", encoding="utf-8") as f:
            f.write("import fastapi\nimport redis\n")

        with open(os.path.join(test_dir, "test_server.py"), "w", encoding="utf-8") as f:
            f.write("import pytest\nimport mock\nimport matplotlib.pyplot as plt\n")

        parser = ASTDependencyParser(tmpdir)
        prod_imports = parser.scan_production_imports()

        assert "fastapi" in prod_imports
        assert "redis" in prod_imports
        assert "pytest" not in prod_imports
        assert "mock" not in prod_imports
        assert "matplotlib" not in prod_imports
