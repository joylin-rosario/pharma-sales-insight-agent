"""Convert KPIResults into EvidenceItems so every numerical claim is traceable
(CLAUDE.md section 10: metric, filters, period, value, evidence reference)."""
from __future__ import annotations

from src.analytics.kpi import KPIResult
from src.state.models import EvidenceItem


def to_evidence(result: KPIResult) -> EvidenceItem:
    return EvidenceItem(
        metric=result.metric,
        filters=result.filters,
        period=result.period,
        value=result.value,
        reason=result.reason,
    )
