# Rover Slim: Enterprise Container Optimization Platform
## Architecture Specification, Adversarial Technical Critique (/grill-me) & MoSCoW Implementation Plan (/plan)

---

**Author**: Rover Slim Core Architecture & Engineering Team  
**Document Version**: 2.0-ENTERPRISE-REVIEW  
**Status**: Authoritative Architectural Plan & Critique  
**Date**: November 2026  
**Target Path**: `ROVER_SLIM_PLAN.md`  
**Reference Codebase**: `rover_slim/`, `extension/`, `action.yml`, Enterprise Reference Estate Documents  

---

## Table of Contents
1. [Executive Summary & Specification Context](#1-executive-summary--specification-context)
   - [1.1 Product Vision & Strategic Objective](#11-product-vision--strategic-objective)
   - [1.2 The Brownfield Container Challenge](#12-the-brownfield-container-challenge)
   - [1.3 Platform Architectural Topology](#13-platform-architectural-topology)
   - [1.4 The Codebase Reality vs. Specification Gap](#14-the-codebase-reality-vs-specification-gap)
2. [Adversarial Technical Critique & Feasibility Analysis (/grill-me)](#2-adversarial-technical-critique--feasibility-analysis-grill-me)
   - [2.1 Pillar 1: Workstation Profiling Feasibility Across Host OS Environments](#21-pillar-1-workstation-profiling-feasibility-across-host-os-environments)
     - [A. eBPF Kernel Tracing in Docker Desktop VMs (Windows WSL2, macOS HyperKit/Virtualization, Linux Native)](#a-ebpf-kernel-tracing-in-docker-desktop-vms-windows-wsl2-macos-hyperkitvirtualization-linux-native)
     - [B. JVM JVMTI Bytecode Profiling (Safepoints, Dynamic Proxies, SPI, JNI, Fat JARs)](#b-jvm-jvmti-bytecode-profiling-safepoints-dynamic-proxies-spi-jni-fat-jars)
     - [C. .NET CLR Diagnostic Port IPC (Socket Permissions, UID Isolation, EventPipe, ALC)](#c-net-clr-diagnostic-port-ipc-socket-permissions-uid-isolation-eventpipe-alc)
   - [2.2 Pillar 2: Dynamic Stripping Risks vs. Runtime Dynamics](#22-pillar-2-dynamic-stripping-risks-vs-runtime-dynamics)
     - [A. The Fallacy of Test-Driven Pruning & Coverage Deficit](#a-the-fallacy-of-test-driven-pruning--coverage-deficit)
     - [B. Runtime Dynamic Failure Matrix](#b-runtime-dynamic-failure-matrix)
     - [C. Concrete Technical Safeguards & Fallback Architectures](#c-concrete-technical-safeguards--fallback-architectures)
   - [2.3 Pillar 3: Brownfield Kubernetes Decoupling Patterns](#23-pillar-3-brownfield-kubernetes-decoupling-patterns)
     - [A. Init Container + Shared emptyDir Volume: Latency, Disk Pressure & Autoscaling Failure](#a-init-container--shared-emptydir-volume-latency-disk-pressure--autoscaling-failure)
     - [B. ORAS OCI Content Artifacts: Kubelet Limitations & Legacy Registry Incompatibility](#b-oras-oci-content-artifacts-kubelet-limitations--legacy-registry-incompatibility)
     - [C. Architectural Comparison Matrix](#c-architectural-comparison-matrix)
   - [2.4 Pillar 4: Mathematical & Billing Stress-Testing of Enterprise ROI](#24-pillar-4-mathematical--billing-stress-testing-of-enterprise-roi)
     - [A. Challenge 1: The Developer Productivity Claim ($400,000/yr)](#a-challenge-1-the-developer-productivity-claim-400000yr)
     - [B. Challenge 2: The Multi-Runtime 75% Footprint Reduction Claim](#b-challenge-2-the-multi-runtime-75-footprint-reduction-claim)
     - [C. Challenge 3: Network Egress & Data Pulls ($19,440/yr vs. $0.00/GB In-Region)](#c-challenge-3-network-egress--data-pulls-19440yr-vs-000gb-in-region)
     - [D. Challenge 4: Vulnerability & Patching Toil ($30,000/yr)](#d-challenge-4-vulnerability--patching-toil-30000yr)
     - [E. Challenge 5: Registry Storage Costs ($1,440/yr)](#e-challenge-5-registry-storage-costs-1440yr)
     - [F. Defensible ROI Summary & Sensitivities](#f-defensible-roi-summary--sensitivities)
3. [MoSCoW Prioritized Implementation Plan (/plan)](#3-moscow-prioritized-implementation-plan-plan)
   - [3.1 Taxonomy Overview & Story Point Allocation](#31-taxonomy-overview--story-point-allocation)
   - [3.2 Must Have: MVP Viability Core Capabilities (7 Components, 38 SP)](#32-must-have-mvp-viability-core-capabilities-7-components-38-sp)
   - [3.3 Should Have: Enterprise Operational Adoption Capabilities (7 Components, 48 SP)](#33-should-have-enterprise-operational-adoption-capabilities-7-components-48-sp)
   - [3.4 Could Have: High-Value Optimizations & Decoupling (6 Components, 31 SP)](#34-could-have-high-value-optimizations--decoupling-6-components-31-sp)
   - [3.5 Won't Have (For Now): Explicitly Deferred Out-of-Scope Items (5 Items)](#35-wont-have-for-now-explicitly-deferred-out-of-scope-items-5-items)
   - [3.6 Traceability Matrix of All 25 System Components](#36-traceability-matrix-of-all-25-system-components)
4. [Sequenced 4-Phase Implementation Roadmap](#4-sequenced-4-phase-implementation-roadmap)
   - [4.1 Phased Execution Timeline (22 Calendar Weeks / 11 Sprints)](#41-phased-execution-timeline-22-calendar-weeks--11-sprints)
   - [4.2 Phase 1: Discovery & Triage (Weeks 1–4)](#42-phase-1-discovery--triage-weeks-14)
   - [4.3 Phase 2: Local Pilot & Validation (Weeks 5–10)](#43-phase-2-local-pilot--validation-weeks-510)
   - [4.4 Phase 3: Pre-Prod Stress Testing (Weeks 11–16)](#44-phase-3-pre-prod-stress-testing-weeks-1116)
   - [4.5 Phase 4: CI/CD Enforcement (Weeks 17–22)](#45-phase-4-cicd-enforcement-weeks-1722)
   - [4.6 Verification Gates G1 Through G4](#46-verification-gates-g1-through-g4)
5. [Comprehensive Risk & Mitigation Matrix](#5-comprehensive-risk--mitigation-matrix)
6. [Enterprise Adoption & Governance Framework](#6-enterprise-adoption--governance-framework)
   - [6.1 Change Management Strategy](#61-change-management-strategy)
   - [6.2 Pilot Selection Criteria & Scoring Rubric](#62-pilot-selection-criteria--scoring-rubric)
   - [6.3 Developer Education & Gamified Engagement](#63-developer-education--gamified-engagement)
   - [6.4 CI/CD Policy Governance & Promotion Controls](#64-cicd-policy-governance--promotion-controls)
7. [Verification & Audit Attestation](#7-verification--audit-attestation)

---

## 1. Executive Summary & Specification Context

### 1.1 Product Vision & Strategic Objective
Rover Slim is an enterprise-grade container optimization engine, developer workbench, and CI/CD policy enforcer architected to remediate systemic container bloat in complex brownfield application estates. Across large-scale enterprise environments—spanning legacy Java (Spring Boot), .NET Core, Python, and Node.js microservices—container images routinely inflate to 1.2 GB – 2.5 GB. 

This bloat degrades developer velocity, slows horizontal pod autoscaling (HPA), exhausts cluster ephemeral storage, inflates container registry footprints, and broadens attack surfaces through unreferenced OS binaries, compilers, shell interpreters, and build toolchains.

The foundational design premise of Rover Slim is **operational separation of concerns**:
1. **Intrusive Discovery Confined to Local Workstations**: Tracing, AST dependency mapping, and optimization synthesis occur exclusively within the developer's local Docker Desktop or CLI sandbox under controlled test load, preserving a strict *Zero Production Overhead* guarantee.
2. **Lightweight Gatekeeping in CI/CD**: Pull request pipelines enforce immutable policy thresholds (maximum allowable image size deltas, layer waste budgets, and critical CVE blocklists) via a fast, non-intrusive GitHub Action without executing runtime profiling or dynamic trace engines in CI runners.

```
+---------------------------------------------------------------------------------------+
|                              LOCAL DEVELOPER WORKSTATION                              |
|  +---------------------------------------------------------------------------------+  |
|  |                 Rover Slim Docker Desktop Extension / Local CLI                 |  |
|  |  * Static AST Import Parsing & Package Dependency Graph Resolution              |  |
|  |  * In-VM Test Sandbox Tracing (JVM JVMTI / .NET CLR EventPipe / AST)            |  |
|  |  * Deterministic Multi-Stage Dockerfile Synthesizer (Non-Root UID 10001)        |  |
|  |  * Green-on-Arrival (GoA) Sentinel: Ephemeral Startup Probing & Auto-Rollback   |  |
|  |  * Interactive Monaco Diff Viewer, Package Matrix UI & Gamified RPG ROI Widget |  |
|  +---------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v (Optimized Dockerfile, .dockerignore, SBOM)
+---------------------------------------------------------------------------------------+
|                               ENTERPRISE CI/CD PIPELINE                               |
|  +---------------------------------------------------------------------------------+  |
|  |                     Lightweight Composite GitHub Action                         |  |
|  |  * Zero-Profiling Fast Build & Image Inspection (<45 seconds)                   |  |
|  |  * Hard Policy Gate: max_image_size_mb, max_wasted_percent                        |  |
|  |  * Security Gate: Trivy/Grype CVE Blocklist (Zero CRITICAL/HIGH tolerance)       |  |
|  |  * Multi-Environment Promotion Matrix (Dev -> QA -> Pre-Prod -> Prod)          |  |
|  +---------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v (Verified Slim Image: registry.corp/svc:v1-slim)
+---------------------------------------------------------------------------------------+
|                             ENTERPRISE KUBERNETES FLEET                               |
|  * Fast Pod Startup (<5s vs 45s) | Rapid HPA Response | Minimized Node Disk Pressure  |
|  * Hardened Non-Root Container Security | Reduced CVE Vulnerability Scanning Noise    |
+---------------------------------------------------------------------------------------+
```

---

### 1.2 The Brownfield Container Challenge
Enterprise software estates do not resemble pristine greenfield microservices. A survey of the enterprise reference estate—specifically the **100 enterprise brownfield microservices** audited across baseline enterprise repositories—reveals the true nature of brownfield container bloat:

- **Massive Single-Layer Bloat**: Images such as enterprise administrative portals and UI services total **1,629 MB**, with a single unoptimized `RUN` layer consuming **1,075 MB**. This layer bundles Node.js compilers, Python build tools, raw Git clones, and unpurged package manager caches (`apt-get`, `npm cache`).
- **Heavy Monolithic Runtimes**: Core backend services such as authentication and identity repository services (1,235 MB and 1,150 MB) package full Java Development Kits (JDKs) rather than headless JREs, bundling debugging tools (`jstack`, `jmap`), compiler tools (`javac`), and native C cryptographic libraries.
- **Embedded External Zips**: Production startup scripts pull 500 MB+ artifact repository ZIP archives containing localization templates, reference keys, and client UI bundles via runtime `wget` commands, attempting to decouple images at run-time but introducing severe pod startup latency and network fragility.
- **Legacy Security Debt**: Baseline enterprise images contain an average of 42 CVEs (including 3 Critical and 8 High severity vulnerabilities), primarily inherited from unpatched OS packages (`curl`, `openssl`, `glibc`, `tar`, `systemd`) bundled into monolithic base images (`ubuntu:18.04`, `centos:7`).

---

### 1.3 Platform Architectural Topology
Rover Slim addresses this reality through four interconnected subsystems:

1. **Core Optimization & Synthesis Engine (`rover_slim/`)**:
   - `parsers/ast_parser.py` & `parsers/transitive_resolver.py`: Statically parses code abstract syntax trees (AST) to identify actively imported modules, resolves transitive dependencies via metadata, and strips unreferenced development/test packages (`pytest`, `locust`, `mock`, `black`).
   - `synthesizers/multistage.py`: Synthesizes deterministic 2-stage and 3-stage Dockerfiles utilizing distroless or minimal Alpine/Wolfi runtime images, enforcing an unprivileged non-root user (`appuser`, UID `10001`), hardened capability drops (`--cap-drop=ALL`), and context shielding via synthesized `.dockerignore`.
2. **Developer Workstation Workbench (`extension/`)**:
   - A Docker Desktop Extension comprising an Electron React/TypeScript frontend (Monaco diff editor, 2-column dependency classification matrix, trophy card ROI dashboard) communicating through a Unix domain socket bridge (`/run/guest-services/rover-slim.sock`) to a FastAPI backend service (`rover_slim/server/app.py`) running inside the local Docker Desktop VM.
3. **Safety & Runtime Verification Subsystem (`rover_slim/verifiers/`, `rover_slim/core/checkpoint.py`)**:
   - `checkpoint.py`: Guarantees atomic, reversible configuration edits by snapshotting all touched files in `.rover-slim/backups/` before synthesis.
   - `goa_sentinel.py`: "Green-on-Arrival" sentinel spins up an ephemeral local container sandbox from the synthesized image, tests container exit codes, verifies HTTP `/health` or TCP socket readiness, and automatically triggers an instant rollback if the container faults.
4. **Enterprise CI/CD Policy Gate (`action.yml`, `.rover-slim.yaml`)**:
   - A lightweight composite GitHub Action executing `rover-slim audit` and `rover-slim optimize --verify-goa` in CI runners. Enforces size delta caps (`max_image_size_mb`), layer waste ceilings (`max_wasted_percent`), and CVE zero-tolerance rules (`fail_on_cve_severity: ["CRITICAL", "HIGH"]`), posting formatted markdown audit summaries directly to pull request comments.

---

### 1.4 The Codebase Reality vs. Specification Gap
An exhaustive, empirical technical survey of the existing codebase (`c:\Users\bsank\rover-slim`) conducted by our technical survey agent reveals a significant architectural delta between the theoretical specification claims (`docs/SPECIFICATION.md`) and the actual working code:

| Architectural Capability | Specification Claim | Codebase Reality (`c:\Users\bsank\rover-slim`) | Architectural Gap & Risk |
| :--- | :--- | :--- | :--- |
| **Multi-Runtime Coverage** | Universal support for Java (Spring Boot), .NET Core, and Python. | Only `PythonLanguageAdapter` and `NodeLanguageAdapter` exist (`rover_slim/languages/registry.py:12-15`). | **Zero Java or .NET implementations exist**. The 100 enterprise Java services cannot be processed by the current code. |
| **Workstation Tracing** | eBPF kernel tracing inside Docker Desktop VM discovers accessed files under test load. | `git grep -i "ebpf"` yields **0 matches in source code**. Only static Python AST import scanning exists (`ast_parser.py:128`). | Spec promises kernel VFS intercept; codebase implements static Python source file parsing. |
| **JVM Profiling** | JVMTI profiler extracts active classes from fat JARs. | `git grep -i "jvmti"` yields **0 matches in source code**. | Spec promises dynamic bytecode profiling; codebase contains no Java agent or bytecode manipulation. |
| **.NET Diagnostics** | .NET CLR diagnostic port IPC tracks loaded assemblies. | `git grep -i "clr"` yields **0 matches in source code**. | Spec promises CLR EventPipe IPC; codebase contains no .NET diagnostic client. |
| **Artifact Decoupling** | Automatic offloading of heavy assets via ORAS OCI artifacts and Init Containers. | `git grep -i "oras"` yields **0 matches in source code**. No K8s manifest synthesizers exist. | Spec promises OCI artifact extraction; codebase contains no ORAS CLI integration. |
| **Desktop Extension** | Extension VM runs as a kernel tracing supervisor. | Extension backend runs unprivileged container (`extension/docker-compose.yaml:1-10`) mounting only `/var/run/docker.sock`. | Extension acts as a GUI Dockerfile generator and Docker CLI wrapper, not a kernel tracer. |
| **Auditing & CVE Scanning** | Real-time layer de-duplication and live CVE scanning. | Layer waste uses hardcoded heuristics (12.5% if layers > 10; `layer_auditor.py:87`); CVE auditor falls back to hardcoded counts based on tag strings (`cve_auditor.py:98`). | Heuristic fallbacks produce synthetic security metrics when external tools are absent. |
| **Node.js Synthesizer** | Functional Node.js multi-stage Dockerfile generator. | Line 149 of `node_adapter.py` contains invalid Dockerfile syntax: `COPY --from=builder /app/dist ./dist 2>/dev/null \|\| ...` | Docker BuildKit fails to parse shell operators inside a `COPY` instruction. |

**Strategic Directive**: Rover Slim cannot bridge this gap by merely writing superficial wrappers around unfeasible technologies. A thorough adversarial technical critique (/grill-me) must challenge the core mechanics, expose failure modes, formulate concrete technical safeguards, stress-test financial assumptions, and establish an honest, prioritized MoSCoW implementation plan (/plan).

---

## 2. Adversarial Technical Critique & Feasibility Analysis (/grill-me)

### 2.1 Pillar 1: Workstation Profiling Feasibility Across Host OS Environments

The specification asserts: *"All intrusive profiling mechanisms—including eBPF kernel tracing, JVM JVMTI profiling, and .NET CLR diagnostic port IPC—execute strictly inside the isolated VM of the local developer's Docker Desktop Extension, providing a zero-production-overhead guarantee."*

We challenge this assertion across operating system architectures, container hypervisors, and runtime boundaries.

```
+--------------------------------------------------------------------------------------------------+
|                  WORKSTATION PROFILING KERNEL & HYPERVISOR BOUNDARIES                            |
+--------------------------------------------------------------------------------------------------+
|  WINDOWS 11 (WSL2 Utility VM)                                                                    |
|  [Host NTFS C:\] --(9P/Plan9)--> [/mnt/c/..] --(WSL2 Kernel 5.15/6.6)--> [Missing BTF / Headers]  |
|  * Blocked: eBPF CO-RE fails (No /sys/kernel/btf/vmlinux). EDR blocks privileged containers.     |
+--------------------------------------------------------------------------------------------------+
|  MACOS (Apple Virtualization.framework / LinuxKit)                                              |
|  [Host APFS] --(VirtioFS / gRPC-FUSE)--> [LinuxKit MicroVM Kernel] --> [Synthetic VFS Inodes]    |
|  * Broken: VFS kprobes miss host VirtioFS file opens. LinuxKit strips kprobes & BTF debuginfo.   |
+--------------------------------------------------------------------------------------------------+
|  LINUX (Native Docker Engine)                                                                    |
|  [Host ext4/xfs] --(Native VFS)--> [Host Kernel] --> [SELinux / AppArmor / unprivileged_bpf=1]  |
|  * Restricted: Standard developer accounts lack CAP_BPF / CAP_SYS_ADMIN; corporate policy deny.  |
+--------------------------------------------------------------------------------------------------+
```

---

#### A. eBPF Kernel Tracing in Docker Desktop VMs (Windows WSL2, macOS HyperKit/Virtualization, Linux Native)

1. **Windows WSL2 Kernel & BTF Deficits**:
   - *Architecture*: On Windows 10/11, Docker Desktop runs inside a specialized WSL2 utility distribution (`docker-desktop`), managed by Microsoft's customized kernel (`linux-msft-wsl-5.15.x` or `6.6.x`).
   - *Failure Mode*: Modern eBPF programs rely on BPF Type Format (BTF) and Compile Once – Run Everywhere (CO-RE) metadata located at `/sys/kernel/btf/vmlinux`. Across standard enterprise Windows installations, Microsoft's WSL2 kernel is compiled without `CONFIG_DEBUG_INFO_BTF=y` or strips debug symbols to minimize memory footprint. 
   - *Header Absence*: Traditional BCC (BPF Compiler Collection) tracers compile C probes on the fly using kernel headers (`/usr/src/linux-headers-$(uname -r)`). In WSL2, no matching header packages exist in standard package repositories (`apt`, `dnf`), causing BCC compilation to fail instantly with `fatal error: linux/kconfig.h: No such file or directory`.
   - *Enterprise EDR Restrictions*: Loading eBPF programs requires `CAP_BPF` + `CAP_PERFMON` (Linux 5.8+) or `CAP_SYS_ADMIN`, necessitating running containers with `--privileged`. Enterprise workstation security configurations (CrowdStrike Falcon, Microsoft Defender for Endpoint) explicitly block privileged container execution on developer endpoints via group policy to prevent kernel privilege escalation and credential extraction from WSL2 memory.
   - *Cgroup-v2 Isolation Deficit*: Kernel tracepoints on `sys_enter_openat` or `vfs_read` observe every file open event across the entire WSL2 VM. This captures background disk I/O from the Docker daemon, containerd snapshotters, Windows filesystem interop daemons (`/init`, `/plan9`), and IDE language servers. Without complex cgroup-v2 ID filtering (`bpf_get_current_cgroup_id()`), the tracer floods its buffers with false-positive file dependencies.

2. **macOS HyperKit & Apple Virtualization.framework Constraints**:
   - *Architecture*: macOS cannot run Linux containers natively. Docker Desktop provisions a minimal LinuxKit microVM via Apple's `Virtualization.framework` (or legacy HyperKit).
   - *VirtioFS Inode Translation Breakage*: Developer source code resides on the macOS APFS host filesystem and is shared into the VM via VirtioFS or gRPC-FUSE. File operations executed inside the container do not touch native Linux block devices (`ext4`/`xfs`). Instead, operations traverse hypervisor IPC. In-kernel eBPF VFS tracepoints either miss cached host operations entirely or capture synthetic hypervisor inodes that cannot be translated back to container image layer tarballs.
   - *LinuxKit Kernel Stripping*: LinuxKit kernels are intentionally stripped to sub-40 MB footprints. Kernel features like `CONFIG_BPF_KPROBE_OVERRIDE`, debug info, and tracefs are stripped by default. Attaching arbitrary kprobes causes instant verifier rejections or kernel panics inside the microVM.
   - *Memory Constraints*: Docker Desktop on macOS is typically allocated 2 GB to 4 GB of RAM by default. Running memory-intensive enterprise stacks (e.g., Spring Boot microservices requiring 1.5 GB heap) alongside eBPF perf event ring buffers triggers VM-level Out-Of-Memory (OOM) kernel panics.

3. **Linux Native Security Lockdown**:
   - Native Linux hosts enforce kernel lockdown policies: `kernel.unprivileged_bpf_disabled=1` and `kernel.kptr_restrict=2`. Non-root developers cannot load BPF programs without root privileges (`sudo`). Enterprise security policies strictly prohibit granting developers root access to production-mirrored Linux workstations.

4. **Ring Buffer Saturation & Silent Event Dropping**:
   - High-throughput integration tests executing database initialization or static asset compiling generate over 100,000 `openat` and `vfs_read` system calls per second.
   - The eBPF ring buffer (`BPF_MAP_TYPE_RINGBUF` or `PERF_EVENT_ARRAY`) has a fixed kernel memory buffer. When saturated, the kernel silently drops events (`-EFAULT` / dropped counter). Dropped events mean files that were actively read during test execution are omitted from the trace manifest, causing Rover Slim to classify them as "dead weight" and prune them—guaranteeing catastrophic runtime failure in production.

---

#### B. JVM JVMTI Bytecode Profiling (Safepoints, Dynamic Proxies, SPI, JNI, Fat JARs)

The specification proposes utilizing a JVM JVMTI native profiling agent to discover actively referenced classes inside Java (Spring Boot) containers under test load.

1. **Safepoint Bias & Stop-The-World Latency Skew**:
   - JVMTI callbacks for `ClassFileLoadHook`, `ClassPrepare`, or method entry instrumentation require the JVM to bring all application threads to a safepoint.
   - In enterprise Spring Boot applications loading 15,000+ classes across hundreds of JARs, intercepting class load events or rewriting bytecode via ASM/ByteBuddy introduces **15% to 40% CPU overhead**. This latency skew disrupts test suites with strict timeout constraints, causes asynchronous race conditions in integration tests, and triggers premature HTTP probe timeouts in GoA Sentinel.

2. **Dynamic In-Memory Bytecode & Proxies (CGLIB / ByteBuddy)**:
   - Spring Boot relies extensively on runtime bytecode synthesis for core enterprise features: `@Transactional`, `@Async`, Spring Security `@PreAuthorize`, and Spring Data Repositories.
   - These dynamic proxies (e.g., `OrderService$$EnhancerBySpringCGLIB$$b4e2a1`) are generated purely in-memory in the JVM Metaspace; they have *no corresponding `.class` file on the container filesystem*.
   - If an empirical minifier maps loaded class names back to filesystem artifacts, it encounters synthetic class names that cannot be resolved. Worse, if the tracer only records the proxy class and fails to record the underlying target interface or ByteBuddy runtime generator dependencies, pruning removes the backing classes, causing instant `NoClassDefFoundError` upon application boot.

3. **Reflection & Service Provider Interface (SPI / ServiceLoader) Blind Spots**:
   - Modern Java libraries utilize `java.util.ServiceLoader` and `META-INF/services/` descriptors for pluggable providers (e.g., SLF4J loggers, JDBC drivers, Jackson modules, cryptographic providers).
   - If a test load exercises only the standard payment gateway (`StripePaymentProvider`), the secondary provider (`PayPalPaymentProvider`) is never loaded. Stripping the unexercised classes breaks dynamic failover in production.
   - Jackson polymorphism (`@JsonTypeInfo`) dynamically resolves deserialization subtypes based on incoming JSON payloads. Payloads not represented in workstation test fixtures leave subtype classes unaccessed, resulting in `JsonMappingException: Could not resolve type id` in production.

4. **Fat JAR Architecture & Signature Invalidation**:
   - Spring Boot packages applications as executable fat JARs (`BOOT-INF/classes` and `BOOT-INF/lib/*.jar`).
   - If an optimization tool attempts to unpack the fat JAR, remove un-accessed `.class` files, and repack it:
     - Any digitally signed JAR dependency (e.g., BouncyCastle, security cryptographic providers, enterprise proprietary SDKs) will immediately fail runtime integrity verification with `java.lang.SecurityException: SHA-256 digest error`.
     - Spring Boot autoconfiguration relies on static metadata descriptors: `META-INF/spring.factories` and `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`. If Spring scans an autoconfiguration class whose dependent classes were stripped, the application fails during startup with `NoClassDefFoundError` or `ClassNotFoundException`.

5. **JNI & Native Shared Libraries**:
   - Java libraries often bundle native C/C++ libraries (`.so` on Linux, `.dll` on Windows) inside JARs and extract them to `/tmp` at runtime (e.g., Netty epoll, RocksDB, SQLite, cryptographic HSM modules).
   - JVMTI traces Java class loading, NOT dynamic `dlopen()` calls from native JNI libraries. Stripping unreferenced `.so` files from the container filesystem will cause JVM crashes with `UnsatisfiedLinkError`.

6. **Injection Overhead & Distroless Container Incompatibility**:
   - Attaching a JVMTI agent dynamically requires the JVM Attach API (`com.sun.tools.attach.VirtualMachine`) and access to the JVM attach socket (`/tmp/.java_pid<PID>`).
   - Modern minimal Java runtime images (`distroless/java`, `eclipse-temurin:alpine-jre`) package only a JRE, intentionally omitting JDK diagnostic utilities (`jcmd`, `jstack`, `attach` library). Dynamic injection is impossible without rebuilding the image with a full JDK.
   - Static attachment requires altering `JAVA_TOOL_OPTIONS` or the Dockerfile `ENTRYPOINT`, which breaks the promise of "zero application changes."

7. **Native Agent Crashes (SIGSEGV)**:
   - JVMTI agents are written in native C/C++ and compiled into shared libraries (`.so`). Unlike pure Java agents, a memory violation, null pointer dereference, or ABI mismatch in a JVMTI native agent terminates the entire JVM process immediately with a `SIGSEGV` or `SIGBUS`.
   - In enterprise estates with mixed JDK vendors (Eclipse Temurin, Oracle JDK, Amazon Corretto, Azul Zulu, GraalVM) and language versions (Java 8, 11, 17, 21), maintaining ABI compatibility across all vendor distributions without crashing developer runtimes is an operational nightmare.

---

#### C. .NET CLR Diagnostic Port IPC (Socket Permissions, UID Isolation, EventPipe, ALC)

The specification proposes utilizing the .NET Core CLR diagnostic port IPC to track loaded assemblies under test load.

1. **Non-Root User Isolation & Linux File Permissions (`0600`)**:
   - In .NET Core 3.0+ on Linux, the CLR runtime creates a Unix domain socket for diagnostics at:
     `/tmp/dotnet-diagnostic-{PID}-{epoch}-socket`
   - Rover Slim mandates running containers as an unprivileged user (`appuser`, UID `10001`). When the application container boots as UID `10001`, the diagnostic socket in `/tmp` is created with permissions `srw-------` (`0600`), owned exclusively by `10001:10001`.
   - If the Docker Desktop extension background sidecar or profiling daemon attempts to connect to this socket from outside the container or as a different user (e.g., UID `0` or `1000`), the Linux kernel rejects the `connect()` syscall with:
     `PermissionError: [Errno 13] Permission denied (EACCES)`
   - Connecting requires either running all profiling daemons under the exact same UID or compromising security by setting `umask 000` inside the target application container.

2. **Mount & PID Namespace Barriers & Capability Dropping (`--cap-drop=ALL`)**:
   - By default in Docker, each container executes in an isolated mount, PID, and IPC namespace. The socket file `/tmp/dotnet-diagnostic-*` exists exclusively within the target container's ephemeral rootfs mount namespace.
   - When enterprise policies enforce unprivileged execution (`UID 10001`) paired with `--cap-drop=ALL` (dropping `CAP_SYS_PTRACE`), ambient Linux capabilities are completely eliminated. Neither host processes nor unprivileged sibling containers can escalate privileges or inspect `/tmp` across container boundaries.
   - A sibling container (such as the Rover Slim extension backend or diagnostic sidecar) cannot access the target container's diagnostic socket unless:
     a) Both containers mount a common host volume onto `/tmp` under matching UID 10001 permissions, and
     b) The diagnostic profiler explicitly joins the target container's PID and IPC namespaces using `--pid=container:<name>` and `--ipc=container:<name>`.
   - In enterprise developer environments where services are spun up via complex `docker-compose.yaml` files or local Kubernetes (Kind/Minikube), altering container namespace parameters breaks standard developer workflows and security policies.

3. **EventPipe Tracing Granularity & Method JIT Overhead**:
   - The diagnostic IPC port communicates with the runtime EventPipe. Capturing assembly load events requires enabling the `Microsoft-Windows-DotNETRuntime` provider with `AssemblyLoaderKeyword` (`0x4`).
   - Assembly load tracing reveals only that an assembly (e.g., `Microsoft.EntityFrameworkCore.dll`) was loaded. It does not provide per-class or per-method granularity.
   - To identify individual unused types, one must enable JIT method compilation events (`JITKeyword`). In large enterprise ASP.NET Core applications with thousands of methods, tracing every JIT compilation event over EventPipe serializes gigabytes of data over IPC, causing CPU throttling, test timeouts, and socket buffer overflows.

4. **AssemblyLoadContext (ALC) & Native P/Invoke Blind Spots**:
   - .NET uses `AssemblyLoadContext` for isolated dynamic plugin loading. Dynamic assemblies loaded from byte arrays (`Assembly.Load(byte[])`), in-memory Roslyn script compilations, and late-bound COM or native P/Invoke libraries (`[DllImport("libsecp256k1")]`, `NativeLibrary.Load`) bypass standard assembly load paths.
   - An empirical minifier that strips unreferenced `.dll` or `.so` files based on EventPipe traces will strip native cryptographic and database driver libraries, resulting in runtime `DllNotFoundException` when unexercised code paths execute.

5. **.NET 6+ Single-File Deployment (`<PublishSingleFile>true</PublishSingleFile>`) Incompatibility**:
   - Modern enterprise .NET microservices (.NET 6, 7, 8+) frequently package services into a single self-contained executable bundle using `<PublishSingleFile>true</PublishSingleFile>`.
   - In .NET 6+, the default single-file deployment embeds managed assemblies directly into the host ELF binary and maps them into memory via runtime memory-mapped files without extracting `.dll` files to `/tmp` (unlike legacy .NET Core 3.1 bundle extractors).
   - Because assemblies are not present as distinct filesystem entities, an empirical container minifier scanning the container filesystem cannot isolate, analyze, or prune unused assemblies from the single binary without corrupting the bundle header or invalidating digital signatures.
   - *Mitigation & Architecture Mandate*: Rover Slim must explicitly require multi-file publish mode (`<PublishSingleFile>false</PublishSingleFile>`) for filesystem-level assembly minification, or must integrate into the MSBuild / CI compilation pipeline prior to single-file bundling, leveraging the native .NET IL Trimmer / ILLink analyzer before final bundle synthesis.

---

### 2.2 Pillar 2: Dynamic Stripping Risks vs. Runtime Dynamics

#### A. The Fallacy of Test-Driven Pruning & Coverage Deficit
The core premise of Rover Slim—pruning any file, class, or package not actively accessed during local test runs—suffers from a fatal structural flaw: **The Test Coverage Deficit**.

- In enterprise brownfield estates, automated test suites rarely exceed **40% to 70%** branch coverage.
- Code paths that are **never or rarely exercised during local developer workstation test runs** include:
  1. **Disaster Recovery & Fault Handling**: Circuit breaker fallbacks, dead-letter queue processors, database reconnection loops, TLS certificate renewal handlers.
  2. **Scheduled Batch Jobs**: Nightly reconciliation tasks, monthly tax calculators, quarterly compliance audit loggers.
  3. **Multi-Tenant / Region Switches**: Dynamic feature flags (LaunchDarkly), alternate payment gateways, locale-specific formatting bundles.
  4. **Cryptographic Fallbacks**: Alternative cipher suites invoked only when client negotiation rejects default TLS ciphers.
- Under Rover Slim's raw trace-and-strip model, if a class or binary is not touched during the local test run, it is stripped. The resulting container boots cleanly in the local sandbox (passing the basic GoA Sentinel check), passes staging smoke tests, and is promoted to production—where it crashes with `NoClassDefFoundError`, `ClassNotFoundException`, or `ModuleNotFoundError` the first time an edge case occurs.

---

#### B. Runtime Dynamic Failure Matrix

| Runtime Ecosystem | Dynamic Loading Mechanism | Stripping Risk / Failure Mode | Production Failure Manifestation |
| :--- | :--- | :--- | :--- |
| **Java (Spring Boot)** | `ClassPathScanningCandidateComponentProvider` (ASM scanning) | Pruning uninstantiated beans removes classes required by downstream conditional beans (`@ConditionalOnClass`). | `BeanCreationException`: Application context fails to initialize on configuration change. |
| **Java (Spring Boot)** | CGLIB / ByteBuddy Runtime Proxies | Synthetic classes (`$$EnhancerBySpringCGLIB$$`) cannot be mapped to disk; underlying interfaces or ByteBuddy runtime stripped. | `NoClassDefFoundError` when calling `@Transactional` or `@PreAuthorize` methods. |
| **Java** | `java.util.ServiceLoader` (SPI) | Provider classes listed in `META-INF/services/` omitted if not exercised during test load. | `ServiceConfigurationError`: Database drivers or logging appenders missing in production. |
| **Java** | Jackson Polymorphic Deserialization | Subtypes registered via `@JsonSubTypes` stripped if specific JSON variant is absent from test fixtures. | `InvalidTypeIdException`: Production API returns 500 when processing legacy payload formats. |
| **Python** | `importlib.import_module()`, `__import__()`, `eval()` | Dynamic plugin loading (e.g., Celery task discovery, SQLAlchemy database dialects, Django apps). | `ModuleNotFoundError`: Worker fails to execute dynamically dispatched background tasks. |
| **Python** | `sys.modules` manipulation & lazy imports | Heavy packages (e.g., Pandas, NumPy, Boto3) employing lazy submodule resolution stripped midway. | `AttributeError: module 'boto3' has no attribute 'client'` under specific AWS SDK operations. |
| **.NET Core** | `Assembly.LoadFrom()`, `Activator.CreateInstance()` | Late-bound dependency injection scanning (e.g., Scrutor assembly scanning). | `InvalidOperationException`: Unable to resolve service for type during runtime routing. |
| **Multi-Runtime** | Native C Libraries (JNI, P/Invoke, `ctypes`, `cffi`) | Managed runtimes load `.so` files via `dlopen()` (e.g., `libssl.so`, `libz.so`, `snappy`). Managed profilers miss native dependencies. | `UnsatisfiedLinkError` (Java) or `DllNotFoundException` (.NET): Critical cryptographic or compression operations fail. |

---

#### C. Concrete Technical Safeguards & Fallback Architectures

To prevent catastrophic runtime failures while still achieving significant container de-bloating, Rover Slim must reject naive class/file stripping and enforce five mandatory engineering safeguards:

```
+---------------------------------------------------------------------------------------------------+
|                              ROVER SLIM FIVE-TIER SAFETY SHIELD                                   |
+---------------------------------------------------------------------------------------------------+
|  1. COARSE-GRAINED PACKAGE BOUNDARY RULE                                                          |
|     * Never prune individual .class files from JARs or .py files from wheels.                     |
|     * Pruning operates strictly at the third-party dependency / package boundary.                |
+---------------------------------------------------------------------------------------------------+
|  2. STATIC MANIFEST & ANNOTATION PRE-SCANNING (ALLOWLIST ENGINE)                                  |
|     * Java: Pre-scan META-INF/services, spring.factories, @ConditionalOnClass, @JsonSubTypes.     |
|     * Python: AST-scan importlib calls, entry_points, and setup.py console_scripts.               |
|     * .NET: Inspect .deps.json and AssemblyLoadContext descriptors.                              |
+---------------------------------------------------------------------------------------------------+
|  3. IMMUTABLE OS SAFE-BASE ALLOWLIST                                                              |
|     * Unconditionally protect ld-linux-*.so, libc.so, libssl.so, /etc/ssl/certs, /etc/resolv.conf|
+---------------------------------------------------------------------------------------------------+
|  4. PRE-PROD SHADOW TESTING & CANARY VALIDATION GATE                                             |
|     * Mirror production traffic (via Envoy/Istio) to slim container for 48 hours.                 |
|     * Assert 0% runtime exception delta and verify GC/memory stability before promotion.          |
+---------------------------------------------------------------------------------------------------+
|  5. DUAL-TAG ATOMIC ROLLBACK MANIFEST                                                             |
|     * Deployment manifests retain both :v1-slim and :v1-fat tags.                                 |
|     * Automated rollback to fat image triggers immediately if 5xx errors breach 1% threshold.     |
+---------------------------------------------------------------------------------------------------+
```

1. **Coarse-Grained Dependency Boundary Rule**:
   - *Mandate*: *Never prune individual `.class` files from an active JAR file or individual `.py` files from an active Python package.*
   - If any class in a JAR is accessed, the entire JAR must be retained. If any module in a Python wheel/package is imported, the entire package directory in `site-packages` must be retained. 
   - *Rationale*: Enterprise frameworks treat packages as atomic semantic units. Fine-grained intra-package class pruning saves negligible space (a few kilobytes per class) while increasing the risk of runtime failure by several orders of magnitude. 85%+ of bloat is eliminated simply by dropping completely unused third-party libraries (e.g., test runners, build tools, unreferenced database drivers).

2. **Static Manifest & Annotation Pre-Scanning (Allowlist Engine)**:
   - Before executing dynamic tracing, Rover Slim must execute an automated static inspection pass:
     - **Java**: Scan all `META-INF/services/`, Spring `application.yml` / `META-INF/spring.factories`, and annotations (`@ConditionalOnClass`, `@JsonSubTypes`). All referenced classes are automatically added to an immutable allowlist.
     - **Python**: Analyze AST nodes for `importlib.import_module()` calls, string literals matching installed package names, and `setup.py` / `pyproject.toml` entry points (`console_scripts`).
     - **.NET**: Inspect `.deps.json` and assembly metadata for late-bound references.
   - Any dependency detected during the static pre-scan is permanently protected from pruning, regardless of whether it was touched during the workstation test run.

3. **Core Operating System Safe-Base Allowlist**:
   - The minifier must unconditionally protect core shared libraries and system configurations:
     - Dynamic linkers: `/lib64/ld-linux-x86-64.so.2`, `/lib/ld-musl-*.so.1`.
     - C standard libraries: `libc.so.6`, `libm.so.6`, `libpthread.so.0`, `libdl.so.2`, `libresolv.so.2`.
     - C++ and compiler runtime libraries: `libstdc++.so.6*`, `libgcc_s.so.1*`, `libgomp.so.1*` (unconditionally protected to safeguard compiled Python C-extensions such as NumPy, SciPy, Pandas, PyTorch, cryptographic modules, and native Java JNI wrappers against dynamic linking runtime crashes).
     - Linux globalization and internationalization (.NET / Python): `icu-libs`, `libicuuc.so*`, `libicui18n.so*`, `libicudata.so*` (unconditionally protected to prevent .NET Core runtime globalization crashes and `TypeInitializationException`, or requiring explicit environment setting `DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1`).
     - Crypto and compression: `libssl.so*`, `libcrypto.so*`, `libz.so*`.
     - Trust stores: `/etc/ssl/certs/`, `/etc/pki/ca-trust/`, `/etc/resolv.conf`, `/etc/nsswitch.conf`.

4. **Shadow Testing / Canary Validation Architecture**:
   - In pre-production staging clusters, Rover Slim mandates a **48-Hour Shadow Deployment Gate**:
     - The optimized container is deployed alongside the baseline container.
     - Production traffic is shadowed (mirrored) via Envoy / Istio service mesh to both instances without affecting live user responses.
     - The shadow instance is monitored for 48 hours for unhandled exceptions, class loading panics, and JVM/CLR core dumps before promotion.

5. **Automated Dual-Tag Rollback Manifest**:
   - CI/CD pipelines must maintain dual metadata: every optimized deployment manifest references both the slim image (`service:v1.2-slim`) and the unstripped fallback image (`service:v1.2-fat`). In the event of an unhandled runtime error burst (>1% 5xx responses), the orchestrator triggers an immediate automated rollback to the fat image without rebuilding.

---

### 2.3 Pillar 3: Brownfield Kubernetes Decoupling Patterns

The specification advocates two decoupling patterns for heavy static assets (e.g., massive SDK zips, reference datasets, ML weights):
1. Init Container + Shared Volume `emptyDir`
2. ORAS OCI Artifact Separation

We critically examine the operational trade-offs of both patterns in enterprise Kubernetes environments.

---

#### A. Init Container + Shared emptyDir Volume: Latency, Disk Pressure & Autoscaling Failure

1. **Pod Startup Latency & HPA Autoscaling Disruption**:
   - Under Kubernetes pod lifecycle semantics, an Init Container must run to completion *before* application containers initialize.
   - If an Init Container downloads a 1.5 GB asset over the cluster network at 50 MB/s, it adds a mandatory **30-second delay** to every pod startup.
   - During unexpected traffic spikes, Horizontal Pod Autoscalers (HPA) trigger new pod replicas. A 30+ second initialization delay prevents newly spawned pods from absorbing load in time, resulting in HTTP 504 Gateway Timeouts, queue backpressure, and potential cascading cluster failure.

2. **Node Disk Pressure & Ephemeral Storage Evictions**:
   - Standard `emptyDir` volumes are backed by the node’s local disk (`/var/lib/kubelet` on the node root filesystem).
   - If a high-density worker node hosts 15 pods of a service, each downloading 1.5 GB into its local `emptyDir`, the pods consume **22.5 GB of ephemeral disk space**.
   - If an Init Container exceeds the pod’s configured `ephemeral-storage` limit (or causes node disk usage to breach the `imagefs.available` / `nodefs.available` threshold of 85%), the Kubernetes kubelet immediately evicts the pod (`PodEviction: The node was low on resource: ephemeral-storage`).
   - Using `emptyDir: { medium: "Memory" }` avoids disk pressure but forces the asset into host RAM, starving application pods and triggering the Linux Out-Of-Memory (OOM) Killer.

3. **Network Failure & Exponential CrashLoopBackOff**:
   - If the remote asset store (Artifactory, S3, or GCS) experiences transient network saturation or rate limiting, the Init Container curl/wget command fails (exit code 1).
   - Kubernetes restarts the failed Init Container with exponential backoff (10s, 20s, 40s, up to 5 minutes). The entire service enters `CrashLoopBackOff`, preventing healthy pods from running.

4. **Credential Sprawl & Least Privilege Violations**:
   - To download assets, the Init Container requires authentication credentials (AWS IAM IRSA role, GCP Workload Identity, or Kubernetes Secret containing storage tokens).
   - Distributing storage credentials to hundreds of microservice pod specs expands the blast radius of potential secret exposure across development teams.

5. **Air-Gapped & Regulated Environments**:
   - In highly regulated brownfield environments (financial banking core, defense networks), Kubernetes worker nodes are completely air-gapped with zero Internet egress. Pods cannot reach external endpoints at runtime. Pulling dynamic assets requires complex private proxy configurations and internal object store synchronizations that enterprise change management boards routinely reject.

---

#### B. ORAS OCI Content Artifacts: Kubelet Limitations & Legacy Registry Incompatibility

1. **Enterprise Registry Incompatibility (The OCI v1.1 Barrier)**:
   - ORAS relies on OCI Image Specification v1.1.0 or custom artifact media types (`application/vnd.company.asset.v1+tar`).
   - Brownfield enterprise infrastructure frequently runs legacy self-hosted artifact registries: JFrog Artifactory versions prior to 7.x, Sonatype Nexus OSS <= 3.40, Harbor < 2.8, or legacy Docker Registry v2.
   - When an automated pipeline pushes an ORAS manifest with custom media types to a legacy enterprise registry, the registry rejects the push with:
     ```http
     HTTP/1.1 400 Bad Request
     {"errors":[{"code":"MANIFEST_INVALID","message":"unsupported mediaType application/vnd.company.asset.v1+tar"}]}
     ```
   - Forcing enterprise infrastructure teams to upgrade core artifact repositories across the entire company is a multi-quarter organizational roadblock that halts Rover Slim adoption.

2. **Kubelet Inability to Pull OCI Artifacts (The In-Pod Credential Trap)**:
   - The Kubernetes `kubelet` natively pulls container images using node IAM roles or `imagePullSecrets`. However, the `kubelet` **cannot** pull arbitrary ORAS OCI artifacts into a pod filesystem!
   - To retrieve an ORAS artifact, the application or a helper container must embed the `oras` CLI binary or SDK and execute a pull command at runtime.
   - This architectural limitation requires the pod to possess **container registry authentication tokens**. Exposing registry read tokens (which often have read access to all repository images across the organization) inside runtime application pods directly violates enterprise security standards and NIST container security guidelines.

3. **Network Egress and Inter-AZ Data Transfer Charges**:
   - Pulling massive OCI artifacts from within pods on every restart generates continuous intra-cluster network churn. In cloud environments (AWS/Azure/GCP), traffic crossing Availability Zone boundaries incurs inter-AZ data transfer fees ($0.01 per GB in AWS), generating unexpected cloud infrastructure costs that undermine Rover Slim's financial ROI.

---

#### C. Architectural Comparison Matrix

| Architectural Dimension | Baseline (Monolithic Layers) | Pattern A: Init Container + `emptyDir` | Pattern B: ORAS OCI Content Artifact | Recommended Enterprise Pattern: Immutable Shared Base Layer |
| :--- | :--- | :--- | :--- | :--- |
| **Pod Startup Latency** | Fast after node cache (2–5s); slow on cold pull (45s). | **Severe Delay**: 15–60s added to *every* pod startup; breaks HPA. | Moderate Delay: 5–20s in-pod retrieval via SDK/CLI. | **Optimal**: Sub-second pod startup; pulled once per node, cached in `containerd`. |
| **Node Disk Footprint** | Stored once in node content store (`overlay2`), shared by all pods. | **Severe Waste**: Duplicated per pod on local rootfs; triggers disk eviction. | Duplicated per pod unless mounted to shared host volume. | **Optimal**: Stored once in local container image cache; zero duplicate storage. |
| **Autoscaling (HPA)** | Reliable after base image is cached on node pool. | **High Risk**: Delays scale-out; causes 504 gateway timeouts. | Moderate Risk: Delays application readiness probe. | **Optimal**: Pods scale instantly (<3s) from pre-warmed node cache. |
| **Registry Compatibility** | Universal (Standard OCI / Docker v2). | Universal (Standard S3, Artifactory HTTP, or GCS). | **Poor**: Fails on legacy Nexus <= 3.40, Artifactory < 7, Harbor < 2.8. | Universal: Standard container image format supported by 100% of registries. |
| **In-Pod Credentials** | Zero credentials in pod; kubelet handles image pull. | Storage/IAM secret or IRSA role required in pod spec. | **Critical Risk**: Registry pull secret must be mounted inside pod. | Zero credentials in pod; managed securely by Kubernetes kubelet. |
| **Air-Gapped Viability** | Fully viable via standard air-gapped registry replication. | Complex: Requires mirrored internal object store and proxies. | Complex: Requires OCI 1.1 compliant internal registry mirrors. | Fully viable: Standard container promotion pipeline across air-gap. |

**Architectural Pivot Recommendation**: Instead of complex runtime decoupling via Init Containers or ORAS, brownfield enterprise assets should be packaged into **standardized, immutable base layers** hosted in the local regional registry. The Kubernetes `containerd` runtime natively de-duplicates and caches these layers across all pods on the node, delivering zero startup latency overhead, zero pod-level credential exposure, and 100% compatibility with legacy enterprise registries.

---

### 2.4 Pillar 4: Mathematical & Billing Stress-Testing of Enterprise ROI

Section 4 of `docs/SPECIFICATION.md` establishes an enterprise financial model claiming **$450,880 / year** in enterprise value across 100 legacy microservices and 80 developers. We conduct a rigorous mathematical and operational stress-test of every ROI pillar:

```
+-------------------------------------------------------------------------------------------------------+
|                              ROI ASSUMPTION STRESS-TEST & SENSITIVITY                                 |
+--------------------------+--------------------+---------------------+---------------------------------+
| ROI Pillar               | Claimed Spec Value | Defensible Reality  | Structural Flaw / Bias          |
+--------------------------+--------------------+---------------------+---------------------------------+
| Developer Productivity   | $400,000 / yr      | $0 - $34,640 / yr   | Soft time fallacy; cached layers|
| Vulnerability Triage     | $30,000 / yr       | $6,000 - $10,000 /yr| App-level CVEs remain unpruned  |
| Network Bandwidth Egress | $19,440 / yr       | $0 / yr (AWS/GCP/Az)| In-cluster pulls are FREE (ECR) |
| Registry Storage Savings | $1,440 / yr        | $1,440 / yr         | Valid math, but rounding error  |
+--------------------------+--------------------+---------------------+---------------------------------+
| Total Realizable Value   | ~$450,880 / yr     | $7,440 - $46,080 /yr| OVERSTATED BY 10x - 60x         |
+--------------------------+--------------------+---------------------+---------------------------------+
```

---

#### A. Challenge 1: The Developer Productivity Claim ($400,000/yr)
- **The Claim**: 80 developers waste 2 hours per week waiting for slow image pulls and build/cache bloat (8,000 hrs/yr at an imputed rate of $50/hr = $400,000/yr). This represents **88.7%** of the entire claimed business value.
- **The Empirical Reality**:
  1. **Docker Layer Caching**: Local workstations do not pull 1.5 GB images from scratch on every run. Docker’s layer cache ensures that base OS and SDK layers are downloaded once. Subsequent pulls transfer only the application layer delta (typically 5 MB to 50 MB), which takes 2–5 seconds over standard corporate networks.
  2. **Mathematical Absurdity of 2 Hours/Week Idle Pull Time**:
     - On a standard corporate 250 Mbps connection, downloading an uncompressed 1.2 GB image takes:
       $$\text{Time} = \frac{1,200 \text{ MB} \times 8 \text{ bits/byte}}{250 \text{ Mbps}} = 38.4 \text{ seconds}$$
     - To accumulate 2 hours (7,200 seconds) of pure download waiting time per week, every single developer would have to perform:
       $$\frac{7,200 \text{ seconds}}{38.4 \text{ seconds/pull}} = 187.5 \text{ cold image pulls per week}$$
       That equates to **37.5 cold image pulls per day, every day**. In enterprise brownfield environments, developers write code, run local unit tests, attend meetings, and pull base images at most 2–4 times per week.
  3. **The Soft-Savings Fallacy**: In corporate financial accounting, saving 15 minutes of asynchronous wait time does not reduce engineering payroll or return cash to the balance sheet. Unless engineering headcount is reduced or developers are billable contractors with tracked hourly invoices, soft productivity claims cannot be booked as hard financial ROI.
  4. **Realistic Value**: Even assuming an aggressive 10 minutes saved per week across 80 devs, annual savings equal:
     $$80 \text{ devs} \times 8.66 \text{ hrs/yr} \times \$50/\text{hr} = \$34,640/\text{yr}$$

---

#### B. Challenge 2: The Multi-Runtime 75% Footprint Reduction Claim
- **The Claim**: Uniform 75%+ image size reduction across multi-runtime stacks (Python, Java Spring Boot, .NET Core).
- **The Physical Reality**:
  1. **Python**: Highly receptive to multi-stage de-bloating. A baseline Python image packaging Debian `build-essential`, GCC, static test files, and pip cache (1.2 GB) can be reduced to ~180–220 MB (80%+ reduction) on Alpine/Distroless.
  2. **Java (Spring Boot)**: Highly constrained by JVM runtime physics:
     - Minimal JRE (Eclipse Temurin OpenJDK 17 headless): ~180 MB.
     - Enterprise Spring Boot Fat JAR (Spring Core, Web, Security, Data, Hibernate, Jackson, JDBC drivers): 80–180 MB.
     - Enterprise APM / Observability Agents (OpenTelemetry Java Agent, Dynatrace/AppDynamics OneAgent): 40–80 MB.
     - Base OS / Distroless layers: 25–40 MB.
     - **Hard Minimum Floor for Enterprise Spring Boot**:
       $$180 + 120 + 50 + 30 = 380 \text{ MB}$$
     - An enterprise baseline image of 1,200 MB reduced to 400 MB achieves a **66% reduction**, not 75%+. In services requiring full JDKs for compilation or legacy application servers (WebLogic/WebSphere/Tomcat), the reduction rarely exceeds **35% to 50%**.
     - Achieving <150 MB requires GraalVM Native Image compilation, which is notoriously incompatible with brownfield Spring Boot applications due to heavy reflection and CGLIB dynamic proxies.
  3. **.NET Core**: A minimal ASP.NET Core runtime (`mcr.microsoft.com/dotnet/aspnet:8.0-alpine`) is ~110 MB. With application binaries and native dependencies, baseline services shrink from 800 MB to ~250–300 MB (62% reduction).
  4. **Estate Weighted Average**: Across an enterprise estate of 50 Java services, 30 .NET services, and 20 Python services:
     $$\text{Weighted Reduction} = (0.50 \times 55\%) + (0.30 \times 62\%) + (0.20 \times 82\%) = 27.5\% + 18.6\% + 16.4\% = 62.5\%$$
     The uniform 75% reduction claim is unachievable without breaking enterprise Java runtimes.

---

#### C. Challenge 3: Network Egress & Data Pulls ($19,440/yr vs. $0.00/GB In-Region)
- **The Claim**: 20,000 monthly container pulls across clusters; 75% size reduction saves $19,440 / yr in cloud egress bandwidth fees.
- **The Flaw**: `rover_slim/auditors/cloud_roi_calculator.py` applies the **public Internet data transfer rate** (`AWS_EGRESS_PER_GB = 0.09`):
  $$\text{Saved GB} = \frac{900 \text{ MB} \times 20,000 \text{ pulls}}{1024} = 17,578 \text{ GB}$$
  $$17,578 \text{ GB} \times \$0.09 = \$1,582/\text{month} \times 12 = \$18,984/\text{yr}$$
- **The Cloud Billing Reality**:
  - In enterprise Kubernetes deployments (AWS EKS, GCP GKE, Azure AKS), where do container pulls originate?
    - AWS EKS pulls from **Amazon ECR** located in the *same AWS region*.
    - GCP GKE pulls from **Artifact Registry** located in the *same GCP region*.
    - Azure AKS pulls from **Azure Container Registry (ACR)** located in the *same Azure region*.
  - **AWS Official Pricing Policy**: *Data transfer between Amazon ECR and Amazon EC2/EKS instances within the same region is completely FREE ($0.00 / GB)*.
  - Applying public Internet egress rates to internal, intra-region container pulls is a fundamental cloud billing misrepresentation. Unless an enterprise is pulling images cross-region or from Docker Hub across the public Internet, the actual network egress savings on the enterprise cloud bill is **$0.00 / yr**.

---

#### D. Challenge 4: Vulnerability & Patching Toil ($30,000/yr)
- **The Claim**: Stripping unused packages eliminates CVE triage toil worth $30,000/yr.
- **The Reality**:
  - Stripping unreferenced OS packages (`curl`, `perl`, `tar`, `systemd`) removes low-to-medium OS-level CVEs reported by scanners like Trivy or Clair.
  - However, enterprise security audit toil is overwhelmingly dominated by **application-level vulnerabilities** in third-party dependencies: Log4Shell (Log4j), Spring4Shell, Jackson Databind deserialization, SnakeYAML RCE, and vulnerable transitive NuGet/Python wheels.
  - Rover Slim does not rewrite or remediate application-level dependencies. If an application actively imports a vulnerable version of Spring Boot or Log4j, Rover Slim *must retain it*. Security teams still have to triage, patch, and regression-test those critical CVEs. The claimed $30,000/yr savings will materialize at best as a modest 20–30% reduction in scanner alert noise ($6,000 to $10,000/yr).

---

#### E. Challenge 5: Registry Storage Costs ($1,440/yr)
- **The Math**: 100 services × 10 retained tags = 1,000 image artifacts.
  - 1,000 images × 900 MB saved = 900 GB saved (~0.9 TB).
  - AWS ECR storage costs $0.10 per GB-month:
    $$900 \text{ GB} \times \$0.10/\text{GB-month} \times 12 \text{ months} = \$1,080/\text{yr}$$
- **The Reality**: While the math is plausible, $1,080 to $1,440 per year represents **0.3%** of the claimed value and is an accounting rounding error in an enterprise running 100 microservices. Deploying, licensing, and maintaining Rover Slim to save $90/month on registry storage is economically irrational on its own.

---

#### F. Defensible ROI Summary & Sensitivities
When stripped of inflated claims, what is the **genuine, defensible business value** of Rover Slim?

1. **Cold-Start Pod Launch Acceleration (Availability Value)**:
   - Reducing container uncompressed size from 1.5 GB to 350 MB slashes cold container image extraction time from **35 seconds down to 4.2 seconds**.
   - During node scale-out events in Kubernetes, HPA absorbs traffic spikes 8x faster, preventing 504 timeouts and preserving SLA compliance.
2. **Cluster Ephemeral Storage Relief (Operational Value)**:
   - Saving 1.1 GB per pod across 500 running pods frees **550 GB of disk space** on worker nodes, eliminating random kubelet pod evictions caused by disk exhaustion.
3. **CI/CD Build & Scan Velocity (Pipeline Value)**:
   - Smaller layers reduce image build, push, and Trivy security scanning times from 4.5 minutes down to 45 seconds per pipeline run. Across 100 repositories running 20 builds/day, this saves **1,333 CI runner hours per month**, yielding hard savings of ~$10,000/year in GitHub Actions / cloud compute costs.
4. **Honest Annual Enterprise Financial Return**:
   - Hard CI/CD Runner Compute Savings: ~$10,000 / yr
   - Registry Storage Savings: ~$1,440 / yr
   - Realizable Developer Productivity (10 min/wk): ~$34,640 / yr
   - Realizable Security Alert Triage Noise Reduction: ~$8,000 / yr
   - **Total Realizable Value: ~$54,080 / yr** (A solid, defensible ROI that enterprise CFOs will approve, rather than an easily disprovable $450,000 fantasy).

---

## 3. MoSCoW Prioritized Implementation Plan (/plan)

### 3.1 Taxonomy Overview & Story Point Allocation

To execute this architecture while mitigating technical and operational risks, all **25 functional components** of Rover Slim are categorized across the four MoSCoW tiers. 

- Sizing utilizes standard Agile Story Points (SP) based on the Fibonacci scale ($1, 2, 3, 5, 8, 13$).
- Team capacity is estimated at **12–15 SP per 2-week sprint** for a core engineering team of 3 senior systems/platform developers.

```
+-------------------------------------------------------------------------------------------------------+
|                                 MOSCOW COMPONENT SCOPE BREAKDOWN                                      |
+-----------------------------------+--------------------+--------------------+-------------------------+
| Tier                              | Components Count   | Story Points (SP)  | Dev Sprints / Calendar  |
+-----------------------------------+--------------------+--------------------+-------------------------+
| Must Have (MVP Core Viability)    | 7 Components       | 38 SP              | 4 Sprints (Weeks 1–8)   |
| Should Have (Enterprise Adoption) | 7 Components       | 48 SP              | Phased (Weeks 6–13)     |
| Could Have (Optimizations)        | 6 Components       | 31 SP              | Phased (Weeks 11–16)    |
| Won't Have (Explicitly Deferred)  | 5 Scope Items      | 0 SP (Deferred)    | Out of Scope            |
+-----------------------------------+--------------------+--------------------+-------------------------+
| TOTAL SCOPE                       | 25 Components      | 117 SP             | 22 Calendar Weeks       |
+-----------------------------------+--------------------+--------------------+-------------------------+
```

*Mathematical Velocity & Capacity Reconciliation*:
The 20 active components total exactly **117 Story Points** (Must Have: 38 SP across 7 components; Should Have: 48 SP across 7 components; Could Have: 31 SP across 6 components; Total: 117 SP across 20 active components + 5 deferred scope items). Delivered concurrently across the 11 two-week sprints (22 calendar weeks) of the 4-phase roadmap, this yields an exact average velocity of **10.64 SP/sprint** ($117 \text{ SP} / 11 \text{ sprints} = 10.636 \approx 10.64 \text{ SP/sprint}$), matching the team capacity of 12–15 SP/sprint for 3 senior systems developers.

---

### 3.2 Must Have: MVP Viability Core Capabilities (7 Components, 38 SP)

These capabilities represent the non-negotiable core required to optimize container images deterministically, verify container runtime health, and enforce basic size thresholds in CI/CD.

```
+----------------------------------------------------------------------------------------------------+
|                                 MUST HAVE (MVP CORE) ARCHITECTURE                                  |
|                                                                                                    |
|  [Source Code]                                                                                     |
|       |                                                                                            |
|       v                                                                                            |
|  +----------------------------------------------------------------------------------------------+  |
|  | #1 Baseline Tracing & Dependency Pruning Engine (ASTDependencyParser, ReqParser)              |  |
|  +----------------------------------------------------------------------------------------------+  |
|       |                                                                                            |
|       v                                                                                            |
|  +----------------------------------------------------------------------------------------------+  |
|  | #2 Minimal Multi-Stage Dockerfile Synthesizer (MultiStageSynthesizer, UID 10001, .dockerignore) |  |
|  +----------------------------------------------------------------------------------------------+  |
|       |                                                                                            |
|       +------------------------------------+-----------------------------------+                   |
|       |                                    |                                   |                   |
|       v                                    v                                   v                   |
|  +---------------------------+   +-------------------------------+   +---------------------------+ |
|  | #3 Docker Desktop Shell   |   | #5 GoA Sentinel Health Checker|   | #6 Checkpoint Sentinel    | |
|  | (React UI, Monaco Diff,   |   | (Ephemeral Sandbox Container, |   | (Atomic Backups in        | |
|  | Package Classification)   |   | HTTP /health, Auto-Rollback)  |   | .rover-slim/backups/)     | |
|  +---------------------------+   +-------------------------------+   +---------------------------+ |
|       |                                    |                                   |                   |
|       +------------------------------------+-----------------------------------+                   |
|       |                                                                                            |
|       v                                                                                            |
|  +----------------------------------------------------------------------------------------------+  |
|  | #7 Core Reporting Engine (Terminal, Markdown, JSON, HTML Schema Serializers)                   |  |
|  +----------------------------------------------------------------------------------------------+  |
|       |                                                                                            |
|       v                                                                                            |
|  +----------------------------------------------------------------------------------------------+  |
|  | #4 Basic CI/CD Gating Action (action.yml: max_image_size_mb, PR Markdown Diff Commenter)       |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

#### 1. Baseline Tracing & Dependency Pruning Engine
- **Architectural Layer**: Core Analysis Engine (`rover_slim/parsers/`, `rover_slim/languages/`)
- **Functional Component**: `ASTDependencyParser` & `RequirementsParser`
- **Technical Rationale**: Container bloat primarily stems from packaging unneeded test runners (`pytest`, `black`, `locust`), documentation tools, and build compilers into production images. A deterministic static AST parser that maps imported modules to manifest dependencies eliminates 60-80% of application-layer bloat without runtime risk.
- **Dependency Mapping**:
  - *Prerequisites*: None (foundational component).
  - *Dependents*: Component #2 (Synthesizer), Component #3 (Desktop UI), Component #5 (GoA Sentinel).
- **Complexity Estimate**: **L (Large) — 8 Story Points (1.5 Dev Sprints)**

#### 2. Minimal Multi-Stage Dockerfile Synthesizer
- **Architectural Layer**: Core Synthesis Engine (`rover_slim/synthesizers/`)
- **Functional Component**: `MultiStageSynthesizer` & `DockerignoreGenerator`
- **Technical Rationale**: Legacy Dockerfiles run as root and leave compilers (`gcc`, `make`) in the final layer. The synthesizer outputs a hardened 2/3-stage build with an unprivileged non-root user (`appuser`, UID `10001`), wheels/artifacts copied from builder stages, and context shielding via `.dockerignore`.
- **Dependency Mapping**:
  - *Prerequisites*: Component #1 (Baseline Tracing Engine).
  - *Dependents*: Component #3 (Desktop UI), Component #4 (CI/CD Action), Component #5 (GoA Sentinel).
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 3. Docker Desktop Extension Shell & Visual Workbench
- **Architectural Layer**: Presentation & Extension UI (`extension/`, `rover_slim/server/`)
- **Functional Component**: Extension Host Daemon (`server/app.py`), Monaco Diff View, Package Matrix UI
- **Technical Rationale**: Developers reject CLI-only tools that silently alter build configurations. A visual Docker Desktop extension provides an interactive 2-column dependency classification matrix, side-by-side Monaco diff inspection, and 1-click apply/rollback actions directly within their daily environment.
- **Dependency Mapping**:
  - *Prerequisites*: Core Engine API (`rover_slim/core/engine.py`).
  - *Dependents*: Component #18 (Gamified ROI Dashboard), Component #11 (Reflection Rules Editor).
- **Complexity Estimate**: **L (Large) — 8 Story Points (1.5 Dev Sprints)**

#### 4. Basic CI/CD Gating Action
- **Architectural Layer**: CI/CD Enforcement Gateway (`action.yml`, `.github/workflows/`)
- **Functional Component**: GitHub Composite Action & Pull Request Commenter
- **Technical Rationale**: Optimization gains decay rapidly without automated gatekeeping. A lightweight GitHub Action that validates PR builds against `max_image_size_mb` (e.g., 350 MB) and layer waste percentages (`max_wasted_percent`) prevents regressions before code merges into protected branches.
- **Dependency Mapping**:
  - *Prerequisites*: Core CLI (`rover_slim/cli.py`), Component #7 (Reporters).
  - *Dependents*: Component #10 (Policy Configuration Engine), Phase 4 Enterprise Rollout.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 5. Green-on-Arrival (GoA) Sentinel Health Checker & Auto-Rollback
- **Architectural Layer**: Verification & Safety Layer (`rover_slim/verifiers/`)
- **Functional Component**: `GoASentinelVerifier` & Container Sandbox Runner
- **Technical Rationale**: Fear of container runtime failure is the single largest barrier to container optimization. GoA Sentinel spins up an ephemeral container sandbox immediately after synthesis, checks container exit status, executes HTTP `/health` probes, and triggers automatic rollback if the container faults.
- **Staged Delivery Architecture**:
  - *Stage 1 (Phase 2, Weeks 5–6)*: Baseline Python container health probing (`GET /health`), container exit-code verification, and 1-click snapshot rollback via Checkpoint Sentinel (#6).
  - *Stage 2 (Phase 2, Weeks 8–10)*: Reflection-aware integration ingesting `ReflectionGuard` (#11) keep-rules and allowlists for complex Java (Spring Boot) and .NET microservices prior to staging promotion.
- **Dependency Mapping**:
  - *Prerequisites*: Component #2 (Synthesizer), Component #6 (Checkpoint Sentinel) for Stage 1; Component #11 (`ReflectionGuard`) for Stage 2.
  - *Dependents*: Component #12 (Automated Regression Sandbox), Pre-Prod Stress Testing.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 6. Checkpoint Sentinel & State Management
- **Architectural Layer**: Safety & Rollback Subsystem (`rover_slim/core/checkpoint.py`)
- **Functional Component**: `CheckpointSentinel` Snapshot Manager
- **Technical Rationale**: Modifications to build files (`Dockerfile`, `requirements.txt`, `.dockerignore`) must be atomic and reversible. Checkpoint Sentinel creates timestamped snapshots in `.rover-slim/backups/` and guarantees immediate 1-click restoration upon error.
- **Dependency Mapping**:
  - *Prerequisites*: Local Filesystem Access.
  - *Dependents*: Component #5 (GoA Sentinel Auto-Rollback), Component #3 (Desktop Extension Rollback).
- **Complexity Estimate**: **S (Small) — 3 Story Points (0.5 Dev Sprints)**

#### 7. Core Reporting Engine
- **Architectural Layer**: Reporting & Serialization (`rover_slim/reporters/`)
- **Functional Component**: Terminal, Markdown, JSON, and HTML Schema Serializers
- **Technical Rationale**: Audit results and optimization deltas must be consumed by human developers (Terminal/Markdown) and automated pipelines (JSON schema). Standardized reports provide audit trails for security compliance.
- **Dependency Mapping**:
  - *Prerequisites*: Engine Core Data Models (`rover_slim/models.py`).
  - *Dependents*: Component #4 (CI/CD PR Commenter), Component #3 (Desktop Extension Export).
- **Complexity Estimate**: **S-M (Small-Medium) — 4 Story Points (0.5 Dev Sprints)**

---

### 3.3 Should Have: Enterprise Operational Adoption Capabilities (7 Components, 48 SP)

These capabilities address the multi-runtime realities (Java Spring Boot, .NET Core), dynamic reflection risks, and governance policies demanded by enterprise architecture review boards.

#### 8. Multi-Runtime JVMTI Bytecode Profiling Hook (Java / Spring Boot)
- **Architectural Layer**: Tracing Agent Layer (`rover_slim/languages/java_agent/`)
- **Functional Component**: Java JVMTI Profiling Agent (`-agentlib:rover_jvmti`) & Classloader Interceptor
- **Technical Rationale**: Enterprise microservices are heavily Java-based (Spring Boot). Static AST analysis fails on compiled JAR/WAR archives. A lightweight C++/JVMTI agent intercepting `ClassPrepare` events during local unit/integration test runs records precisely which `.class` files and dependencies inside fat JARs are loaded into memory.
- **Dependency Mapping**:
  - *Prerequisites*: Component #1 (Baseline Tracing Engine), Component #3 (Desktop Sandboxing).
  - *Dependents*: Component #11 (Reflection Safeguards), Java Multi-Stage Synthesizer.
- **Complexity Estimate**: **XL (Extra Large) — 13 Story Points (2 Dev Sprints)**

#### 9. Multi-Runtime .NET CLR Diagnostic IPC Profiler (.NET Core / ASP.NET)
- **Architectural Layer**: Tracing Agent Layer (`rover_slim/languages/dotnet_agent/`)
- **Functional Component**: EventPipe Diagnostics Client & Assembly Load Interceptor
- **Technical Rationale**: .NET microservices package massive framework assemblies and localized satellite resource DLLs. Utilizing the .NET Core Diagnostic IPC port (`/tmp/dotnet-diagnostic-*.socket`) and EventPipe tracing captures loaded assemblies during local test execution without requiring intrusive source changes.
- **Dependency Mapping**:
  - *Prerequisites*: Component #1 (Baseline Tracing Engine), Local VM IPC Proxy.
  - *Dependents*: Component #11 (Reflection Safeguards), .NET Multi-Stage Synthesizer.
- **Complexity Estimate**: **L (Large) — 8 Story Points (1.5 Dev Sprints)**

#### 10. Enterprise Policy Configuration Engine
- **Architectural Layer**: Policy & Governance Engine (`rover_slim/config.py`, `.rover-slim.yaml`)
- **Functional Component**: Policy Rule Evaluator & CVE Blocklist Enforcer
- **Technical Rationale**: Enterprises require centralized governance over allowable base images (e.g., internal distroless registry), mandatory non-root execution, maximum allowable layer waste, and zero tolerance for `CRITICAL` or `HIGH` CVEs.
- **Dependency Mapping**:
  - *Prerequisites*: Component #4 (CI/CD Gating Action), `cve_auditor.py`.
  - *Dependents*: Phase 4 Enterprise CI/CD Rollout, Security Scorecard.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 11. Dynamic Reflection & JNI/PInvoke Safeguards
- **Architectural Layer**: Safe Pruning & Heuristic Guard Layer (`rover_slim/parsers/reflection_guard.py`)
- **Functional Component**: Heuristic Reflection Analyzer & Keep-Rules Manifest Generator
- **Technical Rationale**: Naive unreferenced class/file stripping breaks Spring reflection (`Class.forName`), dynamic service loaders (`META-INF/services`), and C# P/Invoke native libraries. The safeguard generates `keep-rules.yaml` allowlists and flags dynamically invoked dependencies for mandatory retention.
- **Dependency Mapping**:
  - *Prerequisites*: Component #8 (JVMTI Profiler), Component #9 (.NET CLR Profiler).
  - *Dependents*: Component #5 (Stage 2 Integration: Java/.NET Reflection Validation Mode), Phase 3 Pre-Prod Stress Testing.
- **Complexity Estimate**: **L (Large) — 8 Story Points (1.5 Dev Sprints)**

#### 12. Automated Regression Validation & Pre-Flight Sandbox
- **Architectural Layer**: Verification Subsystem (`rover_slim/verifiers/regression_sandbox.py`)
- **Functional Component**: Synthetic Traffic Replayer & Performance Delta Checker
- **Technical Rationale**: Verifying a container only with `GET /health` is insufficient. The regression sandbox executes local synthetic load tests (HTTP replay or unit suite execution inside the ephemeral container) and asserts that cold-start latency (`max_cold_start_seconds: 1.5`) and memory consumption remain within acceptable boundaries.
- **Dependency Mapping**:
  - *Prerequisites*: Component #5 (GoA Sentinel Health Checker).
  - *Dependents*: Phase 3 Pre-Prod Stress Testing.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 13. Multi-Architecture Buildx Synthesis Engine
- **Architectural Layer**: Core Synthesis Engine (`rover_slim/synthesizers/multiarch.py`)
- **Functional Component**: Docker Buildx Multi-Arch Generator (AMD64 & ARM64)
- **Technical Rationale**: Modern enterprise fleets develop locally on Apple Silicon (ARM64) while deploying to AWS Graviton or x86_64 production nodes. The synthesizer must emit platform-specific multi-arch manifests and pre-compiled binary wheel stages.
- **Dependency Mapping**:
  - *Prerequisites*: Component #2 (Minimal Multi-Stage Synthesizer).
  - *Dependents*: CI/CD Multi-Arch Build Gates.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 14. Continuous File Watcher Mode
- **Architectural Layer**: Developer Workstation Tooling (`rover_slim/core/watcher.py`)
- **Functional Component**: `ProjectWatcher` Daemon
- **Technical Rationale**: When developers add new dependencies in code, background AST re-parsing ensures `requirements-prod.txt` and Dockerfiles stay in sync instantly without requiring manual CLI invocation on every save.
- **Dependency Mapping**:
  - *Prerequisites*: Component #1 (Baseline Tracing Engine).
  - *Dependents*: Desktop Extension Real-Time Sync.
- **Complexity Estimate**: **S-M (Small-Medium) — 4 Story Points (0.5 Dev Sprints)**

---

### 3.4 Could Have: High-Value Optimizations & Decoupling (6 Components, 31 SP)

These features provide enterprise optimization leverage, advanced artifact storage decoupling, and gamified developer adoption mechanics.

#### 15. ORAS OCI Content Artifact Decoupling Engine
- **Architectural Layer**: Artifact & Registry Integration (`rover_slim/decoupling/oras_client.py`)
- **Functional Component**: Open Container Initiative (OCI) Artifact Patcher
- **Technical Rationale**: Heavy reference implementations (e.g., `artifactory-ref-impl`, model weights, embedded test SDKs) bloat container images beyond 1.5 GB. Decoupling non-container assets into OCI content artifacts stored in enterprise registries (Harbor, ACR, ECR) via ORAS allows on-demand hydration rather than baking assets into base layers.
- **Dependency Mapping**:
  - *Prerequisites*: Enterprise Registry OCI Spec v1.1 Compatibility.
  - *Dependents*: Component #16 (Kubernetes Init Container Patcher).
- **Complexity Estimate**: **L (Large) — 8 Story Points (1.5 Dev Sprints)**

#### 16. Kubernetes Init Container + Shared Volume (`emptyDir`) Generator
- **Architectural Layer**: Kubernetes Cloud-Native Synthesizer (`rover_slim/synthesizers/k8s_init_gen.py`)
- **Functional Component**: Pod Spec Manifest Patch Synthesizer
- **Technical Rationale**: For immutable static assets that cannot be deleted, generating a Kubernetes Pod template patch that hydrates assets into a shared `emptyDir` volume via a lean init container prevents static layer bloat while ensuring runtime availability.
- **Dependency Mapping**:
  - *Prerequisites*: Component #15 (ORAS Decoupling Engine).
  - *Dependents*: Pre-Prod Kubernetes Deployment Validation.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 17. Advanced Telemetry, Layer Deep-Dive Auditor & Bloat Explainer
- **Architectural Layer**: Auditing & Diagnostics (`rover_slim/auditors/dive_analyzer.py`, `bloat_explainer.py`)
- **Functional Component**: Wagoodman/Dive Integration & CycloneDX/SPDX SBOM Exporter
- **Technical Rationale**: Provides deep layer-by-layer file tree diffs, identifies duplicate files across layers, explains exact origins of layer waste, and outputs standard CycloneDX 1.5 / SPDX 2.3 SBOMs for enterprise security compliance.
- **Dependency Mapping**:
  - *Prerequisites*: Component #7 (Core Reporting Engine), Layer Auditor.
  - *Dependents*: Desktop Extension Visual File Tree Inspector.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 18. Gamified Developer Feedback & Real-Time ROI Dashboard
- **Architectural Layer**: Developer Experience & Engagement (`rover_slim/auditors/cloud_roi_calculator.py`, `server/app.py`)
- **Functional Component**: Rover RPG Engine (XP, Hunter Ranks, Badges) & In-Situ Feedback Memory
- **Technical Rationale**: Developer engagement drives brownfield adoption. Implementing the `rover-feedback-gamified-roi` specification provides live RoI metrics ($ saved on bandwidth and cold start speedup), awards XP/Hunter Ranks (`Bug Scout` $\to$ `Guardian of Apps`), and persists local 👍/👎 feedback to `.rover-slim/learnings.json` to continuously refine pruning heuristics.
- **Dependency Mapping**:
  - *Prerequisites*: Component #3 (Desktop Extension Shell), Cloud ROI Calculator.
  - *Dependents*: Community Adoption & CSAT Metrics.
- **Complexity Estimate**: **M (Medium) — 5 Story Points (1 Dev Sprint)**

#### 19. Agentic Model Context Protocol (MCP) Server Integration
- **Architectural Layer**: Agentic Tooling & AI Gateway (`rover_slim/mcp_server.py`)
- **Functional Component**: Stdio/SSE MCP Server for IDEs (Antigravity, Cursor, Claude)
- **Technical Rationale**: Enables developer AI assistants to inspect container bloat, trigger GoA sentinel checks, and apply multi-stage optimizations safely through standardized tool schemas.
- **Dependency Mapping**:
  - *Prerequisites*: Core CLI & Engine API.
  - *Dependents*: IDE Autonomous Agent Workflows.
- **Complexity Estimate**: **S-M (Small-Medium) — 4 Story Points (0.5 Dev Sprints)**

#### 20. Rancher Desktop Extension Integration
- **Architectural Layer**: Secondary Desktop Platform Integration (`extension/docker-compose.yaml`)
- **Functional Component**: `rdctl` Packaging Bridge & Moby/Containerd Adapter
- **Technical Rationale**: Many enterprise development teams utilize Rancher Desktop / SUSE due to Docker Desktop licensing policies. Providing `rdctl extension install` compatibility broadens workstation reach.
- **Dependency Mapping**:
  - *Prerequisites*: Component #3 (Docker Desktop Extension Shell).
  - *Dependents*: Multi-Platform Desktop Adoption.
- **Complexity Estimate**: **S-M (Small-Medium) — 4 Story Points (0.5 Dev Sprints)**

---

### 3.5 Won't Have (For Now): Explicitly Deferred Out-of-Scope Items (5 Items)

These items are deliberately excluded to safeguard product security, project timeline, and operational stability.

#### 21. In-Cluster Production Kernel eBPF Tracing
- **Architectural Layer**: Production Kubernetes Infrastructure
- **Definitive Deferral Rationale**:
  - *Security Violation*: Running eBPF kernel probes in production clusters requires `CAP_BPF` or `CAP_SYS_ADMIN` privileges, violating enterprise least-privilege security standards.
  - *Performance Risk*: Kernel tracing under live peak customer traffic introduces CPU/memory jitter and potential kernel panic hazards.
  - *Vision Alignment*: The core Rover Slim guarantee is **Zero Production Overhead** via local-first workstation sandboxing.
- **Revisit Trigger**: Post-v3.0, only for air-gapped non-production performance staging clusters with dedicated eBPF security sidecars.

#### 22. Universal Automatic Source Code AST Refactoring
- **Architectural Layer**: Application Source Code Repositories
- **Definitive Deferral Rationale**:
  - *Blast Radius*: Automatically rewriting source files (e.g., dead code elimination, stripping uncalled methods or classes in Java/C#/Python source code) carries unacceptable risks of breaking runtime semantics.
  - *Scope Boundary*: Rover Slim is a container packaging and dependency optimization platform, not a static application compiler or source code refactorer.
- **Revisit Trigger**: Never in scope for container runtime optimization; out-of-scope indefinitely.

#### 23. Full Automated Legacy Build Toolchain Migration
- **Architectural Layer**: Build System Orchestration
- **Definitive Deferral Rationale**:
  - *Complexity Prohibitive*: Automatically rewriting monolithic Ant scripts, complex multi-module Maven POMs, custom Gradle plugins, or legacy MSBuild definitions is infeasible and high-risk.
  - *Clean Interface*: Rover Slim consumes the existing build outputs (JARs, DLLs, wheels) and operates at the container build layer.
- **Revisit Trigger**: Out-of-scope; enterprise build migrations must be driven by application platform teams.

#### 24. Windows Host Container Optimization (`kernelbase.dll` / Windows Server Core)
- **Architectural Layer**: Windows Container Runtime
- **Definitive Deferral Rationale**:
  - *Platform Rigidity*: Windows containers require multi-gigabyte base layers (`mcr.microsoft.com/windows/servercore`) tightly coupled to the host OS kernel version. These OS layers cannot be stripped or deduplicated using Linux userland techniques.
  - *Market Focus*: Over 90% of cloud-native microservice bloat occurs on Linux-based container distributions (Debian, Ubuntu, Alpine, Wolfi).
- **Revisit Trigger**: Post-v2.5, evaluated only if enterprise demand for legacy .NET Framework on Windows Server containers warrants dedicated engineering.

#### 25. Bare-Metal & Monolithic Non-Containerized Workload Optimization
- **Architectural Layer**: Traditional VM / Bare-Metal Infrastructure
- **Definitive Deferral Rationale**:
  - *Architecture Mismatch*: Rover Slim's value proposition relies on OCI container layer segregation, container sandbox verification, and container registry distribution. Bare-metal and traditional VM deployments require distinct configuration management tools (Ansible, Packer, Puppet).
- **Revisit Trigger**: Out-of-scope indefinitely.

---

### 3.6 Traceability Matrix of All 25 System Components

| # | Functional Component | Architectural Layer | MoSCoW Tier | Complexity / SP | Target Phase | Prerequisites | Dependents |
|---|---|---|---|---|---|---|---|
| **1** | `ASTDependencyParser` & `ReqParser` | Core Analysis Layer | **Must Have** | L (8 SP) | Phase 1 (W1–2) | None | 2, 3, 5 |
| **2** | `MultiStageSynthesizer` & `.dockerignore` | Core Synthesis Layer | **Must Have** | M (5 SP) | Phase 1 (W2–3) | 1 | 3, 4, 5 |
| **3** | Docker Desktop Extension & Monaco UI | Presentation & Workbench | **Must Have** | L (8 SP) | Phase 2 (W5–7) | Core Engine | 11, 18 |
| **4** | Basic CI/CD Gating Action (`action.yml`)| CI/CD Enforcement Layer | **Must Have** | M (5 SP) | Phase 2 (W7–8) | CLI, 7 | 10, Phase 4 |
| **5** | `GoASentinelVerifier` & Auto-Rollback | Verification & Safety | **Must Have** | M (5 SP) | Phase 2 (W5–6 [Stage 1], W8–10 [Stage 2]) | 2, 6 (Stage 1); 11 (Stage 2) | 12, Phase 3 |
| **6** | `CheckpointSentinel` Snapshot Manager | Safety & Rollback | **Must Have** | S (3 SP) | Phase 2 (W5) | Filesystem | 3, 5 |
| **7** | Core Schema Reporters (CLI/MD/JSON) | Reporting & Serialization | **Must Have** | S-M (4 SP) | Phase 1 (W3–4) | Data Models | 3, 4 |
| **8** | Java JVMTI Profiling Agent Hook | Tracing Agent Layer | **Should Have** | XL (13 SP) | Phase 2 (W6–8) | 1, 3 | 11, Java Synth |
| **9** | .NET CLR EventPipe Diagnostics Hook | Tracing Agent Layer | **Should Have** | L (8 SP) | Phase 2 (W7–9) | 1, IPC Proxy | 11, .NET Synth |
| **10**| Enterprise Policy Engine (`.rover-slim.yaml`)| Policy & Governance | **Should Have** | M (5 SP) | Phase 3 (W11–12)| 4, CVE Auditor | Phase 4, Scorecard |
| **11**| `ReflectionGuard` & Keep-Rules Manifest | Safe Pruning Guard | **Should Have** | L (8 SP) | Phase 2 (W8–10) | 8, 9 | 5 (Stage 2 Integration), Phase 3 |
| **12**| Regression Sandbox & Traffic Replay | Verification Subsystem | **Should Have** | M (5 SP) | Phase 3 (W12–13)| 5 | Phase 3 Stress |
| **13**| Multi-Arch Buildx Generator (AMD64/ARM64)| Synthesis Engine Layer | **Should Have** | M (5 SP) | Phase 3 (W11–12)| 2 | CI/CD Multi-Arch |
| **14**| `ProjectWatcher` Background Daemon | Workstation Tooling | **Should Have** | S-M (4 SP) | Phase 2 (W7) | 1 | Extension Sync |
| **15**| ORAS OCI Content Decoupling Engine | Artifact & Registry Gateway| **Could Have** | L (8 SP) | Phase 3 (W14–15)| OCI 1.1 Reg | 16 |
| **16**| Kubernetes Init Container Patcher | Cloud-Native Synthesizer | **Could Have** | M (5 SP) | Phase 3 (W15–16)| 15 | K8s Deployments |
| **17**| Dive Deep-Dive Auditor & SBOM Exporter | Auditing & Compliance | **Could Have** | M (5 SP) | Phase 3 (W13–14)| 7, Layer Auditor| Extension Tree |
| **18**| Rover RPG XP & Feedback Widget | Developer Experience | **Could Have** | M (5 SP) | Phase 3 (W13–14)| 3, ROI Calc | CSAT Metrics |
| **19**| Agentic MCP Server Integration | Agentic AI Tooling | **Could Have** | S-M (4 SP) | Phase 3 (W14) | CLI, Engine | AI Agent IDEs |
| **20**| Rancher Desktop (`rdctl`) Adapter | Secondary Extension | **Could Have** | S-M (4 SP) | Phase 3 (W15) | 3 | Rancher Teams |
| **21**| In-Cluster Kernel eBPF Tracing | Infrastructure Profiling | **Won't Have** | 0 SP (Deferred) | Post-v3.0 | N/A | Security Boundary |
| **22**| Universal Source AST Refactoring | Source Repositories | **Won't Have** | 0 SP (Deferred) | Out-of-Scope | N/A | Compiler Boundary |
| **23**| Legacy Build Toolchain Migration | Build Infrastructure | **Won't Have** | 0 SP (Deferred) | Out-of-Scope | N/A | Build System Boundary |
| **24**| Windows Host Container Optimization | Windows Server Core | **Won't Have** | 0 SP (Deferred) | Post-v2.5 | N/A | OS Kernel Boundary |
| **25**| Bare-Metal Monolithic Optimization | Traditional Compute | **Won't Have** | 0 SP (Deferred) | Out-of-Scope | N/A | Platform Boundary |

---

## 4. Sequenced 4-Phase Implementation Roadmap

### 4.1 Phased Execution Timeline (22 Calendar Weeks / 11 Sprints)

The implementation plan is structured across four sequential, gated phases designed to build organizational confidence, harden safety mechanisms, and prevent production regressions.

```
+-------------------------------------------------------------------------------------------------------+
|                                     ROVER SLIM 22-WEEK ROADMAP GANTT                                  |
+-------------------------------------------------------------------------------------------------------+
|  SPRINT:    S1   S2   S3   S4   S5   S6   S7   S8   S9   S10  S11                                 |
|  WEEK:     W1-2 W3-4 W5-6 W7-8 W9-10 W11-12 W13-14 W15-16 W17-18 W19-20 W21-22                      |
+-------------------------------------------------------------------------------------------------------+
|  PHASE 1: DISCOVERY & TRIAGE                                                                          |
|  [M1.1 Estate Inventory]=========>                                                                    |
|  [M1.2 Layer Bloat Audit]=======>                                                                     |
|  [M1.3 CVE Matrix Scan]=========>                                                                     |
|  [M1.4 Pilot Selection]=========> [GATE G1]                                                           |
+-------------------------------------------------------------------------------------------------------+
|  PHASE 2: LOCAL PILOT & VALIDATION                                                                    |
|  [M2.1 Extension Rollout]===============>                                                             |
|  [M2.2 Multi-Runtime Profiling]=========>                                                             |
|  [M2.3 GoA Sandboxing & Safeguards]=====>                                                             |
|  [M2.4 Developer Feedback & Telemetry]=====> [GATE G2]                                                |
+-------------------------------------------------------------------------------------------------------+
|  PHASE 3: PRE-PROD STRESS TESTING                                                                     |
|  [M3.1 Staging Deployment & Multi-Arch Buildx]====>                                                   |
|  [M3.2 Cold-Start & Concurrency Load Test]=======>                                                    |
|  [M3.3 72-Hour Soak & Gamified ROI Engagement]====>                                                   |
|  [M3.4 Decoupling & Shared Base Validation]======> [GATE G3]                                         |
+-------------------------------------------------------------------------------------------------------+
|  PHASE 4: CI/CD ENFORCEMENT                                                                           |
|  [M4.1 Org-Wide GitHub Action Distribution]==============>                                             |
|  [M4.2 Automated PR Diff Commenting]=====================>                                             |
|  [M4.3 Strict Promotion Gates & CVE Enforcement]==========>                                           |
|  [M4.4 Realized Enterprise ROI & Cloud Billing Audit]====> [GATE G4]                                  |
+-------------------------------------------------------------------------------------------------------+
```

---

### 4.2 Phase 1: Discovery & Triage (Weeks 1–4)

#### Objective & Scope
Audit the enterprise estate of 100 brownfield microservices, catalog baseline container images, identify severe layer bloat, establish security CVE baselines, and select the initial 10 pilot microservices.

#### Milestones & Work Breakdown
- **M1.1: Automated Estate Inventory Scanner** (Weeks 1–2): Deploy read-only CLI script to scan enterprise git organizations, cataloging all `Dockerfile`, `requirements.txt`, `pom.xml`, and `.csproj` configurations into `.rover-slim/estate-audit.json`.
- **M1.2: Baseline Image & Layer Bloat Profiling** (Weeks 2–3): Execute `rover-slim audit` across enterprise registries to measure uncompressed sizes, compressed pull sizes, layer counts, and context cache leakage.
- **M1.3: CVE Vulnerability Exposure Matrix** (Week 3): Scan baseline images against OSV / Grype / Trivy databases using `CVEAuditor` to categorize baseline CVE exposure (Critical, High, Medium, Low).
- **M1.4: Triage & Pilot Candidate Selection** (Week 4): Rank all 100 services by bloat severity and business criticality. Select 10 pilot services (5 Python, 3 Java/Spring Boot, 2 .NET Core) representing stateless, low-risk workloads.

#### Cross-Phase Dependencies
- *Inbound*: Read-only access to enterprise Git repositories and container registry read credentials.
- *Outbound*: Pilot service selection feeds directly into Phase 2 workstation deployments.

#### Exit Criteria (Hard Quantitative Gates)
1. **Catalog Completeness**: 100% of in-scope enterprise repositories (100 services) successfully audited and cataloged in `.rover-slim/estate-audit.json`.
2. **Empirical Baseline Logged**: Median baseline image size, layer count, and CVE distribution mathematically documented across all services.
3. **Pilot Cohort Sign-Off**: 10 pilot service lead developers confirm participation and sign off on target criteria.

---

### 4.3 Phase 2: Local Pilot & Validation (Weeks 5–10)

#### Objective & Scope
Deploy the Rover Slim Docker Desktop extension to 20 workstation developers across the 10 pilot services. Execute local tracing under unit/integration test load, synthesize multi-stage Dockerfiles, enforce GoA sentinel verification, and validate zero runtime breakage.

#### Milestones & Work Breakdown
- **M2.1: Docker Desktop Extension Rollout** (Weeks 5–6): Distribute extension package (`bsankarganesh/rover-slim-extension`) to pilot workstations; verify local UI and daemon connectivity.
- **M2.2: Multi-Runtime Local Profiling Execution** (Weeks 6–8):
  - Execute AST parsing on Python pilot services (`python_adapter.py`).
  - Deploy and test JVMTI profiling agent on Java Spring Boot pilot services under test load.
  - Deploy .NET CLR EventPipe listener on .NET Core pilot services.
- **M2.3: GoA Sentinel Sandbox Testing & Staged Safeguard Tuning** (Weeks 8–10): Run ephemeral container sandboxes locally with HTTP `/health` probes; tune `reflection_guard.py` rules based on initial pilot feedback. Deliver Component #5 in two iterations: Stage 1 delivers baseline Python health probing in Weeks 5–6, and Stage 2 completes reflection-aware integration with Component #11 (`ReflectionGuard`) in Weeks 8–10.
- **M2.4: Developer Feedback & Local Pilot Telemetry** (Weeks 9–10): Deploy baseline in-situ feedback logging (`.rover-slim/learnings.json`) and local developer sentiment tracking across the 20 pilot engineers; measure triage speedup and rule accuracy. (Note: Non-blocking Multi-Arch Buildx [#13, 5 SP] and full Gamified RPG Widget [#18, 5 SP] are re-sequenced to Phase 3, smoothing Phase 2 workload from 64 SP down to 54 SP across Sprints 3–5 to strictly align with team velocity).

#### Cross-Phase Dependencies
- *Inbound*: M1.4 Pilot candidate services selected; Docker Desktop v4.20+ installed on workstations.
- *Outbound*: Validated pilot Dockerfiles and configuration profiles ready for staging cluster deployment.

#### Exit Criteria (Hard Quantitative Gates)
1. **Size Reduction Benchmark**: Achieving $\ge 65\%$ uncompressed image size reduction on average across the 10 pilot services (e.g., from ~1.2 GB down to < 400 MB).
2. **Zero Functional Regression**: 100% passing rate on existing unit and integration test suites executed against the optimized container images.
3. **GoA Sentinel Green Rate**: 100% GoA verification pass rate in ephemeral local sandboxes with zero false-negative startup crashes.
4. **Developer Satisfaction**: Net Developer CSAT score $\ge 85\%$ across the 20 pilot engineers.

---

### 4.4 Phase 3: Pre-Prod Stress Testing (Weeks 11–16)

#### Objective & Scope
Promote the 10 optimized pilot images to staging/pre-production Kubernetes clusters. Conduct high-concurrency synthetic load testing, profile JVM/CLR garbage collection behavior, assert cold-start latency gains, and validate alternative decoupling patterns (Init Containers and ORAS OCI artifacts).

#### Milestones & Work Breakdown
- **M3.1: Staging Cluster Deployment & Multi-Arch Buildx** (Weeks 11–12): Deploy optimized containers into pre-production Kubernetes namespaces using standard Helm/Kustomize charts. Execute Component #13 (Multi-Arch Buildx Generator, 5 SP) to emit dual AMD64/ARM64 container images required for heterogeneous pre-prod cluster worker nodes.
- **M3.2: Cold-Start Latency & Concurrency Stress Testing** (Weeks 12–13): Replay synthetic customer traffic at 1x, 2x, and 3x peak load; measure container cold-start latency, memory working set, and HTTP response percentiles (P95, P99).
- **M3.3: Garbage Collection, Soak Testing & Gamified ROI Engagement** (Weeks 13–14): Run 72-hour continuous soak test; monitor JVM heap/metaspace stability and .NET GC pause times to confirm that pruned dependency sets did not alter memory leak characteristics. Roll out Component #18 (Rover RPG XP & Feedback Widget, 5 SP) to pilot developers to track real-time RoI metrics ($ saved on compute and storage) alongside staging load tests.
- **M3.4: Decoupling & Shared Base Layer Validation** (Weeks 15–16): Harmonizing with Section 2.3's architectural critique, test and validate both the OCI artifact decoupling pattern (ORAS hydration via init container into shared `emptyDir` volumes) AND the recommended immutable shared base layers on the heavy test reference service (`artifactory-ref-impl`). Benchmark pod startup latency (target < 5 seconds) and verify zero security token leakage (ensuring application pods do not mount enterprise registry pull secrets directly, comparing against node containerd layer cache hits).

#### Cross-Phase Dependencies
- *Inbound*: M2.3 & M2.4 Validated multi-stage Dockerfiles from local pilot; Component #13 & #18 integration readiness.
- *Outbound*: Performance-certified container profiles and finalized CI/CD policy configuration rules for Phase 4.

#### Exit Criteria (Hard Quantitative Gates)
1. **Latency Overhead Neutrality**: P99 response latency delta under 3x synthetic load $\le +2\%$ compared to baseline fat images.
2. **Cold-Start Speedup**: Minimum 40% reduction in cold-start pod launch latency on new Kubernetes nodes (e.g., reduction from 25s pull+init to < 10s).
3. **Soak Test Stability**: Zero OOMKilled events and zero memory leaks detected over 72 hours of sustained traffic.
4. **Decoupling & Shared Base Integrity**: Standardized immutable shared base layers achieve 100% container runtime compatibility with sub-second pod launch from node containerd cache. For environments evaluating OCI 1.1 artifact decoupling, ORAS hydration must satisfy startup latency < 5 seconds and maintain zero security token leakage (no exposed registry pull secrets in application pod specs).

---

### 4.5 Phase 4: CI/CD Enforcement (Weeks 17–22)

#### Objective & Scope
Roll out the Rover Slim GitHub Action across all 100 enterprise repositories. Enforce strict PR size gating, layer waste budgets, and CVE blocklists. Implement progressive promotion controls (Dev $\to$ QA $\to$ Pre-Prod $\to$ Prod) and verify realized enterprise ROI against cloud billing telemetry.

#### Milestones & Work Breakdown
- **M4.1: Org-Wide GitHub Action Distribution** (Weeks 17–18): Onboard reusable workflow template (`.github/workflows/rover-slim.yml`) into enterprise centralized CI templates.
- **M4.2: Automated PR Diff Governance & Bot Commenting** (Weeks 18–19): Activate automated PR diff comments showing size deltas, pruned dependencies, security scorecard grade, and GoA sentinel status.
- **M4.3: Strict Multi-Environment Promotion Gates** (Weeks 19–20): Configure blocking merge checks: reject PRs with image size $> 350$ MB, layer waste $> 10\%$, or unapproved `CRITICAL`/`HIGH` CVEs.
- **M4.4: Enterprise ROI & Egress Savings Audit** (Weeks 21–22): Audit cloud registry storage invoices (AWS ECR / GCP Artifact Registry) and network egress metrics to measure empirical financial return against the projected financial model.

#### Cross-Phase Dependencies
- *Inbound*: Phase 3 performance certification; finalized `.rover-slim.yaml` policy definitions.
- *Outbound*: Full enterprise operational steady state.

#### Exit Criteria (Hard Quantitative Gates)
1. **Pipeline Coverage**: 100% of active enterprise microservice repositories (100 services) enforce the Rover Slim GitHub Action gate on pull requests.
2. **Zero Critical CVE Promotion**: 100% enforcement of CVE gating policy—zero container artifacts promoted to production containing unpatched critical vulnerabilities.
3. **Storage & Bandwidth Reduction**: Minimum 60% aggregate reduction in monthly registry storage footprint and container pull bandwidth across all clusters.
4. **Financial ROI Realization**: Measured quarterly savings tracking at or above an annualized run rate of $50,000 across cloud compute, storage, and developer velocity.

---

### 4.6 Verification Gates G1 Through G4

Every phase transition requires formal sign-off against an automated, independently verifiable technical gate:

```
+----------------------------------------------------------------------------------------------------+
|                                    VERIFICATION GATES SPECIFICATION                                |
+------+-----------------------------+---------------------------------------+-----------------------+
| Gate | Target Milestone Transition | Automated Command / Script            | Invalidation Condition|
+------+-----------------------------+---------------------------------------+-----------------------+
|  G1  | Phase 1 -> Phase 2          | rover-slim audit --batch-estate .     | Unhandled repo syntax;|
|      | Discovery to Pilot          | python scripts/verify_estate_audit.py | Missing registry tags |
+------+-----------------------------+---------------------------------------+-----------------------+
|  G2  | Phase 2 -> Phase 3          | rover-slim optimize <dir> --verify-goa| ClassNotFoundException|
|      | Pilot to Pre-Prod           | pytest tests/integration/ -v          | Unit test regression  |
+------+-----------------------------+---------------------------------------+-----------------------+
|  G3  | Phase 3 -> Phase 4          | k6 run load-test.js                   | P99 latency delta >2%;|
|      | Pre-Prod to CI/CD           | kubectl get pods -l app=pilot -o wide | OOMKilled; start >=5s;|
|      |                             | rover-slim audit --image staging-...  | Shared cache failure; |
|      |                             | python scripts/audit_pod_security.py  | Token leak in pod spec|
+------+-----------------------------+---------------------------------------+-----------------------+
|  G4  | Phase 4 -> Steady State     | gh workflow run verify-enterprise-gate| CI check bypassed;    |
|      | Full Production Acceptance  | python scripts/audit_roi_billing.py   | Hotfix build blocked  |
+------+-----------------------------+---------------------------------------+-----------------------+
```

1. **Verification Gate G1 (Discovery to Pilot)**:
   - *Command*: `pytest tests/test_dive_analyzer.py tests/test_layer_auditor.py tests/test_cve_auditor.py -v` followed by `python scripts/verify_estate_audit.py`.
   - *Inspection*: Validate that `rover-slim audit` against the sample estate emits structured metrics matching schema requirements in `.rover-slim/estate-audit.json`.
   - *Invalidation Condition*: Unhandled repository layout crashes the auditor, or missing container registry tags prevent baseline size resolution.

2. **Verification Gate G2 (Pilot to Pre-Prod)**:
   - *Command*: `rover-slim optimize <pilot_dir> --verify-goa` followed by running the service's full integration test suite against the optimized image.
   - *Inspection*: Check that `.rover-slim/report.json` records `status: "PASSED"` and `uncompressed_size_mb <= 400.0`.
   - *Invalidation Condition*: Any dynamic runtime failure (e.g., `ClassNotFoundException`, `MissingMethodException`) discovered during post-optimization test suite runs.

3. **Verification Gate G3 (Pre-Prod to CI/CD)**:
   - *Command*: Execute automated staging performance benchmark suite (`k6 run --vus 50 --duration 10m`), run `rover-slim audit --image staging-registry.corp/pilot-svc:optimized`, and execute `python scripts/audit_pod_security.py --namespace pre-prod`.
   - *Inspection*: Validate Prometheus metrics confirming zero abnormal pod restarts, normal GC pause distributions, verified pod readiness probes, container startup latency < 5s, and zero security token leakage (audit pod specifications to verify no registry credentials or secrets are mounted inside application containers, and verify node containerd shared base layer cache hit rates).
   - *Invalidation Condition*: Pod crash loops, reflection errors under heavy traffic, startup latency >= 5s, failure of node containerd shared layer caching, or detection of exposed registry credentials in pod specifications.

4. **Verification Gate G4 (Enterprise Enforcement Final Acceptance)**:
   - *Command*: Execute enterprise compliance audit script verifying that all 100 repos have active `.rover-slim.yaml` configuration, and simulate a PR with an intentionally bloated 1.2 GB container to confirm that CI/CD blocks promotion with exit code 1.
   - *Inspection*: Inspect enterprise GitHub Actions telemetry, confirm 100% gate attachment, and review monthly cloud billing reports.
   - *Invalidation Condition*: Developers bypass CI/CD checks via unauthorized workflow skips, or false-positive size blocks halt production hotfixes.

---

## 5. Comprehensive Risk & Mitigation Matrix

```
+--------------------------------------------------------------------------------------------------------------------+
|                                    ENTERPRISE RISK & MITIGATION MATRIX                                             |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Risk Description         | Category | Impact | Root Cause                 | Concrete Mitigation   | Trigger Metric |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Dynamic Reflection       | Technical| HIGH   | Test coverage deficit;     | Coarse-grained JAR/pkg| Runtime 5xx    |
| Breakage in Java/.NET    |          |        | in-memory CGLIB proxies.   | rule; keep-rules pre- | error burst    |
|                          |          |        |                            | scan; shadow canary.  | > 0.5%.        |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Non-Root Socket IPC      | Technical| MEDIUM | Linux permissions (0600)   | Proxy daemon under    | EACCES error   |
| Permission Denied        |          |        | on /tmp/dotnet-diagnostic. | matching UID 10001;   | on CLR IPC.    |
|                          |          |        |                            | shared volume mounts. |                |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| eBPF Kernel Missing BTF  | Technical| HIGH   | WSL2 / LinuxKit custom     | Pivot to static AST   | BTF not found  |
| on Developer Machines    |          |        | stripped microVM kernels.  | parsing; disable raw  | in /sys/kernel.|
|                          |          |        |                            | in-VM kprobes.        |                |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Init Container Startup   | Operat.  | HIGH   | 1.5 GB asset download over | Immutable base layer  | Pod readiness  |
| Latency Breaches HPA     |          |        | network on every pod init. | caching; containerd   | latency > 15s. |
|                          |          |        |                            | image de-duplication. |                |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Ephemeral Storage Node   | Operat.  | HIGH   | Multi-pod emptyDir pulls   | Enforce pod ephemeral | Kubelet        |
| Evictions (DiskPressure) |          |        | exhausting /var/lib/kubelet| storage requests/     | NodeHasDisk-   |
|                          |          |        | rootfs on worker nodes.    | limits; node alerts.  | Pressure.      |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Legacy Registry Rejection| Operat.  | MEDIUM | Custom OCI media types not | Pre-check registry API| HTTP 400 Bad   |
| of ORAS Artifacts        |          |        | supported by Artifactory<7 | support; fallback to  | Request on     |
|                          |          |        | or Nexus <= 3.40.          | standard OCI layers.  | manifest push. |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Registry Credential Leak | Security | HIGH   | Pods embedding ORAS CLI    | Never embed registry  | Secret audit   |
| via In-Pod Image Pulls   |          |        | require pull tokens.       | tokens in pods; let   | flags in-pod   |
|                          |          |        |                            | kubelet manage pulls. |                |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| False-Positive CI/CD     | Org.     | HIGH   | Legitimate emergency       | Emergency break-glass | CI pipeline    |
| Blocking Emergency Fixes |          |        | security hotfix blocked by | flag (--skip-policy)  | failure on     |
|                          |          |        | rigid size threshold.      | with mandatory audit. | hotfix branch. |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
| Developer Resistance to  | Org.     | MEDIUM | Friction from unfamiliar   | Docker Desktop Monaco | CSAT score     |
| Strict CI Policy Gating  |          |        | tooling & failed builds.   | UI; gamified RPG XP;  | drops below    |
|                          |          |        |                            | in-situ 👍/👎 widget. | 80%.           |
+--------------------------+----------+--------+----------------------------+-----------------------+----------------+
```

---

## 6. Enterprise Adoption & Governance Framework

### 6.1 Change Management Strategy
Brownfield enterprise transformations frequently stall due to cultural resistance, developer friction, and fear of destabilizing mission-critical services. Rover Slim implements a **4-Stage Enterprise Adoption Flywheel**:

1. **Stage 1: Observation & Value Demonstration (Weeks 1–4)**:
   - Deploy Rover Slim strictly in **Audit-Only Mode** (`rover-slim audit`).
   - Run scans across all 100 repositories without touching a single Dockerfile or failing any CI builds.
   - Deliver transparent, data-driven "Bloat & CVE Exposure Reports" to engineering managers, highlighting quick-win candidates.
2. **Stage 2: Developer Empowerment via Local Workbench (Weeks 5–10)**:
   - Provide the Rover Slim Docker Desktop Extension to developer champions.
   - Position Rover Slim as a developer productivity tool that accelerates local build times, rather than a corporate compliance mandate.
   - Leverage the interactive Monaco diff viewer and 1-click rollback to demystify container optimization.
3. **Stage 3: Pre-Production Performance Certification (Weeks 11–16)**:
   - Partner with QA and SRE teams to validate optimized containers in staging clusters.
   - Publish objective cold-start latency and memory benchmarks to build organizational trust across architecture boards.
4. **Stage 4: Progressive Policy Enforcement (Weeks 17–22)**:
   - Introduce CI/CD size gating initially in **Warning / Advisory Mode** (posting PR comments without failing builds).
   - Transition to **Blocking Mode** only after teams have had 30 days to review recommendations and tune local configurations.

---

### 6.2 Pilot Selection Criteria & Scoring Rubric
To maximize early success and prevent high-visibility failures, the initial 10 pilot microservices must be selected using a rigorous **Service Suitability Scoring Rubric** (Score range: 0 to 100):

$$\text{Suitability Score} = (S_{\text{bloat}} \times 0.35) + (S_{\text{test}} \times 0.30) + (S_{\text{stateless}} \times 0.20) + (S_{\text{crit}} \times 0.15)$$

- **Bloat Severity ($S_{\text{bloat}}$, 0–100)**: Services with baseline image sizes $> 1.0$ GB and layer waste $> 20\%$ score 100.
- **Automated Test Coverage ($S_{\text{test}}$, 0–100)**: Services with comprehensive unit/integration test suites ($> 70\%$ code coverage) score 100; services with $< 30\%$ coverage score 0.
- **Statelessness & Resilience ($S_{\text{stateless}}$, 0–100)**: Pure stateless REST APIs score 100; stateful workloads, database connectors, or distributed transaction coordinators score 0.
- **Business Criticality ($S_{\text{crit}}$, 0–100)**: Internal developer tools, non-customer-facing backends, or staging utilities score 100; core payment gateways, authentication cores, and medical record databases score 0.

**Selection Rule**: Only services achieving a Suitability Score $\ge 75$ are approved for Phase 2 Pilot onboarding.

---

### 6.3 Developer Education & Gamified Engagement
To foster organic developer engagement and overcome resistance to optimization policies, Rover Slim integrates the **Rover RPG Engagement Architecture** (`rover-feedback-gamified-roi`):

1. **Gamified XP & Hunter Ranks**:
   - Developers earn Experience Points (XP) for optimizing containers and maintaining clean builds:
     - $+100 \text{ XP}$: First successful multi-stage optimization passing GoA Sentinel.
     - $+250 \text{ XP}$: Slashing container footprint by $> 50\%$.
     - $+500 \text{ XP}$: Eliminating all Critical/High CVEs from a service container.
   - Ranks progress from `Novice Hunter` $\to$ `Container Scout` $\to$ `Bloat Slayer` $\to$ `Guardian of Apps (GoA Master)`.
2. **In-Situ Feedback Memory (`.rover-slim/learnings.json`)**:
   - The Docker Desktop extension embeds a non-intrusive 👍/👎 rating widget next to suggested Dockerfile diffs.
   - If a developer rejects a suggested dependency prune (thumbs down), Rover Slim prompts for a 1-click reason ("Dynamic import needed", "Test file required in container").
   - The feedback is persisted locally in `.rover-slim/learnings.json` and automatically generates a `keep-rules.yaml` exception, preventing the engine from repeating the mistake.
3. **Live Financial & Carbon ROI Counters**:
   - The extension UI displays real-time tangible metrics:
     - *"This optimization saved 850 MB, speeding up pod launch by 28 seconds and saving ~$120/year in cloud runner compute."*
     - Live metrics connect daily coding actions directly to engineering excellence and corporate sustainability goals.

---

### 6.4 CI/CD Policy Governance & Promotion Controls

Enterprise policy governance is defined centrally in `.rover-slim.yaml` and enforced across git branches:

```yaml
# .rover-slim.yaml — Enterprise Container Governance Specification
version: "2.0"
governance:
  enforce_strict: true
  allow_break_glass: true

policies:
  # Size & Layer Waste Thresholds
  max_image_size_mb: 350.0
  max_wasted_percent: 10.0
  max_cold_start_seconds: 1.5

  # Security & Vulnerability Thresholds
  security:
    scanner: "trivy"
    fail_on_cve_severity: ["CRITICAL", "HIGH"]
    allowed_cve_exceptions: []
    enforce_non_root: true
    required_user_id: 10001
    drop_capabilities: ["ALL"]

  # Base Image Compliance
  base_images:
    approved_registries:
      - "registry.corp/base-images/"
      - "cgr.dev/chainguard/"
    disallowed_base_strings:
      - "latest"
      - "ubuntu:18.04"
      - "centos:7"

promotion_matrix:
  dev:
    blocking: false
    require_goa_sentinel: true
  qa:
    blocking: true
    max_image_size_mb: 500.0
    fail_on_cve_severity: ["CRITICAL"]
  pre_prod:
    blocking: true
    max_image_size_mb: 350.0
    fail_on_cve_severity: ["CRITICAL", "HIGH"]
    require_shadow_test_48h: true
  prod:
    blocking: true
    max_image_size_mb: 350.0
    fail_on_cve_severity: ["CRITICAL", "HIGH"]
    require_dual_tag_manifest: true
```

#### Diagnostic Sidecars & Container Capability Dropping
When `drop_capabilities: ["ALL"]` and `enforce_non_root: true` (`UID 10001`) are enforced on distroless or minimal images, ambient Linux kernel capabilities (including `CAP_SYS_PTRACE`) are completely stripped. Under these hardened constraints:
- Host `docker exec` processes and sibling sidecars lack permission to trace processes or inspect non-root Unix sockets (`0600` permissions on `/tmp/dotnet-diagnostic-*` or `/tmp/.java_pid*`).
- Production and pre-production diagnostic sidecars or tracing agents cannot escalate privileges across isolated container boundaries.
- **Mandatory Attachment Pattern**: Any diagnostic or profiling sidecar must explicitly join the target application container's process and IPC namespaces via `--pid=container:<name>` and `--ipc=container:<name>`, and must mount a shared volume onto `/tmp` running under the identical UID (`10001`). This ensures complete namespace and permission alignment while maintaining zero-privilege security boundaries.

#### The Emergency Break-Glass Procedure
To guarantee that CI/CD size gating never halts emergency production hotfixes during a critical incident:
1. Repository administrators can pass `--skip-governance-override="INCIDENT-<ID>"` in the commit message or PR label.
2. The CI action logs a high-severity security audit event to the enterprise SIEM (Splunk / Datadog).
3. The merge proceeds, but automatically opens an automated P2 Jira tracking ticket assigned to the repository owner, requiring remediation within 5 business days.

---

## 7. Verification & Audit Attestation

This document represents the definitive architectural plan, adversarial critique, and MoSCoW implementation blueprint for Rover Slim. All technical mechanisms, operating system kernel behaviors, bytecode/diagnostic IPC constraints, and cloud billing policies detailed herein have been independently evaluated against empirical codebase facts, operating system kernel specifications, and cloud provider pricing documentation.

### Independent Verification Commands
To independently verify the observations, claims, and codebase status documented in this plan:

1. **Verify Absence of In-Code eBPF, JVMTI, and CLR IPC in Existing Codebase**:
   ```bash
   git grep -i "ebpf" -- rover_slim/ extension/
   git grep -i "jvmti" -- rover_slim/ extension/
   git grep -i "clr" -- rover_slim/ extension/
   git grep -i "oras" -- rover_slim/ extension/
   ```
   *Expected Result*: Zero matching lines found in application code, confirming that these mechanisms represent future architecture to be built rather than existing implementations.

2. **Verify Language Registry Adapters**:
   Inspect `rover_slim/languages/registry.py` lines 12–15:
   *Expected Result*: Only `PythonLanguageAdapter` and `NodeLanguageAdapter` are instantiated.

3. **Verify Baseline Test Suite Execution**:
   ```bash
   pytest -v tests/
   ```
   *Expected Result*: 81 tests pass, confirming that existing static AST parsing, checkpoint sentinel, and basic GoA health check logic are fully functional.

4. **Verify AWS ECR In-Region Free Egress Policy**:
   - Reference: Official AWS ECR Pricing Documentation (`https://aws.amazon.com/ecr/pricing/`).
   - "Data transferred between Amazon ECR and other services within the same region (for example, Amazon EC2, AWS Lambda, Amazon ECS, or Amazon EKS) is free."

---
*End of Rover Slim Enterprise Architecture Specification, Adversarial Critique, and MoSCoW Plan.*
