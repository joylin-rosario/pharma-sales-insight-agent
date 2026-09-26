"""Rule-based natural-language intent parser (CLAUDE.md section 4 steps 5-6).

Deterministic keyword matching against the six supported question types
(section 5). No LLM call is required — this keeps the prototype fully
offline/reproducible and avoids fabricated interpretations of ambiguous asks.
Unsupported questions are explicitly flagged rather than guessed at.
"""
from __future__ import annotations

from src.state.models import ParsedIntent

LEVEL_KEYWORDS = {
    "business_unit": ["business unit", "bu "],
    "area": ["area"],
    "district": ["district"],
    "territory": ["territory"],
    "hr_id": ["health representative", "rep ", "hr "],
}

QUESTION_TYPES = [
    ("top_bottom_territories", ["top territor", "bottom territor", "best territor", "worst territor", "rank territor"]),
    ("gap_contributors", ["gap", "shortfall", "contributor", "what drove", "what caused the"]),
    ("growth_result", ["growth", "grew", "increase in sales", "decline in sales"]),
    ("drill_down", ["drill down", "breakdown by", "break down by"]),
    ("period_comparison", ["compare", "vs last", "versus", "period over period", "month over month"]),
    ("management_summary", ["summary", "executive summary", "management report", "overview"]),
    ("achievement_overview", ["achievement", "target", "performance"]),
]


def _detect_level(question: str) -> str | None:
    lowered = question.lower()
    for level, keywords in LEVEL_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                return level
    return None


def parse_question(question: str) -> ParsedIntent:
    lowered = question.strip().lower()
    if not lowered:
        return ParsedIntent(question_type="unsupported", supported=False, reason="Question was empty.")

    level = _detect_level(question)

    for qtype, keywords in QUESTION_TYPES:
        for kw in keywords:
            if kw in lowered:
                return ParsedIntent(
                    question_type=qtype,
                    level=level,
                    supported=True,
                )

    return ParsedIntent(
        question_type="unsupported",
        level=level,
        supported=False,
        reason=(
            "Could not map this question to a supported analysis type. "
            "Supported: sales/target comparison by level, gap or growth contributors, "
            "drill-down, period comparison, top/bottom territories, management summary."
        ),
    )
