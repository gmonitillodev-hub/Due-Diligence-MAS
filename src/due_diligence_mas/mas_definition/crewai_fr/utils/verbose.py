import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

VerboseScope = Literal["agent", "crew", "flow"]


def is_verbose(scope: VerboseScope) -> bool:
    """Verbosity of agents, crews or flows, from AGENT_VERBOSE, CREW_VERBOSE or FLOW_VERBOSE (default: true)."""
    return os.getenv(f"{scope.upper()}_VERBOSE", "true").strip().lower() in ("1", "true", "yes", "on")
