from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# the 3 departments
class Department(str, Enum):
    SALES = "sales"
    TECHNICAL = "technical"
    FINANCIAL = "financial"

    def __str__(self) -> str:
        return self.value


# one request inside the email
class Intent(BaseModel):
    department: Department = Field(description="which department")
    summary: str = Field(description="short sentence about the request")
    # only fill if customer say it
    order_id: Optional[str] = Field(default=None, description="order number or null")
    product_name: Optional[str] = Field(default=None, description="product name or null")


# what the router give back
class RoutingPlan(BaseModel):
    detected_language: str = Field(default="en", description="lang code")
    needs_translation: bool = Field(default=False, description="true if not english")
    intents: list[Intent] = Field(default_factory=list, description="all requests")


# result of calling one tool
class ToolResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    ok: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "tool": self.tool, "args": self.args, "ok": self.ok, "output": self.output
        }
        if self.error:
            d["error"] = self.error
        return d


# final result. need this 3 keys for the output
class TicketResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_text: str
    processing_steps: list[str] = Field(default_factory=list)
    final_response: str = ""
    # extra stuff for debug, not in the required output
    plan: Optional[RoutingPlan] = None
    tool_results: list[ToolResult] = Field(default_factory=list)

    def to_dict(self, *, include_debug: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "original_text": self.original_text,
            "processing_steps": self.processing_steps,
            "final_response": self.final_response,
        }
        if include_debug:
            out["_debug"] = {
                "plan": self.plan.model_dump(mode="json") if self.plan else None,
                "tool_results": [t.to_dict() for t in self.tool_results],
            }
        return out
