# Power BI Dashboard: Korean Step-by-Step Guide

## Before You Start

이 가이드는 Page 1 `Operational Baseline`부터 시작합니다. 관측된 티켓 수와 가정 기반 효율 시뮬레이션을 분리해 보여줍니다. 이후 Page 2와 Page 3에는 검증 완료된 Gemini Free Tier 300건 샘플의 집계표를 사용합니다.

### Files to Use

Import these three files.

1. `data/processed/tickets_cleaned.csv`
2. `outputs/tables/operational_efficiency_scenarios.csv`
3. `outputs/tables/operational_efficiency_assumptions.csv`

Do not import the category, department, or priority distribution CSV files for this first page. The ticket-level table already contains those fields, so importing both raw and aggregated versions would make the report harder to manage.

### SQL File

You do not need SQL to build this Power BI page.

`sql/eda_queries.sql` is an optional validation file. Run it only if you import `tickets_cleaned.csv` into a SQL tool such as SQLite, DuckDB, or SQL Server and want to reproduce the EDA totals outside Power BI. Its sections are:

- Ticket volume by category
- Ticket volume by priority
- Ticket volume by department
- Category and priority mix for triage planning

## Part 1: Create the Report and Import Data

1. Open Power BI Desktop. On the first screen shown in the screenshot, select **Blank report**.
2. On the top ribbon, select **Home**.
3. Select **Get data**. If you see **Text/CSV**, select it. Otherwise select **Get data from other sources** and then choose **Text/CSV**.
4. Browse to `data/processed/tickets_cleaned.csv`, select it, and choose **Open**.
5. In the preview window, select **Load**. Do not choose Transform Data for this first page.
6. Repeat steps 2 to 5 for `outputs/tables/operational_efficiency_scenarios.csv`.
7. Repeat steps 2 to 5 for `outputs/tables/operational_efficiency_assumptions.csv`.
8. In the right-side Data pane, right-click each table and rename them exactly as follows:
   - `tickets_cleaned` to `Tickets Cleaned`
   - `operational_efficiency_scenarios` to `Operational Efficiency Scenarios`
   - `operational_efficiency_assumptions` to `Operational Efficiency Assumptions`
9. Select **File > Save As** and save the report as `AI_Customer_Support_Operations.pbix` inside `dashboard/powerbi/`.

## Part 2: Add Measures

1. In the Data pane, right-click `Tickets Cleaned` and select **New measure**.
2. Paste the `Total Tickets` measure from `powerbi_measures.dax`.
3. Repeat for `High-Priority Tickets` and `Technical Support Tickets`.
4. Right-click `Operational Efficiency Scenarios`, select **New measure**, and add `Selected Scenario Hours Saved` and `Selected Scenario Cost Saved GBP` from the same DAX file.

## Part 3: Build the First Page

1. At the bottom of the canvas, double-click `Page 1` and rename it `Operational Baseline`.
2. Select **View > Themes** and choose a clean light theme.
3. Select **Insert > Text box**. Add the title `Customer Support Operations` and subtitle `Operational baseline and AI-assisted triage scenarios`.
4. Add three **Card** visuals across the top:
   - Card 1: `Total Tickets`
   - Card 2: `High-Priority Tickets`
   - Card 3: `Technical Support Tickets`
5. Add a **Clustered bar chart** on the left:
   - Y-axis: `actual_category`
   - X-axis: `ticket_id` and set aggregation to **Count**
   - Sort descending by the count
   - Title: `Ticket Volume by Category`
6. Add a second **Clustered bar chart** in the middle:
   - Y-axis: `actual_department`
   - X-axis: `ticket_id` and set aggregation to **Count**
   - Apply a Top N filter of 4 by count
   - Title: `Ticket Volume by Department`
7. Add a **Clustered column chart** on the right:
   - X-axis: `actual_priority`
   - Y-axis: `ticket_id` and set aggregation to **Count**
   - Title: `Ticket Volume by Priority`
8. Add a **Line and clustered column chart** at the bottom:
   - X-axis: `ai_assisted_rate_assumption`
   - Column y-axis: `estimated_hours_saved`
   - Line y-axis: `estimated_cost_saved_gbp`
   - Title: `Estimated Operational Impact by AI-Assisted Triage Coverage`
9. Add a **Table** below or beside the scenario chart:
   - `assumption`
   - `value`
   - `unit`
   - Title: `Simulation Assumptions`
10. Add this footnote with **Insert > Text box**: `Observed ticket volumes are shown separately from assumption-based simulation results. Estimated savings are not observed operational outcomes.`

## Part 4: Format the Page

