"""Small golden set covering Business Unit and Territory questions (section 23)."""
import pandas as pd
import pytest

from src import orchestrator

GOLDEN_CASES = [
    {
        "name": "business_unit_achievement",
        "question": "What is our achievement percent versus target for the business unit?",
        "filters": {"business_unit": "North BU"},
        "expect_facts": True,
    },
    {
        "name": "territory_top_bottom",
        "question": "What are the top territories by sales?",
        "filters": {},
        "expect_facts": True,
    },
    {
        "name": "management_summary",
        "question": "Give me a management summary of performance.",
        "filters": {},
        "expect_facts": True,
    },
]


@pytest.mark.parametrize("case", GOLDEN_CASES, ids=[c["name"] for c in GOLDEN_CASES])
def test_golden_case_routes_and_answers(sample_df, case):
    state = orchestrator.run_request(
        df=sample_df,
        question=case["question"],
        filters=case["filters"],
        user_role="Sales Head",
        authorized_scope={},
        dataset_version="golden_v1",
    )
    assert state.parsed_intent.supported is True
    if case["expect_facts"]:
        assert len(state.final_output.facts) > 0
        assert len(state.final_output.evidence_ids) > 0
