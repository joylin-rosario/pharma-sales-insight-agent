"""Pharma Sales Insight Agent — Streamlit entry point (CLAUDE.md section 24).

Analytics decision-support prototype. Not a chatbot, not an autonomous
decision-maker: every numerical claim is computed deterministically in
Python and every controlled output requires recorded human approval.
"""
from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import orchestrator
from src.agents import data_quality_agent
from src.data.ingestion import UnsupportedFileTypeError, dataset_version_from_bytes, load_sales_file
from src.governance.approval import ACTIONS_REQUIRING_APPROVAL, create_pending_approval, is_approved, record_decision
from src.observability.mask import mask_hr_name
from src.observability.tracer import read_events
from src.state.models import ApprovalDecision
from src.ui.palette import CATEGORICAL, PLOTLY_LAYOUT, STATUS
from src.ui.theme import apply_theme, header_banner, status_pill

ROLES = json.loads(open("config/roles.json").read())

st.set_page_config(page_title="Pharma Sales Insight Agent", layout="wide", page_icon="💊")
apply_theme()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {
    "df": None,
    "dataset_version": None,
    "dq_report": None,
    "approvals": {},  # action_type -> ApprovalRecord
    "workflow_state": None,
    "hierarchy_correction_applied": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_approval(action_type: str):
    return st.session_state.approvals.get(action_type)


def request_approval(action_type: str):
    if action_type not in st.session_state.approvals or st.session_state.approvals[action_type].decision != ApprovalDecision.PENDING:
        st.session_state.approvals[action_type] = create_pending_approval(action_type)


# ---------------------------------------------------------------------------
# Sidebar — role, scope, filters
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    '<div class="pia-sidebar-brand">💊 Pharma Sales Insight Agent</div>'
    '<div class="pia-sidebar-caption">Analytics decision-support prototype — '
    "not a chatbot, not an autonomous decision-maker.</div>",
    unsafe_allow_html=True,
)
st.sidebar.divider()

role = st.sidebar.selectbox("Your role", list(ROLES.keys()))
role_cfg = ROLES[role]
st.sidebar.caption(role_cfg["description"])

authorized_scope: dict = {}
df = st.session_state.df

if df is not None:
    if role == "Area Manager":
        allowed_area = st.sidebar.selectbox("Authorized Area", sorted(df["area"].unique()))
        authorized_scope = {"area": [allowed_area]}
    elif role == "Territory Manager":
        allowed_territory = st.sidebar.selectbox("Authorized Territory", sorted(df["territory"].unique()))
        authorized_scope = {"territory": [allowed_territory]}
    # Sales Head / Demo Admin: unrestricted for this demo

st.sidebar.divider()
st.sidebar.subheader("Filters")
filters: dict = {}
period_filter = None
if df is not None:
    bu = st.sidebar.selectbox("Business Unit", ["(All)"] + sorted(df["business_unit"].unique()))
    if bu != "(All)":
        filters["business_unit"] = bu
    scoped = df[df["business_unit"] == bu] if bu != "(All)" else df

    area = st.sidebar.selectbox("Area", ["(All)"] + sorted(scoped["area"].unique()))
    if area != "(All)":
        filters["area"] = area
    scoped = scoped[scoped["area"] == area] if area != "(All)" else scoped

    district = st.sidebar.selectbox("District", ["(All)"] + sorted(scoped["district"].unique()))
    if district != "(All)":
        filters["district"] = district
    scoped = scoped[scoped["district"] == district] if district != "(All)" else scoped

    territory = st.sidebar.selectbox("Territory", ["(All)"] + sorted(scoped["territory"].unique()))
    if territory != "(All)":
        filters["territory"] = territory

    product = st.sidebar.selectbox("Product", ["(All)"] + sorted(df["product"].unique()))
    if product != "(All)":
        filters["product"] = product

    period_filter = st.sidebar.selectbox("Period", ["(All)"] + sorted(df["date"].unique()))

header_banner(
    "Pharma Sales Insight Agent",
    "Evidence-based sales performance insight across Business Unit, Area, District, Territory, and Health Representative levels.",
)

tabs = st.tabs(["📤 Upload", "✅ Data Quality", "📊 Dashboard", "💬 Ask", "🔏 Approval", "🔍 Trace"])

