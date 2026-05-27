from __future__ import annotations

from .base import Reasoner
from . import prompts
from ..schemas import RoutingPlan, ToolResult


# llm version. use litellm so we can change provider easy, and instructor to
# get the output validated into pydantic
class LLMReasoner(Reasoner):
    name = "llm"

    def __init__(self, model: str, api_base: str | None = None,
                 api_key: str | None = None, max_retries: int = 2) -> None:
        # import here so the offline mode dont need this libs
        import instructor
        from litellm import completion

        self.model = model
        self.max_retries = max_retries
        # only pass these if they are set
        self._extra = {k: v for k, v in
                       {"api_base": api_base, "api_key": api_key}.items()
                       if v}
        self._completion = completion
        self._client = instructor.from_litellm(completion)

    # ask llm and get a RoutingPlan back (instructor validate + retry)
    def analyse(self, email_text: str) -> RoutingPlan:
        return self._client.chat.completions.create(
            model=self.model,
            response_model=RoutingPlan,
            max_retries=self.max_retries,
            messages=[
                {"role": "system", "content": prompts.ANALYSE_SYSTEM},
                {"role": "user",
                 "content": prompts.ANALYSE_USER.format(email=email_text)},
            ],
            **self._extra,
        )

    # just text here, no schema needed
    def compose(
        self,
        original_text: str,
        plan: RoutingPlan,
        tool_results: list[ToolResult],
    ) -> str:
        import json
        facts = json.dumps(
            [r.to_dict() for r in tool_results if r.ok], indent=2, ensure_ascii=False
        )
        resp = self._completion(
            model=self.model,
            messages=[
                {"role": "system", "content": prompts.COMPOSE_SYSTEM},
                {"role": "user", "content": prompts.COMPOSE_USER.format(
                    original=original_text, facts=facts)},
            ],
            temperature=0.3,
            **self._extra,
        )
        return resp.choices[0].message.content.strip()