1. Select each observed-volume chart, choose **Format visual**, and set the data colour to teal: `#1C8C88`.
2. Select the scenario chart and set the columns to amber: `#E3A008`.
3. Use dark charcoal for titles: `#1F2933`.
4. Turn on **View > Snap to grid**. Align the three cards and the three distribution charts.
5. Keep the page free of decorative images, gradients, and excessive borders. This is an operations dashboard, so clarity matters more than decoration.

## Part 5: Add Filters

1. Select **Slicer** from the Visualizations pane.
2. Add `actual_category` to the slicer field.
3. Repeat with `actual_department` and `actual_priority`.
4. Place the three slicers in a compact row below the subtitle or in a narrow left rail.
5. Test one selection. All three observed-data visuals and KPI cards should change together.

## Part 6: Validate and Export

1. Confirm the top KPI is 16,338 before filters are applied.
2. Confirm the category chart shows Incident as the largest category with 6,571 tickets.
3. Confirm the department chart shows Technical Support as the largest queue with 4,737 tickets.
4. Confirm the 50% scenario shows approximately 544.6 estimated hours saved and GBP9,802.80 estimated cost saving.
5. Select **File > Save**.
6. Select **File > Export > PDF** and export one PDF page for your portfolio screenshot folder. Do not upload the `.pbix` file to GitHub because it is excluded by `.gitignore`.

## Part 7: Add Page 2 - AI Validation and Routing

### 7.1 Import and Name the Files

1. Select the **plus (+)** beside `Operational Baseline` to create a new page. Rename it `AI Validation and Routing`.
2. Select **Home > Get data > Text/CSV** and import these files:
   - `outputs/tables/validation_metric_summary.csv`
   - `outputs/tables/category_routing_recommendations.csv`
   - `outputs/tables/routing_threshold_scenarios.csv`
   - `data/processed/confusion_matrix_category.csv`
3. Rename the imported tables in the Data pane:
   - `validation_metric_summary` to `Validation Metric Summary`
   - `category_routing_recommendations` to `Category Routing Recommendations`
   - `routing_threshold_scenarios` to `Routing Threshold Scenarios`
   - `confusion_matrix_category` to `Category Confusion Matrix`
4. For `Category Confusion Matrix`, select **Transform data** during import if the first column has no name. Rename that first column to `Actual Category`, then select **Close & Apply**.
5. Use the Page format icon, set Canvas background to `#F8FAFC` at 0% transparency, and use white `#FFFFFF` for the wallpaper.

### 7.2 Create the Page Header

1. Add a text box in the top-left.
2. Title: `AI Validation and Routing`.
   - Font: Segoe UI Semibold
   - Size: 26 pt
   - Colour: `#1F2933`
3. Subtitle: `Validated on a representative 300-ticket Gemini Free Tier sample`.
   - Font: Segoe UI
   - Size: 12 pt
   - Colour: `#667085`
4. Add a small text box on the top-right: `Category routing only; priority and department remain human-reviewed.`
   - Font: Segoe UI
   - Size: 10 pt
   - Colour: `#667085`
   - Background: `#FFFFFF`
   - Border: `#E5E7EB`, 1 px
   - Corner radius: 4 px

### 7.3 Create the Accuracy KPI Cards

1. In the `Tickets Cleaned` table, create the six Page 2 accuracy measures from `powerbi_measures.dax`: the three numeric accuracy measures and the three `Display` measures.
2. Add three Card visuals in one row below the header:
   - `Category Accuracy Display`; title `Category Accuracy`
   - `Priority Accuracy Display`; title `Priority Accuracy`
   - `Department Accuracy Display`; title `Department Accuracy`
3. For each Card, use these exact settings:
   - Card title: Segoe UI Semibold, 11 pt, colour `#667085`
   - Callout value: Segoe UI Semibold, 28 pt, colour `#1F2933`
   - Background: `#FFFFFF`, 0% transparency
   - Border: On, `#E5E7EB`, 1 px
   - Shadow: Off
   - Corner radius: 4 px
4. Verify the values before continuing: Category `63.3%`, Priority `38.0%`, Department `27.7%`.

### 7.4 Add the Accuracy Comparison Chart

1. Add a **Clustered bar chart** beneath the KPI cards on the left.
2. Add fields:
   - Y-axis: `label` from `Validation Metric Summary`
   - X-axis: `accuracy`
3. Rename fields for this visual:
   - `label` to `Predicted Label`
   - `accuracy` to `Observed Accuracy`
4. Format:
   - Title: `Observed Accuracy by Predicted Label`; Segoe UI Semibold, 14 pt, `#1F2933`
   - Bars: `#1C8C88`
   - Data labels: On, Segoe UI, 10 pt, `#344054`, Display units None, Decimal places 1
   - X-axis: percentage, Start 0%, End 100%, Values Off
   - Y-axis values: Segoe UI, 10 pt, `#667085`
   - Background: transparent; Border: Off; Shadow: Off
