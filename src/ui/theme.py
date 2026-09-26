"""Corporate light-theme CSS and small presentation helpers for app.py.

Reuses the validated palette in src/ui/palette.py so chart colors and UI
chrome stay consistent. Kept separate from palette.py because this module
is Streamlit/HTML presentation, not chart configuration.
"""
from __future__ import annotations

import streamlit as st

from src.ui.palette import BASELINE, GRIDLINE, MUTED_INK, PRIMARY_INK, SECONDARY_INK, STATUS, SURFACE

_BRAND_PRIMARY = "#2a78d6"
_BRAND_PRIMARY_DARK = "#1c5cab"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --pia-primary: {_BRAND_PRIMARY};
  --pia-primary-dark: {_BRAND_PRIMARY_DARK};
  --pia-ink: {PRIMARY_INK};
  --pia-secondary-ink: {SECONDARY_INK};
  --pia-muted-ink: {MUTED_INK};
  --pia-surface: {SURFACE};
  --pia-border: {GRIDLINE};
  --pia-baseline: {BASELINE};
  --pia-shadow-sm: 0 1px 2px rgba(16, 24, 40, 0.04);
  --pia-shadow-md: 0 4px 14px rgba(16, 24, 40, 0.06);
  --pia-shadow-lg: 0 12px 32px rgba(16, 24, 40, 0.09);
  --pia-radius: 14px;
}}

html, body, [class*="css"] {{
  font-family: "Inter", "Segoe UI", -apple-system, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}}

footer {{ visibility: hidden; }}

.block-container {{ padding-top: 2rem; max-width: 1200px; }}

/* ---- Header banner ---- */
.pia-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.4rem 1.75rem;
  margin-bottom: 1.5rem;
  background: #ffffff;
  border: 1px solid var(--pia-border);
  border-radius: var(--pia-radius);
  box-shadow: var(--pia-shadow-md);
}}
.pia-header-left {{ display: flex; align-items: center; gap: 0.9rem; }}
.pia-mark {{ flex-shrink: 0; filter: drop-shadow(0 2px 6px rgba(42, 120, 214, 0.25)); }}
.pia-header .pia-title {{ margin: 0; font-size: 1.55rem; font-weight: 800; color: var(--pia-ink); letter-spacing: -0.02em; }}
.pia-header .pia-subtitle {{ margin: 0.2rem 0 0 0; color: var(--pia-secondary-ink); font-size: 0.92rem; }}
.pia-badge {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.4rem 0.85rem; border-radius: 999px;
  background: linear-gradient(135deg, #eef3fb 0%, #e4edfb 100%);
  color: var(--pia-primary-dark);
  font-size: 0.78rem; font-weight: 600; border: 1px solid #d7e5f7;
  white-space: nowrap;
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
  border-right: 1px solid var(--pia-border);
  background: linear-gradient(180deg, #f7f6f2 0%, #f2f1ec 100%);
}}
.pia-sidebar-brand {{ display: flex; align-items: center; gap: 0.55rem; font-size: 1.02rem; font-weight: 800; color: var(--pia-ink); letter-spacing: -0.01em; }}
.pia-sidebar-caption {{ font-size: 0.8rem; color: var(--pia-muted-ink); line-height: 1.4; margin-top: 0.35rem; }}

/* ---- Tabs ---- */
div[data-baseweb="tab-list"] {{ gap: 0.25rem; }}
button[data-baseweb="tab"] {{
  font-weight: 600; font-size: 0.93rem; border-radius: 8px 8px 0 0;
  transition: background-color 0.15s ease, color 0.15s ease;
}}
button[data-baseweb="tab"]:hover {{ background-color: #f0f4fb; color: var(--pia-primary-dark); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--pia-primary) !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: var(--pia-primary) !important; height: 3px !important; border-radius: 3px; }}
div[data-baseweb="tab-border"] {{ background-color: var(--pia-border) !important; }}

/* ---- Metric cards ---- */
div[data-testid="stMetric"] {{
  background: #ffffff;
  border: 1px solid var(--pia-border);
  border-radius: 12px;
  padding: 0.9rem 1.1rem 0.7rem 1.1rem;
  box-shadow: var(--pia-shadow-sm);
  transition: box-shadow 0.18s ease, transform 0.18s ease;
}}
div[data-testid="stMetric"]:hover {{ box-shadow: var(--pia-shadow-md); transform: translateY(-1px); }}
div[data-testid="stMetricLabel"] {{ font-weight: 600; color: var(--pia-secondary-ink); }}
div[data-testid="stMetricValue"] {{ color: var(--pia-ink); font-weight: 700; }}

/* ---- Generic containers (bordered st.container(border=True)) ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  border-radius: 12px !important;
  box-shadow: var(--pia-shadow-sm);
}}

/* ---- Buttons ---- */
.stButton button, button[data-testid^="baseButton"], button[data-testid^="stBaseButton"] {{
  border-radius: 8px;
  font-weight: 600;
  transition: box-shadow 0.15s ease, transform 0.1s ease;
  box-shadow: var(--pia-shadow-sm);
}}
.stButton button:hover, button[data-testid^="baseButton"]:hover, button[data-testid^="stBaseButton"]:hover {{
  box-shadow: var(--pia-shadow-md);
  transform: translateY(-1px);
}}
.stButton button[kind="primary"], button[data-testid="baseButton-primary"], button[data-testid="stBaseButton-primary"] {{
  background: linear-gradient(135deg, {_BRAND_PRIMARY} 0%, {_BRAND_PRIMARY_DARK} 100%);
  border: none;
}}

/* ---- Inputs ---- */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{
  border-radius: 8px !important;
}}

/* ---- Section headers ---- */
h2, h3 {{ color: var(--pia-ink); font-weight: 700; letter-spacing: -0.01em; }}

/* ---- Status pills ---- */
.pia-pill {{
  display: inline-block; padding: 0.24rem 0.75rem; border-radius: 999px;
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


def brand_mark(size: int = 34) -> str:
    """Inline SVG logomark: an ascending bar-chart glyph on a brand-blue rounded square.

    Rendered as a single line — Streamlit's markdown parser treats 4-space-indented
    lines as a code block, so a pretty-printed multi-line SVG here would corrupt
    whatever HTML follows it in the same st.markdown() call.
    """
    return (
        f'<svg class="pia-mark" width="{size}" height="{size}" viewBox="0 0 40 40" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="40" height="40" rx="11" fill="{_BRAND_PRIMARY}"/>'
        f'<rect x="9" y="22" width="5.5" height="10" rx="1.8" fill="white" fill-opacity="0.95"/>'
        f'<rect x="17.25" y="15" width="5.5" height="17" rx="1.8" fill="white"/>'
        f'<rect x="25.5" y="9" width="5.5" height="23" rx="1.8" fill="white"/>'
        f"</svg>"
    )


def header_banner(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="pia-header">'
        f'<div class="pia-header-left">{brand_mark(38)}'
        f'<div><p class="pia-title">{title}</p>'
        f'<p class="pia-subtitle">{subtitle}</p></div></div>'
        f'<span class="pia-badge">🔒 Decision-support only · human approval required for controlled outputs</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


_PILL_CLASS = {"pass": "pia-pill-pass", "warning": "pia-pill-warning", "block": "pia-pill-block"}
_PILL_LABEL = {"pass": "PASS", "warning": "WARNING", "block": "BLOCKED"}


def status_pill(status: str) -> str:
    cls = _PILL_CLASS.get(status, "pia-pill-warning")
    label = _PILL_LABEL.get(status, status.upper())
    return f'<span class="pia-pill {cls}">{label}</span>'
