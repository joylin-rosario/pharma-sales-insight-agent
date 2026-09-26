"""Corporate light-theme CSS and small presentation helpers for app.py.

Reuses the validated palette in src/ui/palette.py so chart colors and UI
chrome stay consistent. Kept separate from palette.py because this module
is Streamlit/HTML presentation, not chart configuration.
"""
from __future__ import annotations

import streamlit as st

from src.ui.palette import BASELINE, GRIDLINE, MUTED_INK, PRIMARY_INK, SECONDARY_INK, STATUS, SURFACE

_BRAND_PRIMARY = "#2a78d6"

_CSS = f"""
<style>
:root {{
  --pia-primary: {_BRAND_PRIMARY};
  --pia-ink: {PRIMARY_INK};
  --pia-secondary-ink: {SECONDARY_INK};
  --pia-muted-ink: {MUTED_INK};
  --pia-surface: {SURFACE};
  --pia-border: {GRIDLINE};
  --pia-baseline: {BASELINE};
}}

html, body, [class*="css"] {{
  font-family: "Segoe UI", -apple-system, system-ui, sans-serif;
}}

footer {{ visibility: hidden; }}

/* ---- Header banner ---- */
.pia-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.1rem 1.5rem;
  margin-bottom: 1.25rem;
  background: linear-gradient(135deg, #ffffff 0%, #f3f7fc 100%);
  border: 1px solid var(--pia-border);
  border-left: 6px solid var(--pia-primary);
  border-radius: 10px;
}}
.pia-header .pia-title {{ margin: 0; font-size: 1.55rem; font-weight: 700; color: var(--pia-ink); letter-spacing: -0.01em; }}
.pia-header .pia-subtitle {{ margin: 0.2rem 0 0 0; color: var(--pia-secondary-ink); font-size: 0.92rem; }}
.pia-badge {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.35rem 0.8rem; border-radius: 999px;
  background: #eef3fb; color: var(--pia-primary);
  font-size: 0.78rem; font-weight: 600; border: 1px solid #d7e5f7;
  white-space: nowrap;
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{ border-right: 1px solid var(--pia-border); }}
.pia-sidebar-brand {{ font-size: 1.05rem; font-weight: 700; color: var(--pia-ink); margin-bottom: 0.1rem; }}
.pia-sidebar-caption {{ font-size: 0.8rem; color: var(--pia-muted-ink); line-height: 1.3; }}

/* ---- Tabs ---- */
button[data-baseweb="tab"] {{ font-weight: 600; font-size: 0.95rem; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--pia-primary) !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: var(--pia-primary) !important; }}
div[data-baseweb="tab-border"] {{ background-color: var(--pia-border) !important; }}

/* ---- Metric cards ---- */
div[data-testid="stMetric"] {{
  background: #ffffff;
  border: 1px solid var(--pia-border);
  border-radius: 10px;
  padding: 0.8rem 1rem 0.6rem 1rem;
}}
div[data-testid="stMetricLabel"] {{ font-weight: 600; color: var(--pia-secondary-ink); }}
div[data-testid="stMetricValue"] {{ color: var(--pia-ink); }}

/* ---- Section headers ---- */
h2, h3 {{ color: var(--pia-ink); font-weight: 700; }}

/* ---- Status pills ---- */
.pia-pill {{
  display: inline-block; padding: 0.22rem 0.7rem; border-radius: 999px;
  font-weight: 700; font-size: 0.8rem; letter-spacing: 0.02em;
}}
.pia-pill-pass {{ background: #e6f7ec; color: {STATUS["good"]}; border: 1px solid #bfe8cc; }}
.pia-pill-warning {{ background: #fff4e0; color: #a56a00; border: 1px solid #f6dba8; }}
.pia-pill-block {{ background: #fbe7e6; color: {STATUS["critical"]}; border: 1px solid #f3c3c1; }}

/* ---- Governance / evidence note ---- */
.pia-note {{
  font-size: 0.82rem; color: var(--pia-muted-ink); font-style: italic;
}}
</style>
"""


def apply_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header_banner(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="pia-header">
          <div>
            <p class="pia-title">{title}</p>
            <p class="pia-subtitle">{subtitle}</p>
          </div>
          <span class="pia-badge">🔒 Decision-support only · human approval required for controlled outputs</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


_PILL_CLASS = {"pass": "pia-pill-pass", "warning": "pia-pill-warning", "block": "pia-pill-block"}
_PILL_LABEL = {"pass": "PASS", "warning": "WARNING", "block": "BLOCKED"}


def status_pill(status: str) -> str:
    cls = _PILL_CLASS.get(status, "pia-pill-warning")
    label = _PILL_LABEL.get(status, status.upper())
    return f'<span class="pia-pill {cls}">{label}</span>'
