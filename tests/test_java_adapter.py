import os
import tempfile
import pytest
from rover_slim.languages.java_adapter import JavaLanguageAdapter
from rover_slim.languages.registry import LanguageRegistry
from rover_slim.models import RoverSlimConfig

SAMPLE_POM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.enterprise.service</groupId>
    <artifactId>auth-service</artifactId>
    <version>1.0.0</version>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>3.2.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
            <version>3.2.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <version>3.2.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
"""

SAMPLE_GRADLE = """
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
}
"""

def test_java_adapter_detection():
    adapter = JavaLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        assert adapter.detect(tmpdir) is False

        # Maven indicator
        pom = os.path.join(tmpdir, "pom.xml")
        with open(pom, "w", encoding="utf-8") as f:
            f.write(SAMPLE_POM_XML)
        assert adapter.detect(tmpdir) is True
        assert adapter.name == "java"
        assert adapter.display_name == "Java / Spring Boot"

def test_java_adapter_maven_dependency_segregation():
    adapter = JavaLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        pom = os.path.join(tmpdir, "pom.xml")
        with open(pom, "w", encoding="utf-8") as f:
            f.write(SAMPLE_POM_XML)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_str = " ".join(str(p) for p in prod)
        dev_str = " ".join(str(d) for d in dev)
        pruned_names = [p.package for p in pruned]

        assert "spring-boot-starter-web" in prod_str
        assert "spring-boot-starter-actuator" in prod_str
        assert "spring-boot-starter-test" in dev_str
        assert "junit-jupiter" in dev_str
        assert "spring-boot-starter-test" in pruned_names
        assert "junit-jupiter" in pruned_names
        assert len(pruned) >= 2

def test_java_adapter_gradle_dependency_segregation():
    adapter = JavaLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        gradle = os.path.join(tmpdir, "build.gradle")
        with open(gradle, "w", encoding="utf-8") as f:
            f.write(SAMPLE_GRADLE)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_str = " ".join(str(p) for p in prod)
        dev_str = " ".join(str(d) for d in dev)

        assert "spring-boot-starter-web" in prod_str
        assert "spring-boot-starter-test" in dev_str
        assert len(pruned) >= 2

def test_java_dockerfile_synthesis_and_layertools():
    adapter = JavaLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create pom.xml and application.properties
        with open(os.path.join(tmpdir, "pom.xml"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_POM_XML)
        with open(os.path.join(tmpdir, "application.properties"), "w", encoding="utf-8") as f:
            f.write("server.port=9090\nspring.application.name=auth-service\n")

        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)

        assert "FROM eclipse-temurin:17-jdk-alpine AS builder" in df
        assert "FROM eclipse-temurin:17-jre-alpine AS extractor" in df
        assert "FROM eclipse-temurin:17-jre-alpine AS runtime" in df
        assert "layertools" in df
        assert "USER 10001:10001" in df
        assert "EXPOSE 8080" in df

        probes = adapter.discover_health_probes(tmpdir)
        assert len(probes) == 1
        assert probes[0].port == 9090
        assert probes[0].path == "/actuator/health"

def test_registry_detects_java():
    registry = LanguageRegistry()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "pom.xml"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_POM_XML)

        detected = registry.detect_language(tmpdir)
        assert detected.name == "java"
        assert detected.display_name == "Java / Spring Boot"

def test_rover_slim_engine_java_e2e_pilot():
    from rover_slim.core.engine import RoverSlimEngine
    with tempfile.TemporaryDirectory() as tmpdir:
        pom = os.path.join(tmpdir, "pom.xml")
        with open(pom, "w", encoding="utf-8") as f:
            f.write(SAMPLE_POM_XML)
        
        engine = RoverSlimEngine(root_dir=tmpdir)
        audit_report = engine.audit()
        assert audit_report.status == "PASSED"
        assert audit_report.baseline.uncompressed_size_mb > audit_report.optimized.uncompressed_size_mb
        assert len(audit_report.pruned_dependencies) >= 2

        opt_report = engine.optimize(verify_goa=True)
        assert opt_report.status == "PASSED"
        assert os.path.exists(os.path.join(tmpdir, "Dockerfile"))
        assert os.path.exists(os.path.join(tmpdir, ".dockerignore"))
        assert os.path.exists(os.path.join(tmpdir, ".rover-slim", "summary.md"))
        assert os.path.exists(os.path.join(tmpdir, ".rover-slim", "sbom.spdx.json"))
        
        with open(os.path.join(tmpdir, "Dockerfile"), "r", encoding="utf-8") as f:
            content = f.read()
            assert "layertools" in content
            assert "USER 10001:10001" in content

