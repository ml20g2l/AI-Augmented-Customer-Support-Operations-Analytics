# Root-Cause Mapping Audit

## Purpose

This audit documents how LLM-extracted root-cause wording was converted into dashboard themes for the 300-ticket validated classification sample.

## Coverage

| Measure | Result |
| --- | ---: |
| Classified tickets reviewed | 300 |
| Tickets assigned to a named theme | 209 |
| Named-theme coverage | 69.7% |
| Unmapped extracted wording | 91 |
| Unmapped extracted wording share | 30.3% |

## Controls

- Theme assignment uses deterministic keyword rules in `src/root_cause_analysis.py` after the LLM extraction step.
- Named themes are used for the recurring-issue chart and evidence-bounded recommendation table.
- `Other extracted issue` remains visible as the `Unmapped Extracted Wording` data-quality KPI and is excluded from named-theme recommendations.
- Observed shares refer only to the classified sample. They are not ticket-deflection forecasts or production root-cause labels.

## Interpretation

The remaining unmapped wording is heterogeneous and often describes a narrow technical symptom rather than a reusable operational theme. It is retained rather than force-mapped into an unsuitable category. This preserves the distinction between a useful exploratory signal and a validated production root-cause taxonomy.

## Reproducibility

Run `python -m src.run_pipeline --evaluate-only` after classification to regenerate `outputs/tables/root_cause_mapping_audit.csv` locally. The table is intentionally excluded from GitHub with the other generated data outputs.
