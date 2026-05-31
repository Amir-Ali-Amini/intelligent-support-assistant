# tests for the offline router (keywords + entity extract)

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from support_assistant.llm.rule_based import RuleBasedReasoner  # noqa: E402
from support_assistant.schemas import Department  # noqa: E402
from examples.sample_emails import MULTI_INTENT, ORDER_ONLY, VAGUE  # noqa: E402


class TestRuleBasedRouting(unittest.TestCase):
    def setUp(self):
        self.reasoner = RuleBasedReasoner()

    def test_multi_intent_detects_three_departments(self):
        # the big email should hit all 3
        plan = self.reasoner.analyse(MULTI_INTENT)
        depts = {i.department for i in plan.intents}
        self.assertEqual(
            depts,
            {Department.SALES, Department.TECHNICAL, Department.FINANCIAL},
        )

    def test_extracts_order_id(self):
        plan = self.reasoner.analyse(MULTI_INTENT)
        sales = next(i for i in plan.intents if i.department == Department.SALES)
        self.assertEqual(sales.order_id, "12345")

    def test_extracts_product_name(self):
        plan = self.reasoner.analyse(MULTI_INTENT)
        tech = next(i for i in plan.intents if i.department == Department.TECHNICAL)
        self.assertEqual(tech.product_name, "Aurora Smartwatch")

    def test_order_only_single_intent(self):
        plan = self.reasoner.analyse(ORDER_ONLY)
        self.assertEqual(len(plan.intents), 1)
        self.assertEqual(plan.intents[0].department, Department.SALES)
        self.assertEqual(plan.intents[0].order_id, "98765")

    def test_vague_email_no_intents(self):
        # no keywords -> nothing
        plan = self.reasoner.analyse(VAGUE)
        self.assertEqual(plan.intents, [])


if __name__ == "__main__":
    unittest.main()
