import os
import tempfile
from rover_slim.parsers.req_parser import RequirementsParser, RequirementEntry

def test_requirements_segregation():
    with tempfile.TemporaryDirectory() as tmpdir:
        req_file = os.path.join(tmpdir, "requirements.txt")
        with open(req_file, "w", encoding="utf-8") as f:
            f.write("""
fastapi>=0.100.0
uvicorn[standard]==0.23.2
pytest>=7.4.0
pytest-cov==4.1.0
black==23.7.0
streamlit>=1.25.0
pydantic>=2.0.0
unused-package==1.0.0
""")

        # App code importing fastapi, uvicorn, pydantic
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "app.py"), "w", encoding="utf-8") as f:
            f.write("""
import fastapi
import uvicorn
from pydantic import BaseModel
""")

        parser = RequirementsParser(tmpdir)
        prod, dev, pruned = parser.segregate_dependencies()

        prod_names = [p.normalized_name for p in prod]
        dev_names = [d.normalized_name for d in dev]

        # Production should only have genuinely used runtime libs
        assert "fastapi" in prod_names
        assert "uvicorn" in prod_names
        assert "pydantic" in prod_names

        # Dev / unreferenced should be moved to dev
        assert "pytest" in dev_names
        assert "pytest-cov" in dev_names
        assert "black" in dev_names
        assert "streamlit" in dev_names
        assert "unused-package" in dev_names

        assert len(pruned) >= 5
