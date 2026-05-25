from __future__ import annotations

import abc

from .. schemas import RoutingPlan, ToolResult


# base for the reasoner. has 2 jobs: analyse and compose
class Reasoner(abc.ABC):
    name: str = "reasoner"

    @abc.abstractmethod
    def analyse(self, email_text: str) -> RoutingPlan:
        raise NotImplementedError

    @abc.abstractmethod
    def compose(
        self,
        original_text: str,
        plan: RoutingPlan,
        tool_results: list[ToolResult],
    ) -> str:
        raise NotImplementedError
