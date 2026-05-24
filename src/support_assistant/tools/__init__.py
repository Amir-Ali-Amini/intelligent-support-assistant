from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..schemas import Department, ToolResult
from . import mock_apis


# one tool. schema say what args it need
@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]
    department: Department
    schema: dict[str, str]


# keep all tools and call them by name
class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def tool_for_department(self, department: Department) -> Tool | None:
        for tool in self._tools.values():
            if tool.department == department:
                return tool
        return None

    # call by name. catch error so it dont crash all
    def call(self, name: str, **kwargs: Any) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                tool=name, args=kwargs, output=None, ok=False,
                error=f"Unknown tool: {name!r}",
            )
        try:
            output = tool.fn(**kwargs)
            return ToolResult(tool=name, args=kwargs, output=output, ok=True)
        except Exception as exc:
            return ToolResult(
                tool=name, args=kwargs, output=None, ok=False, error=str(exc),
            )


# make the 3 tools
def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Tool(
        name="get_order_status",
        description="Look up the delivery status of an order by its id.",
        fn=mock_apis.get_order_status,
        department=Department.SALES,
        schema={"order_id": "The order number, e.g. '12345'."},
    ))
    registry.register(Tool(
        name="get_product_info",
        description="Return technical specifications for a product by name.",
        fn=mock_apis.get_product_info,
        department=Department.TECHNICAL,
        schema={"product_name": "The product the customer is asking about."},
    ))
    registry.register(Tool(
        name="get_refund_policy",
        description="Return the company's refund / return policy.",
        fn=mock_apis.get_refund_policy,
        department=Department.FINANCIAL,
        schema={},  # no args
    ))
    return registry
