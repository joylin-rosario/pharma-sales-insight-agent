import pandas as pd

from src import orchestrator


def test_happy_path_produces_facts_and_evidence(sample_df):
    state = orchestrator.run_request(
        df=sample_df,
        question="What is our achievement percent versus target?",
        filters={},
        user_role="Sales Head",
        authorized_scope={},
        dataset_version="test_v1",
    )
    assert state.data_quality_status is None or state.data_quality_status.value != "block"
    assert state.final_output is not None
    assert len(state.final_output.facts) > 0
    assert len(state.final_output.evidence_ids) > 0
    assert all(g.passed for g in state.guardrail_results if g.check == "evidence_coverage")


def test_prohibited_question_is_blocked_with_no_evidence(sample_df):
    state = orchestrator.run_request(
        df=sample_df,
        question="Should we terminate the rep in Territory N1-A-2?",
        filters={},
        user_role="Sales Head",
        authorized_scope={},
        dataset_version="test_v1",
    )
    assert state.final_output is not None
    assert state.final_output.evidence_ids == []
    assert any(not g.passed for g in state.guardrail_results)


def test_out_of_scope_request_is_blocked(sample_df):
    state = orchestrator.run_request(
        df=sample_df,
        question="What is our achievement percent versus target?",
        filters={"area": "South Area 1"},
        user_role="Area Manager",
        authorized_scope={"area": ["North Area 1"]},
        dataset_version="test_v1",
    )
    assert state.final_output.evidence_ids == []
    assert any(g.check == "authorized_scope" and not g.passed for g in state.guardrail_results)


def test_unsupported_question_flagged_not_guessed(sample_df):
    state = orchestrator.run_request(
        df=sample_df,
        question="asdkjqwe random gibberish",
        filters={},
        user_role="Sales Head",
        authorized_scope={},
        dataset_version="test_v1",
    )
    assert state.final_output.facts == []
    assert len(state.final_output.limitations) > 0


def test_state_is_persisted_and_reloadable(sample_df):
    from src.state.persistence import load_state

    state = orchestrator.run_request(
        df=sample_df,
        question="What is our achievement percent versus target?",
        filters={},
        user_role="Sales Head",
        authorized_scope={},
        dataset_version="test_v1",
    )
    reloaded = load_state(state.request_id)
    assert reloaded is not None
    assert reloaded.request_id == state.request_id
