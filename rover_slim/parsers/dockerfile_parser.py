import os
import re
from typing import List, Dict, Any, Optional

class DockerfileInstruction:
    def __init__(self, instruction: str, arguments: str, line_number: int):
        self.instruction = instruction.upper()
        self.arguments = arguments
        self.line_number = line_number

    def __repr__(self):
        return f"<DockerfileInstruction {self.instruction} {self.arguments[:30]}>"

class DockerfileAnalysis:
    def __init__(self):
        self.is_multistage: bool = False
        self.stages: List[Dict[str, Any]] = []
        self.base_images: List[str] = []
        self.exposed_ports: List[int] = []
        self.has_apt_clean: bool = False
        self.has_no_cache_pip: bool = False
        self.copies_root_context: bool = False
        self.runs_as_root: bool = True
        self.warnings: List[str] = []
        self.entrypoint: Optional[str] = None
        self.cmd: Optional[str] = None

class DockerfileParser:
    """Parses Dockerfiles to extract structural metadata, stage definitions, and hygiene warnings."""

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath

    def parse(self, content: Optional[str] = None) -> DockerfileAnalysis:
        analysis = DockerfileAnalysis()
        if content is None and self.filepath and os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read()
        
        if not content:
            return analysis

        instructions: List[DockerfileInstruction] = []
        lines = content.splitlines()
        
        current_inst = ""
        current_args = ""
        start_line = 1

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if current_inst:
                if stripped.endswith("\\"):
                    current_args += " " + stripped[:-1].strip()
                else:
                    current_args += " " + stripped
                    instructions.append(DockerfileInstruction(current_inst, current_args.strip(), start_line))
                    current_inst = ""
                    current_args = ""
            else:
                match = re.match(r"^([A-Z_]+)\s+(.*)$", stripped, re.IGNORECASE)
                if match:
                    inst = match.group(1).upper()
                    args = match.group(2).strip()
                    if args.endswith("\\"):
                        current_inst = inst
                        current_args = args[:-1].strip()
                        start_line = idx
                    else:
                        instructions.append(DockerfileInstruction(inst, args, idx))

        from_count = 0
        for inst in instructions:
            if inst.instruction == "FROM":
                from_count += 1
                base_img = inst.arguments.split()[0]
                analysis.base_images.append(base_img)
                analysis.stages.append({"stage_index": from_count, "from": inst.arguments})
            elif inst.instruction == "EXPOSE":
                ports = re.findall(r"\d+", inst.arguments)
                for p in ports:
                    try:
                        analysis.exposed_ports.append(int(p))
                    except ValueError:
                        pass
            elif inst.instruction == "USER":
                if inst.arguments.strip() not in ["0", "root"]:
                    analysis.runs_as_root = False
            elif inst.instruction == "CMD":
                analysis.cmd = inst.arguments
            elif inst.instruction == "ENTRYPOINT":
                analysis.entrypoint = inst.arguments
            elif inst.instruction == "RUN":
                if "apt-get" in inst.arguments:
                    if "rm -rf /var/lib/apt/lists" in inst.arguments:
                        analysis.has_apt_clean = True
                    else:
                        analysis.warnings.append("apt-get cache not cleaned (missing 'rm -rf /var/lib/apt/lists/*')")
                if "pip install" in inst.arguments:
                    if "--no-cache-dir" in inst.arguments:
                        analysis.has_no_cache_pip = True
                    else:
                        analysis.warnings.append("pip install cache not disabled (missing '--no-cache-dir')")
            elif inst.instruction == "COPY" or inst.instruction == "ADD":
                if inst.arguments.strip().startswith(". .") or inst.arguments.strip().startswith("./ ./"):
                    analysis.copies_root_context = True

        analysis.is_multistage = from_count > 1
        if not analysis.is_multistage:
            analysis.warnings.append("Single-stage build detected. Build tools and headers are likely retained in final image.")
        if analysis.runs_as_root:
            analysis.warnings.append("Container runs as root user. Recommended: add non-privileged user (appuser).")

        return analysis
