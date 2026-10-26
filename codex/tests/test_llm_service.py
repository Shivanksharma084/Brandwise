"""Unit tests for LLM Retrieval-Grounded Judgment Service."""

import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.llm_service import LLMReviewService


def test_mock_semantic_evaluation():
    service = LLMReviewService()
    sample_text = "Hey guys! Our new cream cures acne in 7 days."

    rules = [{"clause_ref": "§2.1", "title": "Tone", "description": "Professional tone"}]
    facts = [{"statistic": "Acne reduction", "value": "Helps reduce appearance", "owner": "Legal", "valid_until": "2027-01-01"}]

    findings = service.evaluate_content_semantic(sample_text, rules, facts, channel="social")

    assert len(findings) >= 2, f"Expected at least 2 findings, got {len(findings)}"

    categories = [f.category for f in findings]
    assert "tone" in categories or "claim" in categories
    print("[PASS] test_mock_semantic_evaluation")


if __name__ == "__main__":
    print("Running LLM service unit tests...")
    test_mock_semantic_evaluation()
    print("ALL LLM SERVICE TESTS PASSED SUCCESSFULLY! 🚀")