5. Tooltips: add `label`, `accuracy`, and `sample_tickets`. Rename them `Predicted Label`, `Observed Accuracy`, and `Validated Tickets`.

### 7.5 Add the Category Routing Policy Table

1. Add a **Table** visual to the right of the accuracy chart.
2. Add fields in this order:
   - `category`
   - `ticket_count`
   - `empirical_accuracy`
   - `routing_recommendation`
3. Rename for this visual: `Category`, `Validated Tickets`, `Empirical Accuracy`, and `Routing Decision`.
4. Format:
   - Title: `Conservative Category Routing Policy`; Segoe UI Semibold, 14 pt, `#1F2933`
   - Column headers: Segoe UI Semibold, 10 pt, `#344054`, white background
   - Values: Segoe UI, 10 pt, `#344054`
   - `empirical_accuracy`: percentage, one decimal place
   - Alternating rows: On, colour `#F8FAFC`
   - Grid vertical lines: Off; horizontal lines: `#E5E7EB`
   - Totals: Off
   - Background: `#FFFFFF`; Border: `#E5E7EB`, 1 px; Corner radius: 4 px
5. Apply conditional background colour to `Routing Decision`:
   - `Auto-route category`: pale teal `#DDF3F1`
   - `Human review`: pale amber `#FFF4D6`
6. Tooltips: add `decision_basis`, `decision_threshold`, and `minimum_sample_tickets`. Rename them `Decision Basis`, `Accuracy Threshold`, and `Minimum Sample Tickets`.

### 7.6 Add the Threshold Trade-off Chart

1. Add a **Line and clustered column chart** across the bottom-left.
2. Add fields:
   - X-axis: `accuracy_threshold`
   - Column y-axis: `automation_rate`
   - Line y-axis: `estimated_auto_route_errors`
3. Rename for this visual:
   - `accuracy_threshold` to `Accuracy Threshold`
   - `automation_rate` to `Automation Rate`
   - `estimated_auto_route_errors` to `Estimated Auto-route Errors`
4. Format:
   - Title: `Automation Coverage and Estimated Error Risk by Threshold`; Segoe UI Semibold, 14 pt, `#1F2933`
   - Column colour: amber `#E3A008`
   - Line colour: dark charcoal `#344054`; width 3; markers Off
   - X-axis: percentage, categorical, values 10 pt `#667085`
   - Column Y-axis: percentage, Values Off
   - Line Y-axis: Values Off
   - Legend: On, Top centre, Segoe UI, 9 pt, `#667085`
   - Background: `#FFFFFF`; Border: `#E5E7EB`, 1 px; Corner radius: 4 px; Shadow Off
5. Tooltips: add `accuracy_threshold`, `automation_rate`, `automated_tickets`, `estimated_auto_route_errors`, `minutes_saved_sample`, and `estimated_cost_saved_sample`.
6. Add a text box inside the lower part of the chart card: `At the 60% threshold, only Request qualifies for category-only auto-routing.`
   - Font: Segoe UI, 9 pt, colour `#B54708`
   - Background: `#FFF7E6`; Border: `#F4C36B`, 1 px; Corner radius: 4 px

### 7.7 Add the Category Confusion Matrix

1. Add a **Matrix** visual to the bottom-right.
2. Add `Actual Category` to Rows. Add each predicted category column from `Category Confusion Matrix` to Values.
3. Title: `Category Confusion Matrix`; Segoe UI Semibold, 14 pt, `#1F2933`.
4. Apply Background colour conditional formatting to each predicted-category value:
   - Minimum: `#FFFFFF`
   - Maximum: `#B8E0DD`
5. Use Segoe UI, 9 pt, `#344054` for headers and values. Turn Totals Off.
6. Use a white background with a `#E5E7EB` 1 px border and 4 px corner radius.

### 7.8 Add the Page 2 Caveat

Add this text box at the bottom of the page:

`Routing decisions use observed category accuracy, not self-reported LLM confidence. Priority and department remain human-reviewed.`

- Font: Segoe UI, 10 pt, `#667085`
- Background: transparent
- Border: Off

## Part 8: Add Page 3 - Root Cause and Recommendations

### 8.1 Import and Prepare the Files

1. Create a new page and rename it `Root Cause and Recommendations`.
2. Select **Home > Get data > Text/CSV** and import:
   - `outputs/tables/root_cause_normalised_distribution.csv`
   - `outputs/tables/root_cause_recommendations.csv`
3. Rename the tables:
   - `root_cause_normalised_distribution` to `Root Cause Themes`
   - `root_cause_recommendations` to `Root Cause Recommendations`
