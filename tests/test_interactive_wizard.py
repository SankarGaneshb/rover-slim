from rover_slim.parsers.interactive_wizard import InteractiveWizard
from rover_slim.parsers.req_parser import RequirementEntry
from rover_slim.models import PrunedPackage

def test_interactive_wizard_no_override(monkeypatch):
    wizard = InteractiveWizard()
    # Mock user input to 'none'
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: "none")

    prod = [RequirementEntry("fastapi==0.100.0", "fastapi")]
    dev = [RequirementEntry("pytest==7.4.0", "pytest")]
    pruned = [PrunedPackage(package="pytest==7.4.0", action="MOVED_TO_DEV", reason="Dev", estimated_size_mb=20.0)]

    r_prod, r_dev, r_pruned = wizard.review_segregation(prod, dev, pruned)
    assert len(r_prod) == 1
    assert len(r_dev) == 1
    assert r_prod[0].name == "fastapi"

def test_interactive_wizard_with_override(monkeypatch):
    wizard = InteractiveWizard()
    # User moves pytest to prod
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: "pytest")

    prod = [RequirementEntry("fastapi==0.100.0", "fastapi")]
    dev = [RequirementEntry("pytest==7.4.0", "pytest")]
    pruned = [PrunedPackage(package="pytest==7.4.0", action="MOVED_TO_DEV", reason="Dev", estimated_size_mb=20.0)]

    r_prod, r_dev, r_pruned = wizard.review_segregation(prod, dev, pruned)
    assert len(r_prod) == 2
    assert len(r_dev) == 0
    assert any(p.name == "pytest" for p in r_prod)
