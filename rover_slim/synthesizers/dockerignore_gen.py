from rover_slim.parsers.context_shield import ContextShield

class DockerignoreGenerator:
    """Helper wrapper to generate and write hardened .dockerignore."""

    def __init__(self, root_dir: str):
        self.shield = ContextShield(root_dir)

    def generate(self, custom_rules: list = None) -> str:
        return self.shield.generate_dockerignore(custom_rules)

    def write(self, output_path: str = None, force: bool = False):
        return self.shield.write_dockerignore(output_path, force=force)
