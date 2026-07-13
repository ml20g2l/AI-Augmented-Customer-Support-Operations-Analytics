# Power BI Dashboard: Korean Step-by-Step Guide

## Before You Start

This guide builds Page 1 only: `Operational Baseline`. It uses observed ticket volumes and clearly labelled assumption-based efficiency scenarios. Do not use the current Gemini prediction file because the Free Tier quota interrupted the validation run.

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

## Future Pages

Build `AI Validation and Routing` only after the Free Tier API pipeline returns at least 300 successful predictions. Build `Root Cause and Recommendations` only after valid root-cause data is available.
