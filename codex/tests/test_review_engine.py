"""Unit test for the Deterministic Review Engine."""

import sys
import os

# Add backend to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.review_engine import deterministic_engine, DeterministicReviewEngine


def test_superlatives_detection():
    engine = DeterministicReviewEngine()
    sample_text = "Our formula is India's #1 skincare solution and cures acne in 7 days!"
    findings = engine.check_superlatives_and_claims(sample_text)

    assert len(findings) >= 2, f"Expected at least 2 findings, got {len(findings)}"

    categories = [f.category for f in findings]
    severities = [f.severity for f in findings]

    assert "claim" in categories
    assert "high" in severities
    print("[PASS] test_superlatives_detection")


def test_banned_terminology():
    engine = DeterministicReviewEngine()
    sample_terms = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "term": "crazy deal",
            "status": "banned",
            "preferred_alternative": "special offer",
            "notes": "Slang is prohibited in brand voice",
        }
    ]
    sample_text = "Grab this crazy deal right now!"
    findings = engine.check_terminology(sample_text, sample_terms)

    assert len(findings) == 1
    assert findings[0].highlighted_text == "crazy deal"
    assert findings[0].suggested_fix == "special offer"
    print("[PASS] test_banned_terminology")


def test_disclosure_check():
    engine = DeterministicReviewEngine()
    sample_text = "Check out our new summer line! Use code SUMMER20 for a discount. Link in bio!"
    findings = engine.check_disclosures(sample_text, channel="social")

    assert len(findings) == 1
    assert findings[0].category == "disclaimer"
    print("[PASS] test_disclosure_check")


def test_readability():
    engine = DeterministicReviewEngine()
    sample_text = "This is a simple sentence. We love clean code. It works well."
    metrics = engine.calculate_readability(sample_text)

    assert "reading_ease" in metrics
    assert "grade_level" in metrics
    assert metrics["grade_level"] <= 8.0
    print("[PASS] test_readability")


def test_contrast_ratio():
    engine = DeterministicReviewEngine()
    # Pure black (#000000) on white (#FFFFFF) is 21.0
    ratio = engine.calculate_contrast_ratio("#000000", "#FFFFFF")
    assert ratio >= 20.0

    # Light grey on white should fail WCAG AA (4.5)
    low_ratio = engine.calculate_contrast_ratio("#D1D5DB", "#FFFFFF")
    assert low_ratio < 4.5
    print("[PASS] test_contrast_ratio")


if __name__ == "__main__":
    print("Running DeterministicReviewEngine tests...")
    test_superlatives_detection()
    test_banned_terminology()
    test_disclosure_check()
    test_readability()
    test_contrast_ratio()
    print("ALL TESTS PASSED SUCCESSFULLY! 🚀")
