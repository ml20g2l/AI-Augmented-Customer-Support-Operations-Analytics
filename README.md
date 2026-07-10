# AI-Augmented Customer Support Operations Analytics

This project evaluates how AI-assisted ticket classification can improve customer support triage operations. The focus is not simply building an LLM classifier, but quantifying where AI can safely support routing, how much manual triage time could be saved, and which recurring issues create the largest operational load.

## Project Positioning

The core business question:

> Can AI-assisted classification improve customer support routing while keeping error risk transparent and measurable?

This project is designed for Junior to Associate Data, Business, Product, and Operations Analyst roles. It combines Python analytics, LLM-assisted classification, validation metrics, and Power BI-ready outputs.

## Data

Planned dataset: **Multilingual Customer Support Tickets** from Kaggle.

This project uses a synthetic but realistic customer support ticket dataset for demonstration purposes. Methodology and metrics are directly transferable to real production ticket data.

Scope:

- English tickets only
- Up to 500 representative tickets classified with the Gemini API free tier
- Remaining data used for EDA and operational simulation using existing labels
- LLM results validated against existing `category`, `priority`, and `department` labels where available

Current local dataset check:

- Downloaded with `kagglehub` from `tobiasbueck/multilingual-customer-support-tickets`
- Latest downloaded archive path resolved to KaggleHub version folder `versions/14`
- Selected v5-style source file: `aa_dataset-tickets-multi-lang-5-2-50-version.csv`
- Detected source columns: `subject`, `body`, `answer`, `type`, `queue`, `priority`, `language`, `version`, `tag_1` to `tag_8`
- Label mapping: `type` -> category, `queue` -> department/routing queue, `priority` -> priority
- Starting rows: 28,587
- English rows after language filter: 16,338
- Final cleaned rows: 16,338
- Classification sample: 500 stratified rows

## Folder Structure

```text
data/
  raw/            # original Kaggle CSV file
  processed/      # cleaned data, sample data, predictions, metrics
notebooks/        # optional exploratory notebooks
outputs/
  charts/         # confusion matrices and visuals
  tables/         # Power BI-ready CSV tables
sql/              # optional SQL queries for EDA checks
src/
  config.py
  data_cleaning.py
  evaluation.py
  gemini_classification.py
  powerbi_exports.py
  sampling.py
  schema.py
  run_pipeline.py
requirements.txt
```

## Phase 1: Core Analytics

1. Clean the raw ticket dataset
2. Filter to English-language tickets when a language column is available
3. Analyze ticket category, department, and priority distributions
4. Build a representative sample for Gemini classification
5. Compare AI predictions with actual labels
6. Calculate accuracy, precision, recall, F1, and confusion matrices
7. Estimate before/after triage time and potential cost savings

The operational-efficiency table is available before LLM validation and is intentionally assumption-based. It shows the potential impact of 0%, 25%, 50%, and 75% AI-assisted triage coverage across all cleaned English tickets. These scenarios use a visible baseline of five manual triage minutes per ticket, one AI-assisted minute per ticket, and a GBP18 fully loaded hourly cost. They are not presented as observed savings.

## Project Progress

| Phase | Workstream | Status | Evidence |
| --- | --- | --- | --- |
| Phase 1 | Data cleaning and English-only scope | Complete | 28,587 source rows to 16,338 cleaned English tickets; cleaning audit saved locally. |
| Phase 1 | EDA and distribution analysis | Complete | Executed Jupyter notebook and Power BI-ready category, department, and priority tables. |
| Phase 1 | Operational-efficiency simulation | Complete | Assumption-labelled time and cost scenarios across all cleaned tickets. |
| Phase 1 | Gemini classification and validation | Pending Free Tier reset | The pipeline is ready to resume only failed tickets; no paid tier will be used. |
| Phase 2 | Routing design and threshold comparison | Designed, pending validated sample | Power BI table structure and routing logic are ready once sufficient successful predictions exist. |
| Phase 3 | Root-cause analysis and recommendations | Pending validated sample | Root-cause extraction and observed-share recommendations will follow successful classification. |

## Phase 2: AI Routing Design

The routing design uses empirical accuracy, not raw LLM confidence, as the primary decision basis.

- High-accuracy categories can be recommended for auto-routing
- Lower-accuracy or ambiguous categories remain in human review
- LLM self-reported confidence is retained only as a supporting diagnostic field

This avoids overstating the reliability of model-generated confidence scores.

## Phase 3: Root Cause and Recommendations

Recurring issue analysis will be based on extracted root causes such as refund, login issue, password reset, delivery delay, billing error, and product defect.

Recommendation principle:

> If an issue accounts for X% of measured tickets, then self-service or FAQ improvements can be discussed as addressing up to that measured X% of ticket demand, before applying any separate adoption or deflection assumptions.

All recommendation figures should be tied back to observed data.

## How To Run

1. Add the Kaggle CSV file to `data/raw/`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: download the Kaggle dataset with `kagglehub`:

```bash
python -m src.download_data
```

4. Clean and sample the data:

```bash
python -m src.run_pipeline --raw-file data/raw/your_file.csv --sample-size 500
```

5. Run Gemini classification using a Free Tier API key:

Confirm in Google AI Studio that the API key belongs to a project marked **Free**. Do not link a billing account or select a paid-tier project for this portfolio project. The classifier accepts only `gemini-3.1-flash-lite`, requires an explicit free-tier acknowledgement, and caps each run at 500 tickets. It does not use grounding, batch processing, or other paid-only features. Predictions are saved after each ticket so an interrupted run can resume without repeating already completed requests. If the Free Tier quota is exhausted, failed tickets are retried only when the free quota becomes available again; the project never switches to a paid tier.

```bash
set GEMINI_API_KEY=your_free_tier_api_key
set GEMINI_FREE_TIER_ONLY=true
python -m src.gemini_classification --input data/processed/classification_sample.csv
```

In PowerShell, use:

```powershell
$env:GEMINI_API_KEY="your_free_tier_api_key"
$env:GEMINI_FREE_TIER_ONLY="true"
python -m src.gemini_classification --input data/processed/classification_sample.csv
```

6. Evaluate predictions and export Power BI tables:

```bash
python -m src.run_pipeline --evaluate-only
```

## Planned Power BI Outputs

- Ticket volume by category, priority, and department
- Classification accuracy by label type
- Confusion matrix heatmaps
- Automation threshold scenario table
- Estimated triage time saved
- Top recurring root causes

## Methodology Notes

- Gemini classification is validated on a representative sample, not the full dataset.
- Gemini is given the observed category, priority, and routing label options, then must choose from those options exactly. This tests AI-assisted triage within the existing operating taxonomy rather than an unrelated open-ended taxonomy.
- LLM confidence is treated as an auxiliary signal only.
- Routing thresholds are based on empirical performance against known labels.
- Cost and time savings are simulation estimates and should be shown separately from directly observed data.
- Gemini classification is restricted to the Google AI Studio Free Tier. The project is intentionally designed to stop at the free quota rather than continue on a paid tier.
