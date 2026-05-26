from __future__ import annotations

import re

from .base import Reasoner
from ..schemas import Department, Intent, RoutingPlan, ToolResult

# offline version. no internet, just keywords and regex. used in tests too

# words that hint each department
_SALES_CUES = (
    "order",
    "track",
    "tracking",
    "shipment",
    "shipping",
    "delivery",
    "delivered",
    "package",
    "dispatch",
    "where is my",
    "status of my",
)
_TECHNICAL_CUES = (
    "how do i",
    "how to",
    "feature",
    "spec",
    "specs",
    "specification",
    "battery",
    "connect",
    "pair",
    "setup",
    "set up",
    "install",
    "warranty",
    "not working",
    "doesn't work",
    "technical",
    "manual",
)
_FINANCIAL_CUES = (
    "refund",
    "return",
    "money back",
    "reimburse",
    "billing",
    "charge",
    "charged",
    "invoice",
    "payment",
    "cancel my order and get",
)

_ORDER_NEAR_RE = re.compile(
    r"order(?:\s*(?:number|no\.?|#|id)?)?\s*[:#]?\s*#?(\d{4,})", re.IGNORECASE
)
_ORDER_ANY_RE = re.compile(r"#(\d{4,})")
_KNOWN_PRODUCTS = ("Thunder X1 Headphones", "Aurora Smartwatch")


def _contains_any(text: str, cues: tuple[str, ...]) -> bool:
    return any(cue in text for cue in cues)


# find order id in the text
def _extract_order_id(text: str) -> str | None:
    m = _ORDER_NEAR_RE.search(text) or _ORDER_ANY_RE.search(text)
    return m.group(1) if m else None


# find product name
def _extract_product(text: str) -> str | None:
    lowered = text.lower()
    for product in _KNOWN_PRODUCTS:
        if product.lower() in lowered:
            return product
    return None


class RuleBasedReasoner(Reasoner):
    name = "rule_based"

    def analyse(self, email_text: str) -> RoutingPlan:
        text = email_text.lower()
        intents: list[Intent] = []

        if _contains_any(text, _SALES_CUES):
            intents.append(
                Intent(
                    department=Department.SALES,
                    summary="Customer is asking about the status of an order.",
                    order_id=_extract_order_id(email_text),
                )
            )
        if _contains_any(text, _TECHNICAL_CUES):
            intents.append(
                Intent(
                    department=Department.TECHNICAL,
                    summary="Customer has a technical / product question.",
                    product_name=_extract_product(email_text),
                )
            )
        if _contains_any(text, _FINANCIAL_CUES):
            intents.append(
                Intent(
                    department=Department.FINANCIAL,
                    summary="Customer is asking about refunds / returns.",
                )
            )

        return RoutingPlan(intents=intents, detected_language="en")

    # build the reply text from the tool results
    def compose(
        self,
        original_text: str,
        plan: RoutingPlan,
        tool_results: list[ToolResult],
    ) -> str:
        by_tool = {r.tool: r for r in tool_results if r.ok}
        parts: list[str] = [
            "Hello,",
            "",
            "Thank you for reaching out. " "Here is everything you asked about:",
        ]

        order = by_tool.get("get_order_status")
        if order:
            o = order.output
            status = str(o.get("status", "unknown")).replace("_", " ")
            line = (
                f"\n• Order #{o.get('order_id')}: your order is currently *{status}*."
            )
            if o.get("carrier"):
                line += f" It is being handled by {o['carrier']}."
            if o.get("eta_days"):
                line += f" Estimated delivery in about {o['eta_days']} day(s)."
            if o.get("delivered_on"):
                line += f" It was delivered on {o['delivered_on']}."
            parts.append(line)

        product = by_tool.get("get_product_info")
        if product:
            p = product.output
            line = f"\n• Regarding {p.get('product_name')}:"
            if p.get("note"):
                line += f" {p['note']}"
            details = []
            if p.get("battery_life_hours"):
                details.append(f"battery life ~{p['battery_life_hours']}h")
            if p.get("connectivity"):
                details.append(f"connectivity: {p['connectivity']}")
            if p.get("warranty_months"):
                details.append(f"{p['warranty_months']}-month warranty")
            if details:
                line += " (" + "; ".join(details) + ")."
            parts.append(line)

        refund = by_tool.get("get_refund_policy")
        if refund:
            parts.append(f"\n• Refund policy: {refund.output.get('policy')}")

        # only greeting was added -> we didnt find anything
        if len(parts) == 3:
            parts.append(
                "\nCould you share a few more details so we can help " "you further?"
            )

        parts += [
            "",
            "If there is anything else we can help with, just reply " "to this email.",
            "",
            "Best regards,",
            "Customer Support Team",
        ]
        return "\n".join(parts)