4. Set Canvas background to `#F8FAFC` at 0% transparency. Keep the wallpaper white.
5. In `Tickets Cleaned`, create the Page 3 measures from `powerbi_measures.dax`.

### 8.2 Create the Page Header and KPI Cards

1. Add the title `Root Cause and Recommendations`.
   - Font: Segoe UI Semibold, 26 pt, `#1F2933`
2. Add the subtitle `Recurring issue themes from the classified 300-ticket sample`.
   - Font: Segoe UI, 12 pt, `#667085`
3. Add three Card visuals below the header:
   - `Classified Sample Tickets Display`; title `Classified Sample Tickets`
   - `Largest Named Root Cause Share Display`; title `Largest Named Theme Share`
   - `Unmapped Root Cause Share Display`; title `Unmapped Extracted Wording`
4. Apply the same Card format as Page 2: title Segoe UI Semibold 11 pt `#667085`; callout Segoe UI Semibold 28 pt `#1F2933`; white background; `#E5E7EB` 1 px border; 4 px corner radius; shadow Off.
5. The third card is a data-quality guardrail. Its title should remain visible; do not present it as a success metric.

### 8.3 Add the Recurring-Issue Bar Chart

1. Add a **Clustered bar chart** on the left under the KPI cards.
2. Add fields:
   - Y-axis: `root_cause_theme`
   - X-axis: `ticket_count`
3. In Filters on this visual, exclude `Other extracted issue` and `Unclassified root cause`. These are wording-quality buckets, not actionable issue themes.
4. Sort by `ticket_count` descending.
5. Format:
   - Title: `Top Named Recurring Issue Themes`; Segoe UI Semibold, 14 pt, `#1F2933`
   - Bar colour: teal `#1C8C88`
   - Data labels: On, Segoe UI, 10 pt, `#344054`, Display units None, Decimal places 0
   - X-axis values: Off
   - Y-axis values: Segoe UI, 10 pt, `#667085`
   - Background: `#FFFFFF`; Border: `#E5E7EB`, 1 px; Corner radius 4 px; Shadow Off
6. Tooltips: add `root_cause_theme`, `ticket_count`, and `observed_sample_ticket_share`. Rename them `Issue Theme`, `Classified Tickets`, and `Observed Sample Share`.

### 8.4 Add the Recommendation Table

1. Add a **Table** visual to the right of the chart.
2. Add fields in this order:
   - `root_cause_theme`
   - `ticket_count`
   - `observed_sample_ticket_share`
   - `recommended_action`
3. Rename for this visual: `Issue Theme`, `Tickets`, `Observed Share`, `Recommended Action`.
4. Exclude `Other extracted issue` and `Unclassified root cause` using the visual filter.
5. Format:
   - Title: `Evidence-Bounded Recommendations`; Segoe UI Semibold, 14 pt, `#1F2933`
   - Header: Segoe UI Semibold, 10 pt, `#344054`, white background
   - Values: Segoe UI, 10 pt, `#344054`; word wrap On for `Recommended Action`
   - `Observed Share`: percentage, one decimal place
   - Alternating rows: On, `#F8FAFC`
   - Vertical grid lines: Off; horizontal lines: `#E5E7EB`; Totals: Off
   - Background: `#FFFFFF`; Border: `#E5E7EB`, 1 px; Corner radius: 4 px; Shadow Off
6. Tooltips: add `maximum_addressable_share` and `evidence_note`. Rename them `Maximum Addressable Share` and `Interpretation`.

### 8.5 Add a Data-Quality and Recommendation Note

1. Add a text box across the bottom of the page.
2. Text:

`Observed shares describe the classified sample only. They are not ticket-deflection forecasts. Recommendations describe where self-service work could address demand before adoption or deflection assumptions are applied.`

3. Format:
   - Font: Segoe UI, 10 pt, `#667085`
   - Background: `#FFF7E6`
   - Border: `#F4C36B`, 1 px
   - Corner radius: 4 px
   - Padding: 10 px
4. Keep this note visible in the final PDF. It is an important methodology caveat, not decorative text.

### 8.6 Final Quality Check for Pages 2 and 3

1. Turn off visual-header icons for every chart and table: **Format visual > General > Header icons > Off**.
2. Use only these colours: charcoal `#1F2933`, muted text `#667085`, teal `#1C8C88`, amber `#E3A008`, pale amber `#FFF7E6`, and border grey `#E5E7EB`.
3. Do not use gradients, shadows, or rounded cards above 4 px.
4. Confirm that all recommendation wording refers to the `classified sample`, not all tickets or a guaranteed ticket reduction.
5. Save the `.pbix`, then export each page as PDF or PNG into `dashboard/screenshots/`. Keep the `.pbix` file out of GitHub.
