from __future__ import annotations

import logging

from .router import Router
from .llm.base import Reasoner
from .schemas import Intent, TicketResult, ToolResult
from .tools import ToolRegistry

logger = logging.getLogger(__name__)


# the main chain. analyse -> run tools -> compose. also keep the steps log
class SupportOrchestrator:
    def __init__(self, router: Router, reasoner: Reasoner,
                 registry: ToolRegistry) -> None:
        self.router = router
        self.reasoner = reasoner
        self.registry = registry

    def process(self, email_text: str) -> TicketResult:
        steps: list[str] = []

        # step 1: analyse
        plan = self.router.plan(email_text)
        if plan.needs_translation:
            steps.append(
                f"Detected non-English email (language='{plan.detected_language}'); "
                "would translate before processing."
            )
        depts = ", ".join(sorted({str(i.department) for i in plan.intents})) or "none"
        steps.append(
            f"Analysed email and detected {len(plan.intents)} request(s) "
            f"across department(s): {depts}."
        )

        # step 2: run the tools, one per intent
        tool_results: list[ToolResult] = []
        for intent in plan.intents:
            result = self._execute_intent(intent, steps)
            if result is not None:
                tool_results.append(result)

        # step 3: write the final reply
        if tool_results or plan.intents:
            final = self.reasoner.compose(email_text, plan, tool_results)
            steps.append(
                f"Composed a unified reply from {len(tool_results)} tool result(s)."
            )
        else:
            # nothing found, ask the customer for more
            final = (
                "Hello,\n\nThank you for your message. We were not able to "
                "identify a specific request — could you tell us a little more "
                "about how we can help?\n\nBest regards,\nCustomer Support Team"
            )
            steps.append("No actionable request detected; asked the customer to clarify.")

        return TicketResult(
            original_text=email_text,
            processing_steps=steps,
            final_response=final,
            plan=plan,
            tool_results=tool_results,
        )

    # one intent -> find its tool, get the args, call it
    def _execute_intent(self, intent: Intent, steps: list[str]) -> ToolResult | None:
        tool = self.registry.tool_for_department(intent.department)
        if tool is None:
            steps.append(f"No tool available for department '{intent.department}'.")
            return None

        # take the args the tool need from the intent
        kwargs = {arg: getattr(intent, arg, None) for arg in tool.schema}
        missing = [arg for arg, val in kwargs.items() if val in (None, "")]

        if missing:
            # we dont have the arg so we cant call
            steps.append(
                f"[{intent.department}] Need {', '.join(missing)} for "
                f"'{tool.name}' but it was not found in the email."
            )
            return ToolResult(
                tool=tool.name, args=kwargs, output=None, ok=False,
                error=f"Missing required argument(s): {', '.join(missing)}",
            )

        result = self.registry.call(tool.name, **kwargs)
        arg_desc = ", ".join(f"{k}={v!r}" for k, v in kwargs.items()) or "no args"
        status = "ok" if result.ok else f"error: {result.error}"
        steps.append(f"[{intent.department}] Called {tool.name}({arg_desc}) -> {status}.")
        return result
