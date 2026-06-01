# end to end test of the whole pipeline (offline)

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from support_assistant.config import build_orchestrator, Settings  # noqa: E402
from examples.sample_emails import MULTI_INTENT, VAGUE  # noqa: E402


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # force offline so no api key needed
        self.orch = build_orchestrator(Settings(llm_model=None))

    def test_output_contract_keys(self):
        # must be exactly these 3 keys
        result = self.orch.process(MULTI_INTENT).to_dict()
        self.assertEqual(
            set(result.keys()),
            {"original_text", "processing_steps", "final_response"},
        )

    def test_original_text_preserved(self):
        result = self.orch.process(MULTI_INTENT).to_dict()
        self.assertEqual(result["original_text"], MULTI_INTENT)

    def test_processing_steps_record_all_tool_calls(self):
        result = self.orch.process(MULTI_INTENT).to_dict()
        joined = " ".join(result["processing_steps"])
        self.assertIn("get_order_status", joined)
        self.assertIn("get_product_info", joined)
        self.assertIn("get_refund_policy", joined)

    def test_final_response_mentions_gathered_facts(self):
        result = self.orch.process(MULTI_INTENT).to_dict()
        reply = result["final_response"].lower()
        self.assertIn("12345", reply)
        self.assertIn("refund", reply)

    def test_vague_email_asks_for_clarification(self):
        result = self.orch.process(VAGUE).to_dict()
        self.assertIn("more", result["final_response"].lower())


if __name__ == "__main__":
    unittest.main()
