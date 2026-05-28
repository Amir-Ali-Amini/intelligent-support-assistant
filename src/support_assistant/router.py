from __future__ import annotations

from .llm.base import Reasoner
from .schemas import RoutingPlan
from .tools import ToolRegistry


# the router. ask the reasoner to read the email, then keep only intents
# that we have a tool for
class Router:
    def __init__(self, reasoner: Reasoner, registry: ToolRegistry) -> None:
        self.reasoner = reasoner
        self.registry = registry

    def plan(self, email_text: str) -> RoutingPlan:
        raw_plan = self.reasoner.analyse(email_text)
        # drop intent if no tool exist for it
        valid = [
            intent for intent in raw_plan.intents
            if self.registry.tool_for_department(intent.department) is not None
        ]
        raw_plan.intents = valid
        return raw_plan
