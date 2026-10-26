"""
Visual and accessibility checkers for images and layout assets.
Checks:
1. Missing alt text for images
2. WCAG 2.2 color contrast against brand palette
3. Image dimensions & aspect ratio verification
"""

import math
from typing import Any
from app.core.review_engine import FindingCandidate, deterministic_engine


class VisualAccessibilityChecker:
    """Checks image and visual layout assets against brand design system & WCAG standards."""

    @staticmethod
    def check_image_accessibility(
        file_path: str | None,
        alt_text: str | None,
        context: str = "social_post"
    ) -> list[FindingCandidate]:
        """Check image metadata for missing accessibility alternative text."""
        findings: list[FindingCandidate] = []

        if file_path and (not alt_text or not alt_text.strip()):
            findings.append(
                FindingCandidate(
                    category="accessibility",
                    severity="medium",
                    explanation="Image asset is missing descriptive alternative text (alt text) for screen readers.",
                    source_ref="WCAG 2.2 §1.1.1 (Non-text Content)",
                    confidence=1.0,
                    suggested_fix="Provide a concise description of the image content and visual elements."
                )
            )

        return findings

    @staticmethod
    def check_palette_contrast(
        text_color_hex: str,
        background_color_hex: str,
        is_large_text: bool = False
    ) -> list[FindingCandidate]:
        """Verify text-to-background contrast ratio meets WCAG AA standards."""
        findings: list[FindingCandidate] = []
        ratio = deterministic_engine.calculate_contrast_ratio(text_color_hex, background_color_hex)
        threshold = 3.0 if is_large_text else 4.5

        if ratio < threshold:
            findings.append(
                FindingCandidate(
                    category="accessibility",
                    severity="medium",
                    explanation=f"Color contrast ratio of {ratio}:1 fails WCAG 2.2 AA minimum standard ({threshold}:1).",
                    source_ref=f"WCAG 2.2 §1.4.3 (Contrast Minimum - {threshold}:1 target)",
                    confidence=1.0,
                    suggested_fix=f"Darken the text color or lighten the background to reach at least {threshold}:1."
                )
            )

        return findings


visual_checker = VisualAccessibilityChecker()
