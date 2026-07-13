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

1. **Home > Get data > Text/CSV**를 선택합니다.
2. `outputs/tables/category_routing_recommendations.csv`와 `outputs/tables/routing_threshold_scenarios.csv`를 각각 불러옵니다.
3. `category_routing_recommendations` 테이블에서 **Table** 시각화를 추가합니다. `category`, `ticket_count`, `empirical_accuracy`, `routing_recommendation`을 넣습니다.
4. `routing_threshold_scenarios` 테이블에서 **Line and clustered column chart**를 추가합니다. X축은 `accuracy_threshold`, 열 값은 `automation_rate`, 선 값은 `minutes_saved_sample`으로 지정합니다.
5. 같은 테이블로 **Card**를 세 개 추가해 `automated_tickets`, `estimated_auto_route_errors`, `estimated_cost_saved_sample`을 보여줍니다. 카드에는 각각 `Automated Tickets`, `Estimated Auto-route Errors`, `Estimated Cost Saved (Sample)` 제목을 붙입니다.
6. 60% threshold 행을 선택했을 때 `Request`만 `Auto-route category`이고 나머지는 `Human review`인지 확인합니다. 이 정책은 category에만 적용됩니다. priority와 department는 자동 라우팅에 사용하지 않습니다.
7. 텍스트 상자에 다음 문구를 추가합니다: `Routing decisions use observed category accuracy, not self-reported LLM confidence. Priority and department remain human-reviewed.`

## Part 8: Add Page 3 - Root Cause and Recommendations

1. **Home > Get data > Text/CSV**를 선택합니다.
2. `outputs/tables/root_cause_normalised_distribution.csv`와 `outputs/tables/root_cause_recommendations.csv`를 불러옵니다.
3. `root_cause_normalised_distribution` 테이블에서 **Clustered bar chart**를 추가합니다. Y축은 `root_cause_theme`, X축은 `ticket_count`, 제목은 `Top Recurring Issue Themes`로 지정합니다.
4. `root_cause_recommendations` 테이블에서 **Table** 시각화를 추가합니다. `root_cause_theme`, `ticket_count`, `observed_sample_ticket_share`, `recommended_action`을 넣습니다.
5. `observed_sample_ticket_share`는 Percentage 형식으로 바꿉니다. `maximum_addressable_share`도 표시한다면 같은 Percentage 형식을 적용합니다.
6. 페이지 하단에 다음 문구를 추가합니다: `Observed shares describe the classified sample only. They are not ticket-deflection forecasts.`
7. raw root cause가 아니라 반드시 정규화된 `root_cause_theme`을 사용합니다. 같은 의미의 서로 다른 표현을 별도 이슈로 세지 않기 위해서입니다.
