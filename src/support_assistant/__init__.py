# customer support assistant. read email -> route -> call tools -> write reply

from .config import Settings, build_orchestrator, build_reasoner
from .orchestrator import SupportOrchestrator
from .schemas import Department, Intent, RoutingPlan, TicketResult, ToolResult

__all__ = [
    "Settings",
    "build_orchestrator",
    "build_reasoner",
    "SupportOrchestrator",
    "Department",
    "Intent",
    "RoutingPlan",
    "TicketResult",
    "ToolResult",
]

__version__ = "0.1.0"
