# tests for the mock tools and the registry

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from support_assistant.tools import build_default_registry  # noqa: E402
from support_assistant.tools import mock_apis  # noqa: E402
from support_assistant.schemas import Department  # noqa: E402


class TestMockApis(unittest.TestCase):
    def test_known_order(self):
        out = mock_apis.get_order_status("12345")
        self.assertEqual(out["status"], "in_transit")
        self.assertEqual(out["order_id"], "12345")

    def test_order_strips_hash(self):
        # should remove the # too
        out = mock_apis.get_order_status("#98765")
        self.assertEqual(out["order_id"], "98765")
        self.assertEqual(out["status"], "delivered")

    def test_unknown_order(self):
        out = mock_apis.get_order_status("00000")
        self.assertEqual(out["status"], "unknown")

    def test_product_case_insensitive(self):
        out = mock_apis.get_product_info("aurora smartwatch")
        self.assertEqual(out["category"], "wearable")

    def test_refund_policy_no_args(self):
        out = mock_apis.get_refund_policy()
        self.assertIn("30 days", out["policy"])
        self.assertEqual(out["window_days"], 30)


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = build_default_registry()

    def test_all_three_registered(self):
        names = {t.name for t in self.registry.all()}
        self.assertEqual(
            names,
            {"get_order_status", "get_product_info", "get_refund_policy"},
        )

    def test_department_mapping(self):
        self.assertEqual(
            self.registry.tool_for_department(Department.SALES).name,
            "get_order_status",
        )

    def test_call_captures_unknown_tool(self):
        result = self.registry.call("does_not_exist")
        self.assertFalse(result.ok)
        self.assertIn("Unknown tool", result.error)


if __name__ == "__main__":
    unittest.main()