# ---------------------------------------------------------------------------
# Upload tab
# ---------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Upload approved sales file")
    st.caption("Synthetic or formally approved data only. CSV or XLSX. See data/synthetic/sales_data.csv for a demo file.")
    uploaded = st.file_uploader("Sales data file", type=["csv", "xlsx", "xls"])

    if uploaded is not None:
        raw_bytes = uploaded.getvalue()
        try:
            new_df = load_sales_file(uploaded, uploaded.name)
            st.session_state.df = new_df
            st.session_state.dataset_version = dataset_version_from_bytes(raw_bytes)
            report, status = data_quality_agent.run(new_df)
            st.session_state.dq_report = report
            st.success(
                f"Loaded {len(new_df)} rows. Dataset version `{st.session_state.dataset_version}`. "
                f"Data quality status: **{status.value.upper()}** — see the Data Quality tab."
            )
        except UnsupportedFileTypeError as exc:
            st.error(str(exc))
        except Exception as exc:  # ingestion failure surfaced, not swallowed
            st.error(f"Failed to read file: {exc}")

    if st.session_state.df is None:
        st.info("No file uploaded yet. You can load the bundled synthetic dataset for a quick demo:")
        if st.button("Load synthetic demo dataset"):
            with open("data/synthetic/sales_data.csv", "rb") as f:
                raw_bytes = f.read()
            new_df = load_sales_file(open("data/synthetic/sales_data.csv", "rb"), "sales_data.csv")
            st.session_state.df = new_df
            st.session_state.dataset_version = dataset_version_from_bytes(raw_bytes)
            report, status = data_quality_agent.run(new_df)
            st.session_state.dq_report = report
            st.rerun()

# ---------------------------------------------------------------------------
# Data Quality tab
# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Data Quality Agent report")
    report = st.session_state.dq_report
    if report is None:
        st.info("Upload a file first.")
    else:
        st.markdown(f"#### Status: {status_pill(report.status)}", unsafe_allow_html=True)
        st.caption(f"{report.row_count} rows checked across columns: {', '.join(report.checked_columns)}")
        if not report.findings:
            st.success("No issues found.")
        for finding in report.findings:
            icon = {"block": "🛑", "warning": "⚠️", "info": "ℹ️"}[finding.severity]
            st.write(f"{icon} **[{finding.check}]** {finding.message}")

        if report.status == "block":
            st.error("Critical failures block downstream analysis. Fix the source file and re-upload.")

        ambiguous = [f for f in report.findings if f.check == "hierarchy_mapping"]
        if ambiguous:
            st.divider()
            st.write("**Hierarchy correction available** (requires human approval — section 19):")
            approval = get_approval("accept_hierarchy_correction")
            if approval and approval.decision == ApprovalDecision.APPROVED:
                st.success("Correction approved and applied for this session (ambiguous rows excluded from analysis).")
            elif approval and approval.decision == ApprovalDecision.REJECTED:
                st.warning("Correction was rejected. Ambiguous rows remain excluded from drill-down until resolved upstream.")
            else:
                if st.button("Request approval to exclude ambiguous rows from this session's analysis"):
                    request_approval("accept_hierarchy_correction")
                    st.rerun()
                if approval:
                    st.info("Approval pending — go to the Approval tab.")

