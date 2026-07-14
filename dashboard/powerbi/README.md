# Power BI Dashboard Build Guide

For project findings, methodology, and final dashboard screenshots, see the [project README](../../README.md).

## Purpose

Build a three-page operational dashboard. Page 1 uses cleaned tickets and transparent simulation assumptions. Pages 2 and 3 now use a validated 300-ticket Gemini Free Tier sample, with conservative routing and recommendation caveats retained in the visuals.

## Data Sources

Import the following local CSV files from the project folder.

| Table | File | Use |
| --- | --- | --- |
| Tickets Cleaned | `data/processed/tickets_cleaned.csv` | Base ticket-level table for category, department, and priority analysis. |
| Operational Efficiency Scenarios | `outputs/tables/operational_efficiency_scenarios.csv` | Assumption-based time and cost scenarios. |
| Operational Efficiency Assumptions | `outputs/tables/operational_efficiency_assumptions.csv` | Visible model assumptions and caveats. |
| Category Distribution | `outputs/tables/category_distribution.csv` | Optional pre-aggregated category chart. |
| Department Distribution | `outputs/tables/department_distribution.csv` | Optional pre-aggregated department chart. |
| Priority Distribution | `outputs/tables/priority_distribution.csv` | Optional pre-aggregated priority chart. |
| Validation Metric Summary | `outputs/tables/validation_metric_summary.csv` | Headline accuracy and sample-size metrics by predicted label. |
| Category Routing Recommendations | `outputs/tables/category_routing_recommendations.csv` | Empirical category accuracy and conservative routing decision. |
| Routing Threshold Scenarios | `outputs/tables/routing_threshold_scenarios.csv` | Automation, estimated error, time, and cost trade-offs by threshold. |
| Root Cause Themes | `outputs/tables/root_cause_normalised_distribution.csv` | Normalised recurring-issue themes from the classified sample. |
| Root Cause Recommendations | `outputs/tables/root_cause_recommendations.csv` | Observed sample share and evidence-bounded actions. |

The current `gemini_predictions.csv` contains 300 successful Free Tier classifications and can be imported for diagnostics. Use the prepared aggregate tables above for the final visuals.

## Page 1: Operational Baseline

Use this as the default page.

1. Add three KPI cards: Total Tickets, High-Priority Tickets, and Technical Support Tickets.
2. Add a horizontal bar chart for ticket volume by category.
3. Add a horizontal bar chart for ticket volume by department.
4. Add a column chart for ticket volume by priority.
5. Add a line-and-column chart using Operational Efficiency Scenarios: AI-assisted rate on the x-axis, estimated hours saved as columns, and estimated cost saved as the line.
6. Add the assumptions table at the bottom of the page. Title it `Simulation Assumptions`.

Use concise subtitles that distinguish observed data from assumptions. For example: `Estimated from stated handling-time assumptions; not observed savings.`

## Page 2: AI Validation and Routing

The validated sample now contains 300 successful, label-constrained predictions.

1. Add KPI cards for category, priority, and department accuracy.
2. Add a category confusion matrix heatmap.
3. Add a table of empirical category accuracy, ticket count, and routing recommendation.
4. Add a what-if parameter called `Accuracy Threshold` from 50% to 95% in 5% increments.
5. Add cards for automation rate, estimated auto-route errors, and estimated time saved.
6. Use the threshold parameter to show auto-route only for categories whose empirical accuracy meets the selected threshold. All remaining categories should be labelled `Human review`.

LLM confidence must not control routing. It may appear only as a diagnostic distribution or calibration comparison.

## Page 3: Root Cause and Recommendations

Root-cause extraction is available for the valid classified sample. Use `Root Cause Themes` rather than raw model wording so synonymous issues are grouped consistently.

1. Add a ranked bar chart for root-cause frequency.
2. Add a matrix with root cause, ticket count, and ticket share.
3. Add a recommendation text card driven by the selected root cause: `This issue accounts for X% of the measured sample. Self-service improvements could address up to that measured share before adoption and deflection assumptions are applied.`

Do not state a ticket-reduction percentage beyond the observed root-cause share without a separate adoption assumption.

## Visual Standards

- Use a white canvas, charcoal text, teal for observed volumes, and amber for assumptions.
- Use red only for error or human-review risk.
- Keep global slicers limited to category, department, and priority.
- Show data caveats in a small footer rather than in the KPI cards.

## Dashboard Screenshots

The final Power BI dashboard screenshots are stored alongside this guide:

- `operational-baseline.png`: Page 1, Operational Baseline
- `ai-validation-and-routing.png`: Page 2, AI Validation and Routing
- `root-cause-and-recommendations.png`: Page 3, Root Cause and Recommendations

The `.pbix` source file remains local and is intentionally excluded from GitHub.
