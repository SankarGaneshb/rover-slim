from rover_slim.parsers.transitive_resolver import TransitiveDependencyResolver

def test_transitive_expansion_for_fastapi():
    resolver = TransitiveDependencyResolver()
    expanded = resolver.expand_production_packages({"fastapi"})

    assert "fastapi" in expanded
    assert "starlette" in expanded
    assert "pydantic" in expanded

def test_transitive_expansion_for_pandas():
    resolver = TransitiveDependencyResolver()
    expanded = resolver.expand_production_packages({"pandas"})

    assert "pandas" in expanded
    assert "numpy" in expanded
    assert "python-dateutil" in expanded