# ---------------------------------------------------------------------------
# Dashboard tab
# ---------------------------------------------------------------------------
with tabs[2]:
    if st.session_state.df is None:
        st.info("Upload a file first.")
    elif st.session_state.dq_report is not None and st.session_state.dq_report.status == "block":
        st.error("Data quality status is BLOCK. Dashboard is disabled until critical failures are resolved.")
    else:
        from src.analytics.kpi import compute_summary, compute_contribution_breakdown

        scoped = st.session_state.df.copy()
        for col, value in filters.items():
            scoped = scoped[scoped[col] == value]
        if period_filter and period_filter != "(All)":
            scoped = scoped[scoped["date"] == period_filter]

        summary = compute_summary(scoped, filters, period_filter if period_filter != "(All)" else None)

        st.subheader("Key performance indicators")
        c1, c2, c3 = st.columns(3)
        c1.metric("Actual Sales", summary["actual_sales"].display)
        c2.metric("Target Sales", summary["target_sales"].display)
        c3.metric("Achievement %", summary["achievement_pct"].display)

        c4, c5 = st.columns(2)
        variance = summary["variance_to_target"]
        c4.metric("Variance to Target", variance.display, delta=None)
        if summary["growth_pct"].value is not None:
            c5.metric("Growth %", summary["growth_pct"].display)
        else:
            c5.metric("Growth %", "N/A")
            st.caption(f"Growth % unavailable — {summary['growth_pct'].reason}")

        st.divider()
        st.subheader("Performance charts")
        col_a, col_b = st.columns(2)

        with col_a:
            st.write("**Actual vs Target by Business Unit**")
            grouped = scoped.groupby("business_unit")[["sales_value", "target_value"]].sum().reset_index()
            fig = go.Figure()
            fig.add_bar(name="Actual", x=grouped["business_unit"], y=grouped["sales_value"], marker_color=CATEGORICAL[0])
            fig.add_bar(name="Target", x=grouped["business_unit"], y=grouped["target_value"], marker_color=CATEGORICAL[1])
            fig.update_layout(barmode="group", **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.write("**Variance to Target by Area**")
            grouped_area = scoped.groupby("area")[["sales_value", "target_value"]].sum().reset_index()
            grouped_area["variance"] = grouped_area["sales_value"] - grouped_area["target_value"]
            colors = [STATUS["good"] if v >= 0 else STATUS["critical"] for v in grouped_area["variance"]]
            fig2 = go.Figure(go.Bar(x=grouped_area["area"], y=grouped_area["variance"], marker_color=colors))
            fig2.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        st.subheader("Territory contribution %")
        st.caption("Within current filter scope.")
        contrib = compute_contribution_breakdown(scoped, "territory", filters)
        contrib_df = pd.DataFrame(
            [{"territory": c.filters.get("territory"), "contribution_pct": c.value} for c in contrib if c.value is not None]
        )
        if not contrib_df.empty:
            fig3 = go.Figure(go.Bar(x=contrib_df["territory"], y=contrib_df["contribution_pct"], marker_color=CATEGORICAL[2]))
            fig3.update_layout(**PLOTLY_LAYOUT, yaxis_title="Contribution %")
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.subheader("Row-level data")
        st.caption("Current filters applied.")
        can_view_hr = role_cfg["can_view_hr_level"] and is_approved(list(st.session_state.approvals.values()), "view_hr_level_detail")
        display_df = scoped.copy()
        if not can_view_hr:
            display_df["hr_name"] = display_df["hr_name"].apply(mask_hr_name)
            st.caption("Health Representative names are masked. Approve 'view_hr_level_detail' in the Approval tab to reveal.")
            approval = get_approval("view_hr_level_detail")
            if role_cfg["can_view_hr_level"] and (approval is None or approval.decision != ApprovalDecision.APPROVED):
                if st.button("Request approval to view HR-level detail"):
                    request_approval("view_hr_level_detail")
                    st.rerun()
        st.dataframe(display_df, use_container_width=True, height=300)

# ---------------------------------------------------------------------------
# Ask tab
# ---------------------------------------------------------------------------
with tabs[3]:
    if st.session_state.df is None:
        st.info("Upload a file first.")
    elif st.session_state.dq_report is not None and st.session_state.dq_report.status == "block":
        st.error("Data quality status is BLOCK. Ask is disabled until critical failures are resolved.")
    else:
        st.subheader("Ask a business question")
        st.caption(
            "Supported: compare sales/target by level, gap or growth contributors, drill-down, "
            "period comparison, top/bottom territories, management summary."
        )
        question = st.text_input("Your question", placeholder="e.g. What is our achievement vs target this period?")
        treat_hypothesis_as_confirmed = st.checkbox(
            "Present top hypothesis as a confirmed finding (requires approval)", value=False
        )

        if st.button("Run analysis", type="primary") and question:
            with st.spinner("Supervisor is planning and delegating..."):
                state = orchestrator.run_request(
                    df=st.session_state.df,
                    question=question,
                    filters=filters,
                    user_role=role,
                    authorized_scope=authorized_scope,
                    dataset_version=st.session_state.dataset_version or "unknown",
                    period=period_filter if period_filter and period_filter != "(All)" else None,
                )
                st.session_state.workflow_state = state

        state = st.session_state.workflow_state
        if state is not None:
            st.divider()
            st.caption(f"Request ID `{state.request_id}` · Dataset version `{state.dataset_version}`")

            with st.expander("Execution plan & agent statuses", expanded=True):
                for step in state.plan:
                    status_icon = {"done": "✅", "failed": "❌", "running": "🔄", "planned": "⏳"}.get(step.status, "•")
                    skill_txt = f" · skill: `{step.skill}`" if step.skill else ""
                    st.write(f"{status_icon} **{step.agent}** — {step.task}{skill_txt}")

            blocked_guardrails = [g for g in state.guardrail_results if not g.passed]
            if blocked_guardrails:
                st.error("🛑 Request blocked by governance guardrails:")
                for g in blocked_guardrails:
                    st.write(f"- **{g.check}**: {g.reason}")

            if state.final_output:
                fo = state.final_output
                st.subheader("Findings")
                col_f, col_o = st.columns(2)
                with col_f:
                    with st.container(border=True):
                        st.markdown("**Facts** · deterministic calculations")
                        for f in fo.facts:
                            st.write(f"- {f}")
                with col_o:
                    with st.container(border=True):
                        st.markdown("**Observations**")
                        for o in fo.observations:
                            st.write(f"- {o}")

                if fo.hypotheses:
                    st.markdown('**Hypotheses** <span class="pia-note">labeled, require human validation</span>', unsafe_allow_html=True)
                    for h in fo.hypotheses:
                        st.write(f"- {h}")
                    if treat_hypothesis_as_confirmed:
                        approval = get_approval("present_hypothesis_as_fact")
                        if approval and approval.decision == ApprovalDecision.APPROVED:
                            st.success("Approved: top hypothesis is now presented as a confirmed finding below.")
                            st.write(f"**Confirmed finding:** {fo.hypotheses[0].replace('[HYPOTHESIS - requires human validation] ', '')}")
                        else:
                            if st.button("Request approval to present hypothesis as fact"):
                                request_approval("present_hypothesis_as_fact")
                                st.rerun()
                            st.info("Approval required in the Approval tab before a hypothesis can be presented as confirmed.")

                if fo.recommendations:
                    st.markdown('**Recommendations** <span class="pia-note">low-risk, reversible, subject to approval</span>', unsafe_allow_html=True)
                    for r in fo.recommendations:
                        st.write(f"- {r}")

                if fo.limitations:
                    st.markdown("**Limitations**")
                    for l in fo.limitations:
                        st.caption(f"⚠️ {l}")

                if fo.evidence_ids:
                    with st.expander(f"Evidence ({len(fo.evidence_ids)} items)"):
                        for ev in state.evidence:
                            st.write(f"`{ev.evidence_id}` · {ev.metric} · filters={ev.filters} · value={ev.value} · reason={ev.reason}")

                st.divider()
                export_approval = get_approval("export_management_report")
                exportable = export_approval and export_approval.decision == ApprovalDecision.APPROVED
                if not exportable:
                    if st.button("Request approval to export management report"):
                        request_approval("export_management_report")
                        st.rerun()
                report_text = "\n".join(
                    ["FACTS"] + fo.facts + ["", "OBSERVATIONS"] + fo.observations
                    + ["", "LIMITATIONS"] + fo.limitations
                )
                st.download_button(
                    "📄 Export management report",
                    data=report_text,
                    file_name=f"management_report_{state.request_id}.txt",
                    disabled=not exportable,
                    help="Disabled until export approval is recorded in the Approval tab.",
                )

# ---------------------------------------------------------------------------
# Approval tab
# ---------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Human-in-the-loop approvals")
    st.caption("A rejection returns the workflow to revision — it never silently completes.")

    if not st.session_state.approvals:
        st.info("No approval requests yet. They appear automatically when a controlled output is requested.")
    for action_type, record in st.session_state.approvals.items():
        with st.container(border=True):
            st.write(f"**{action_type}** — status: `{record.decision.value}`")
            if record.decision == ApprovalDecision.PENDING:
                approver = st.text_input(f"Approver name ({action_type})", key=f"approver_{action_type}")
                comment = st.text_area(f"Comment ({action_type})", key=f"comment_{action_type}")
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve", key=f"approve_{action_type}", disabled=not approver):
                    record_decision(record, approver, ApprovalDecision.APPROVED, comment)
                    st.rerun()
                if col2.button("❌ Reject", key=f"reject_{action_type}", disabled=not approver):
                    record_decision(record, approver, ApprovalDecision.REJECTED, comment)
                    st.rerun()
            else:
                st.caption(f"Decided by {record.approver} at {record.timestamp}. Comment: {record.comment or '—'}")

    st.divider()
    st.write("**Connectors** (section 17 — least privilege, approval required before any write capability)")
    st.checkbox("Read-only SQLite analytical access", value=True, disabled=True)
    write_approval = get_approval("enable_connector_or_write")
    write_enabled = write_approval and write_approval.decision == ApprovalDecision.APPROVED
    if st.checkbox("Enable write-back connector (never actually enabled in this prototype)", value=False, disabled=True):
        pass
    if not write_enabled and st.button("Request approval to enable a write connector (illustrative only)"):
        request_approval("enable_connector_or_write")
        st.rerun()

# ---------------------------------------------------------------------------
# Trace tab
# ---------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Execution trace")
    state = st.session_state.workflow_state
    if state is None:
        st.info("Run a question in the Ask tab to see its trace.")
    else:
        st.caption(
            "User Request > Plan > Sub-agent > Skill > Tool/MCP > Evidence > Action > "
            "Guardrail Check > Human Approval > Final Output > Evaluation"
        )
        events = read_events(state.request_id)
        for ev in events:
            status_icon = {"ok": "✅", "error": "❌", "blocked": "🛑", "unsupported_intent": "⚠️"}.get(ev["status"], "•")
            parts = [f"`{ev['timestamp']}`", status_icon, f"**{ev['workflow_step']}**"]
            if ev.get("agent"):
                parts.append(f"agent={ev['agent']}")
            if ev.get("skill"):
                parts.append(f"skill={ev['skill']}")
            if ev.get("latency_ms") is not None:
                parts.append(f"{ev['latency_ms']}ms")
            st.write(" · ".join(parts))

        with st.expander("Full request state (JSON)"):
            st.json(state.model_dump())
