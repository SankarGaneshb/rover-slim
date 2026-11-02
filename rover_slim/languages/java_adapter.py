import os
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Any
from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig

class JavaLanguageAdapter(BaseLanguageAdapter):
    """
    Language adapter for Java / Spring Boot enterprise ecosystems.
    Supports Maven (pom.xml) and Gradle (build.gradle/kts) dependency extraction,
    multi-stage Spring Boot Dockerfile synthesis with Layertools, and Actuator health probes.
    """

    DEV_TEST_ARTIFACTS = {
        "junit",
        "junit-jupiter",
        "junit-jupiter-api",
        "junit-jupiter-engine",
        "mockito-core",
        "mockito-junit-jupiter",
        "spring-boot-starter-test",
        "assertj-core",
        "hamcrest",
        "json-path",
        "h2",
        "byte-buddy-agent",
        "jacoco",
        "wiremock",
        "testcontainers"
    }

    @property
    def name(self) -> str:
        return "java"

    @property
    def display_name(self) -> str:
        return "Java / Spring Boot"

    def detect(self, root_dir: str) -> bool:
        """Detects presence of Maven pom.xml, Gradle build files, or Java sources."""
        root = os.path.abspath(root_dir)
        indicators = [
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "mvnw",
            "gradlew",
            "src/main/java"
        ]
        for ind in indicators:
            if os.path.exists(os.path.join(root, ind)):
                return True
        return False

    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[Any], List[Any], List[PrunedPackage]]:
        """Parses pom.xml or build.gradle to segregate compile vs. test dependencies."""
        root = os.path.abspath(root_dir)
        always_prod_set = set(always_prod or [])
        always_dev_set = set(always_dev or [])

        prod_dependencies = []
        dev_dependencies = []
        pruned_packages: List[PrunedPackage] = []

        pom_path = os.path.join(root, "pom.xml")
        gradle_path = os.path.join(root, "build.gradle")
        gradle_kts_path = os.path.join(root, "build.gradle.kts")

        if os.path.exists(pom_path):
            prod_dependencies, dev_dependencies, pruned_packages = self._parse_pom(
                pom_path, always_prod_set, always_dev_set
            )
        elif os.path.exists(gradle_path) or os.path.exists(gradle_kts_path):
            path = gradle_path if os.path.exists(gradle_path) else gradle_kts_path
            prod_dependencies, dev_dependencies, pruned_packages = self._parse_gradle(
                path, always_prod_set, always_dev_set
            )
        else:
            # Fallback default Spring Boot stack
            prod_dependencies = ["org.springframework.boot:spring-boot-starter-web"]
            dev_dependencies = ["org.springframework.boot:spring-boot-starter-test"]
            pruned_packages = [
                PrunedPackage(
                    package="spring-boot-starter-test",
                    action="EXCLUDED",
                    reason="Spring Boot test starter omitted from production runtime.",
                    estimated_size_mb=48.5
                )
            ]

        return prod_dependencies, dev_dependencies, pruned_packages

    def _parse_pom(
        self,
        pom_path: str,
        always_prod: set,
        always_dev: set
    ) -> Tuple[List[Any], List[Any], List[PrunedPackage]]:
        prod = []
        dev = []
        pruned = []

        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            # Handle XML namespaces
            ns = ""
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"

            for dep in root.findall(f".//{ns}dependencies/{ns}dependency"):
                group_elem = dep.find(f"{ns}groupId")
                artifact_elem = dep.find(f"{ns}artifactId")
                version_elem = dep.find(f"{ns}version")
                scope_elem = dep.find(f"{ns}scope")

                artifact = artifact_elem.text.strip() if artifact_elem is not None and artifact_elem.text else "unknown"
                group = group_elem.text.strip() if group_elem is not None and group_elem.text else "unknown"
                version = version_elem.text.strip() if version_elem is not None and version_elem.text else "latest"
                scope = scope_elem.text.strip().lower() if scope_elem is not None and scope_elem.text else "compile"

                coord = f"{group}:{artifact}:{version}"

                is_test = (
                    scope == "test"
                    or artifact in self.DEV_TEST_ARTIFACTS
                    or artifact in always_dev
                )
                if artifact in always_prod:
                    is_test = False

                if is_test:
                    dev.append(coord)
                    pruned.append(
                        PrunedPackage(
                            package=artifact,
                            action="EXCLUDED",
                            reason=f"Test-scoped Maven dependency ({scope}) pruned from runtime.",
                            estimated_size_mb=25.0
                        )
                    )
                else:
                    prod.append(coord)
        except Exception:
            prod = ["org.springframework.boot:spring-boot-starter-web"]
            dev = ["org.springframework.boot:spring-boot-starter-test"]
            pruned = [
                PrunedPackage(
                    package="spring-boot-starter-test",
                    action="EXCLUDED",
                    reason="Test starter omitted from production runtime.",
                    estimated_size_mb=48.5
                )
            ]

        return prod, dev, pruned

    def _parse_gradle(
        self,
        gradle_path: str,
        always_prod: set,
        always_dev: set
    ) -> Tuple[List[Any], List[Any], List[PrunedPackage]]:
        prod = []
        dev = []
        pruned = []

        try:
            with open(gradle_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Match dependencies e.g. testImplementation 'org.junit:junit:5.9' or implementation(...)
            dep_pattern = re.compile(r"""(implementation|testImplementation|testRuntimeOnly|compileOnly)\s*\(?['"]([^'"]+)['"]\)?""")
            for match in dep_pattern.finditer(content):
                scope, coord = match.group(1), match.group(2)
                artifact = coord.split(":")[1] if ":" in coord else coord

                is_test = (
                    "test" in scope.lower()
                    or artifact in self.DEV_TEST_ARTIFACTS
                    or artifact in always_dev
                )
                if artifact in always_prod:
                    is_test = False

                if is_test:
                    dev.append(coord)
                    pruned.append(
                        PrunedPackage(
                            package=artifact,
                            action="EXCLUDED",
                            reason=f"Test-scoped Gradle dependency ({scope}) pruned from runtime.",
                            estimated_size_mb=25.0
                        )
                    )
                else:
                    prod.append(coord)
        except Exception:
            prod = ["org.springframework.boot:spring-boot-starter-web"]

        return prod, dev, pruned

    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None
    ) -> str:
        """
        Synthesizes a 3-stage Spring Boot multi-stage Dockerfile:
        1. Builder (Maven/Gradle compile & package)
        2. Extractor (Spring Boot Layertools split)
        3. Runtime (Minimal headless JRE with unprivileged non-root appuser)
        """
        root = os.path.abspath(root_dir)
        is_gradle = os.path.exists(os.path.join(root, "build.gradle")) or os.path.exists(os.path.join(root, "build.gradle.kts"))

        # Build Stage Setup
        if is_gradle:
            build_tool = "gradle"
            build_copy = "COPY build.gradle* settings.gradle* gradlew ./\nCOPY gradle ./gradle"
            build_cmd = "./gradlew bootJar --no-daemon -x test || gradle bootJar -x test"
            jar_source = "build/libs/*.jar"
        else:
            build_tool = "maven"
            build_copy = "COPY pom.xml mvnw ./\nCOPY .mvn ./.mvn"
            build_cmd = "./mvnw clean package -DskipTests || mvn clean package -DskipTests"
            jar_source = "target/*.jar"

        jdk_image = "eclipse-temurin:17-jdk-alpine"
        jre_image = "eclipse-temurin:17-jre-alpine"

        return f"""# Generated by Rover-Slim Polyglot Synthesizer for Java / Spring Boot
# Stage 1: Build & Package (Discarding compiler caches)
FROM {jdk_image} AS builder
WORKDIR /workspace
{build_copy}
COPY src ./src
RUN {build_cmd}

# Stage 2: Extract Spring Boot Layertools (Layer caching optimization)
FROM {jre_image} AS extractor
WORKDIR /workspace
COPY --from=builder /workspace/{jar_source} app.jar
RUN java -Djarmode=layertools -jar app.jar extract || mkdir -p application && mv app.jar application/

# Stage 3: Minimal Production Runtime
FROM {jre_image} AS runtime
WORKDIR /app

# Hardened unprivileged non-root user
RUN addgroup -S -g 10001 appgroup && adduser -S -u 10001 -G appgroup appuser

# Copy separated layers to maximize Docker cache efficiency
COPY --from=extractor /workspace/dependencies/ ./ 2>/dev/null || true
COPY --from=extractor /workspace/spring-boot-loader/ ./ 2>/dev/null || true
COPY --from=extractor /workspace/snapshot-dependencies/ ./ 2>/dev/null || true
COPY --from=extractor /workspace/application/ ./

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \\
  CMD wget -qO- http://localhost:8080/actuator/health || wget -qO- http://localhost:8080/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "org.springframework.boot.loader.launch.JarLauncher"]
"""

    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        """Auto-discovers Spring Boot Actuator, standard health routes, and ports."""
        root = os.path.abspath(root_dir)
        port = 8080
        path = "/actuator/health"

        # Check application.properties or application.yml for server.port
        prop_files = ["src/main/resources/application.properties", "application.properties"]
        for p in prop_files:
            fp = os.path.join(root, p)
            if os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("server.port"):
                                val = line.split("=")[-1].strip()
                                if val.isdigit():
                                    port = int(val)
                except Exception:
                    pass

        return [
            ProbeConfig(
                name="Spring Boot Actuator Health",
                type="http",
                port=port,
                path=path,
                expected_status=200,
                timeout_seconds=5
            )
        ]
