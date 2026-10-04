"""
Rover-Slim: Autonomous Container Optimization, AST Dependency Segregation,
and Green-on-Arrival (GoA) Sentinel Verification Engine.
"""

__version__ = "1.1.0"

from rover_slim.models import RoverSlimConfig, OptimizationReport
from rover_slim.core.engine import RoverSlimEngine
from rover_slim.parsers.ast_parser import ASTDependencyParser
from rover_slim.parsers.req_parser import RequirementsParser
from rover_slim.synthesizers.multistage import MultiStageSynthesizer
from rover_slim.verifiers.goa_sentinel import GoASentinelVerifier

__all__ = [
    "__version__",
    "RoverSlimConfig",
    "OptimizationReport",
    "RoverSlimEngine",
    "ASTDependencyParser",
    "RequirementsParser",
    "MultiStageSynthesizer",
    "GoASentinelVerifier"
]
