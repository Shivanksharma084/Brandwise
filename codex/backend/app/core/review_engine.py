"""
Deterministic brand governance rules engine.

Performs fast, reproducible, and explainable rule checks without calling an LLM:
1. Terminology checks (banned terms, preferred alternatives)
2. Superlatives and unsubstantiated claims detection (#1, best, cure, guaranteed)
3. Required regulatory disclosures (e.g. #ad, #sponsored, statutory warnings)
4. Reading level assessment (Flesch-Kincaid readability / grade level)
5. Visual and accessibility checks (contrast ratio calculation, missing alt-text)
"""

import re
import math
from typing import Any
from dataclasses import dataclass, field


@dataclass
class FindingCandidate:
    category: str
    severity: str
    explanation: str
    source_ref: str
    confidence: float
    span_start: int | None = None
    span_end: int | None = None
    highlighted_text: str | None = None
    suggested_fix: str | None = None
    rule_id: str | None = None


class DeterministicReviewEngine:
    """Engine executing deterministic, non-LLM checks on submitted copy."""

    # Default regex patterns for common regulatory and superlative checks
    SUPERLATIVE_PATTERNS = [
        (
            re.compile(r"(?:^|[^\w])(#1|number\s*one|no\.\s*1)\b", re.IGNORECASE),
            "High",
            "Unsupported superlative claim '#1' requires a verified fact entry with source and expiry.",
            "Guideline §3.2 (Claim Verification)",
            "Consider qualifying with survey year or category, e.g., 'One of top rated in 2025'"
        ),
        (
            re.compile(r"\b(100%|guaranteed|cures?|eliminates?|permanent(?:ly)?)\b", re.IGNORECASE),
            "High",
            "Absolute efficacy or cure claim detected. Prohibited under advertising & health standards.",
            "Guideline §4.2 (Health & Regulated Claims)",
            "Use measured language such as 'helps reduce' or 'formulated to support'"
        ),
        (
            re.compile(r"\b(cheapest|lowest price|best in india|world'?s best)\b", re.IGNORECASE),
            "Medium",
            "Comparative superlative claim requires registered market data validation.",
            "Guideline §3.4 (Comparative Claims)",
            "State explicit basis of comparison or cite current audited report"
        ),
    ]

    DISCLOSURE_PATTERNS = [
        # Paid collaboration / Influencer rules (ASCI compliance)
        (
            "ad_disclosure",
            re.compile(r"\b(#ad|#sponsored|#collab|#paidpartner)\b", re.IGNORECASE),
            "High",
            "Missing prominent commercial disclosure tag (#ad / #sponsored).",
            "ASCI Influencer Guidelines §1.1",
            "Add '#ad' or '#sponsored' prominently at the start of your caption."
        )
    ]

    def check_terminology(
        self,
        text: str,
        terminology_entries: list[dict[str, Any]]
    ) -> list[FindingCandidate]:
        """
        Check content against approved and banned terminology list.
        Each entry has: term, status ('banned', 'preferred'), preferred_alternative.
        """
        findings: list[FindingCandidate] = []
        if not text:
            return findings

        for item in terminology_entries:
            term = item.get("term", "").strip()
            if not term:
                continue

            status = item.get("status", "").lower()
            alt = item.get("preferred_alternative")
            notes = item.get("notes") or ""

            # Word boundary regex search
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                start, end = match.span()
                matched_str = match.group(0)

                if status == "banned":
                    fix_suggestion = f"Replace '{matched_str}' with '{alt}'" if alt else f"Remove '{matched_str}'"
                    findings.append(
                        FindingCandidate(
                            category="terminology",
                            severity="high",
                            span_start=start,
                            span_end=end,
                            highlighted_text=matched_str,
                            explanation=f"Banned term '{matched_str}' detected. {notes}".strip(),
                            source_ref=f"Brand Terminology Register (Term: {term})",
                            confidence=1.0,
                            suggested_fix=alt if alt else fix_suggestion,
                            rule_id=str(item.get("id", "")) or None
                        )
                    )
                elif status == "preferred" and alt and matched_str.lower() != alt.lower():
                    # If this is a deprecated variant of the preferred term
                    findings.append(
                        FindingCandidate(
                            category="terminology",
                            severity="medium",
                            span_start=start,
                            span_end=end,
                            highlighted_text=matched_str,
                            explanation=f"Preferred brand term is '{alt}' instead of '{matched_str}'.",
                            source_ref=f"Brand Terminology Register (Term: {term})",
                            confidence=0.95,
                            suggested_fix=alt,
                            rule_id=str(item.get("id", "")) or None
                        )
                    )

        return findings

    def check_superlatives_and_claims(self, text: str) -> list[FindingCandidate]:
        """Detect unsubstantiated superlatives and time-bound cure promises."""
        findings: list[FindingCandidate] = []
        if not text:
            return findings

        for regex, severity, explanation, source_ref, fix in self.SUPERLATIVE_PATTERNS:
            for match in regex.finditer(text):
                # If there's a capture group, use its span and content for cleaner highlights
                if match.groups() and match.group(1):
                    start, end = match.span(1)
                    highlight = match.group(1)
                else:
                    start, end = match.span()
                    highlight = match.group(0)

                findings.append(
                    FindingCandidate(
                        category="claim",
                        severity=severity.lower(),
                        span_start=start,
                        span_end=end,
                        highlighted_text=highlight,
                        explanation=explanation,
                        source_ref=source_ref,
                        confidence=0.92,
                        suggested_fix=fix
                    )
                )
        return findings

    def check_disclosures(self, text: str, channel: str | None = None) -> list[FindingCandidate]:
        """Check for mandatory influencer and statutory disclosures when channel is social or ad."""
        findings: list[FindingCandidate] = []
        if not text:
            return findings

        # Check if text appears to be a promotional/collaboration post
        is_promo = bool(re.search(r"\b(discount|code|collab|use code|buy now|link in bio)\b", text, re.IGNORECASE))
        has_disclosure = any(
            re.search(r"\b(#ad|#sponsored|#collab|#paidpartner)\b", text, re.IGNORECASE)
            for _ in [1]
        )

        if is_promo and not has_disclosure and channel in ["social", "instagram", "tiktok", "youtube", None]:
            findings.append(
                FindingCandidate(
                    category="disclaimer",
                    severity="high",
                    span_start=0,
                    span_end=min(len(text), 30),
                    highlighted_text=text[:30] + "...",
                    explanation="Promotional commercial post detected without required ASCI/FTC disclosure hashtag.",
                    source_ref="ASCI Influencer Code 2025 §1.1",
                    confidence=0.90,
                    suggested_fix="Add '#ad' or '#sponsored' at the beginning of the caption."
                )
            )

        return findings

    def calculate_readability(self, text: str) -> dict[str, Any]:
        """
        Calculates Flesch Reading Ease and Flesch-Kincaid Grade Level.
        Ensures content meets typical brand accessibility targets (grade 6-8).
        """
        words = re.findall(r"\b[a-zA-Z]+\b", text)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]

        word_count = len(words)
        sentence_count = max(len(sentences), 1)

        if word_count == 0:
            return {"reading_ease": 100.0, "grade_level": 0.0, "reading_category": "Easy"}

        # Syllable counter heuristic
        def count_syllables(word: str) -> int:
            word = word.lower()
            count = len(re.findall(r"[aeiouy]+", word))
            if word.endswith("e") and not word.endswith("le"):
                count = max(1, count - 1)
            return max(1, count)

        syllable_count = sum(count_syllables(w) for w in words)

        # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        asl = word_count / sentence_count
        asw = syllable_count / word_count
        reading_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
        reading_ease = max(0.0, min(100.0, round(reading_ease, 1)))

        # Flesch-Kincaid Grade: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
        grade_level = (0.39 * asl) + (11.8 * asw) - 15.59
        grade_level = max(1.0, round(grade_level, 1))

        category = "Standard"
        if reading_ease >= 70:
            category = "Easy / Conversational"
        elif reading_ease <= 40:
            category = "Complex / Academic"

        return {
            "reading_ease": reading_ease,
            "grade_level": grade_level,
            "category": category,
            "word_count": word_count,
            "sentence_count": sentence_count,
        }

    @staticmethod
    def calculate_contrast_ratio(fg_hex: str, bg_hex: str) -> float:
        """
        Calculates WCAG 2.2 color contrast ratio between two hex colors.
        Returns a float between 1.0 and 21.0. Minimum AA ratio for normal text is 4.5.
        """
        def hex_to_relative_luminance(hex_code: str) -> float:
            hex_code = hex_code.lstrip("#")
            if len(hex_code) == 3:
                hex_code = "".join([c * 2 for c in hex_code])
            r, g, b = [int(hex_code[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

            def adjust(c: float) -> float:
                return c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4)

            return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

        l1 = hex_to_relative_luminance(fg_hex)
        l2 = hex_to_relative_luminance(bg_hex)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        return round(ratio, 2)

    def run_all(
        self,
        text: str,
        terminology_entries: list[dict[str, Any]] | None = None,
        channel: str | None = None,
        file_path: str | None = None,
        alt_text: str | None = None,
    ) -> list[FindingCandidate]:
        """Run all deterministic checks (text + visual/accessibility) and aggregate finding candidates."""
        findings: list[FindingCandidate] = []
        if not text and not file_path:
            return findings

        # 1. Terminology checks
        if text and terminology_entries:
            findings.extend(self.check_terminology(text, terminology_entries))

        # 2. Superlatives & claims checks
        if text:
            findings.extend(self.check_superlatives_and_claims(text))

        # 3. Regulatory / Disclosure checks
        if text:
            findings.extend(self.check_disclosures(text, channel))

        # 4. Readability check for high complexity
        if text:
            readability = self.calculate_readability(text)
            if readability["grade_level"] > 12.0 and len(text) > 100:
                findings.append(
                    FindingCandidate(
                        category="accessibility",
                        severity="low",
                        span_start=0,
                        span_end=min(len(text), 50),
                        highlighted_text=text[:50] + "...",
                        explanation=f"Text complexity exceeds brand target (Grade {readability['grade_level']}). Target is Grade 6-8.",
                        source_ref="WCAG 2.2 §3.1.5 (Reading Level)",
                        confidence=0.85,
                        suggested_fix="Simplify sentence structure and replace technical words with everyday language."
                    )
                )

        # 5. Visual accessibility check (missing alt text for images)
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


# Global instance
deterministic_engine = DeterministicReviewEngine()
