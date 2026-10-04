import os
import json
import tempfile
import pytest
from rover_slim.languages.node_adapter import NodeLanguageAdapter
from rover_slim.languages.registry import LanguageRegistry
from rover_slim.models import RoverSlimConfig

def test_node_adapter_detection():
    adapter = NodeLanguageAdapter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty dir
        assert adapter.detect(tmpdir) is False

        # Create package.json
        pkg_json = os.path.join(tmpdir, "package.json")
        with open(pkg_json, "w") as f:
            json.dump({
                "name": "my-express-api",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.2",
                    "cors": "^2.8.5"
                },
                "devDependencies": {
                    "jest": "^29.6.0",
                    "eslint": "^8.45.0",
                    "typescript": "^5.1.6"
                }
            }, f)

        assert adapter.detect(tmpdir) is True
        assert adapter.name == "nodejs"
        assert adapter.display_name == "Node.js / TypeScript"

def test_node_adapter_dependency_segregation():
    adapter = NodeLanguageAdapter()

    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_json = os.path.join(tmpdir, "package.json")
        with open(pkg_json, "w") as f:
            json.dump({
                "dependencies": {
                    "express": "^4.18.2",
                    "pg": "^8.11.0",
                    "webpack": "^5.88.0"  # matches dev pattern in prod
                },
                "devDependencies": {
                    "jest": "^29.6.0",
                    "prettier": "^3.0.0",
                    "@types/node": "^20.4.0"
                }
            }, f)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_names = [p.name for p in prod]
        dev_names = [d.name for d in dev]

        assert "express" in prod_names
        assert "pg" in prod_names
        assert "webpack" in dev_names  # Pruned from prod
        assert "jest" in dev_names
        assert "prettier" in dev_names
        assert "@types/node" in dev_names
        assert len(pruned) >= 4

def test_node_adapter_dockerfile_synthesis_and_probes():
    adapter = NodeLanguageAdapter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # App file with route and port
        server_code = """
const express = require('express');
const app = express();

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(8080, () => console.log('Listening on 8080'));
"""
        with open(os.path.join(tmpdir, "server.js"), "w") as f:
            f.write(server_code)

        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)
        
        assert "FROM node:20-slim AS builder" in df
        assert "FROM node:20-slim AS runtime" in df
        assert "npm prune --omit=dev" in df
        assert "USER 10001" in df

        probes = adapter.discover_health_probes(tmpdir)
        assert len(probes) == 1
        assert probes[0].path == "/health"
        assert probes[0].port == 8080

def test_registry_detects_node():
    registry = LanguageRegistry()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "package.json"), "w") as f:
            f.write('{"name":"test-node"}')
            
        adapter = registry.detect_language(tmpdir)
        assert adapter.name == "nodejs"
