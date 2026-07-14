from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, TABLES_DIR, ensure_directories


def normalise_root_cause(value: object) -> str:
    """Group wording variants into transparent operational issue themes."""
    text = str(value or "unknown").strip().lower().replace("_", " ").replace("-", " ")

    if any(term in text for term in ["unauthor", "authentication", "access failure", "access error"]):
        return "Account access and security"
    if "integration" in text:
        return "Integration support"
    if any(term in text for term in ["incompatib", "software conflict", "firmware conflict"]):
        return "Software compatibility"
    if any(term in text for term in ["information", "inquiry", "enquiry"]):
        return "Information request"
    if "security" in text:
        return "Security configuration and policy"
    if any(term in text for term in ["billing", "subscription", "pricing"]):
        return "Billing and subscription"
    if any(term in text for term in ["campaign", "marketing", "engagement", "messaging"]):
        return "Marketing performance"
    if any(term in text for term in ["outage", "malfunction", "instability", "synchronization", "synchronisation"]):
        return "Platform reliability"
    if text in {"", "nan", "none", "unknown"}:
        return "Unclassified root cause"
    return "Other extracted issue"


def _recommendation_for(root_cause: str) -> str:
    actions = {
        "Account access and security": "Improve account-recovery and security self-service guidance.",
        "Integration support": "Publish integration setup, configuration, and troubleshooting guidance.",
        "Software compatibility": "Publish compatibility requirements and update troubleshooting guidance.",
        "Information request": "Improve product and service FAQ discovery for common information requests.",
        "Security configuration and policy": "Provide security configuration checklists and policy guidance.",
        "Billing and subscription": "Clarify billing, renewal, and subscription self-service journeys.",
        "Marketing performance": "Provide campaign performance diagnostics and optimisation guidance.",
        "Platform reliability": "Review incident prevention and status communication for recurring reliability issues.",
    }
    return actions.get(root_cause, "Review the underlying tickets before selecting a self-service intervention.")


def export_root_cause_analysis(
    predictions_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Export normalised issue themes and evidence-bounded recommendations."""
    ensure_directories()
    predictions = pd.read_csv(predictions_file)
    if "root_cause" not in predictions.columns:
        return pd.DataFrame(), pd.DataFrame()

    root_causes = predictions["root_cause"].fillna("unknown")
    themes = root_causes.map(normalise_root_cause)
    distribution = (
        themes.value_counts()
        .rename_axis("root_cause_theme")
        .reset_index(name="ticket_count")
    )
    distribution["observed_sample_ticket_share"] = (
        distribution["ticket_count"] / distribution["ticket_count"].sum()
    )
    distribution.to_csv(TABLES_DIR / "root_cause_normalised_distribution.csv", index=False)

    total_tickets = int(themes.size)
    unmapped_tickets = int((themes == "Other extracted issue").sum())
    unclassified_tickets = int((themes == "Unclassified root cause").sum())
    mapping_audit = pd.DataFrame([
        {
            "total_classified_tickets": total_tickets,
            "named_theme_tickets": total_tickets - unmapped_tickets - unclassified_tickets,
            "named_theme_coverage": (total_tickets - unmapped_tickets - unclassified_tickets) / total_tickets,
            "unmapped_extracted_wording_tickets": unmapped_tickets,
            "unmapped_extracted_wording_share": unmapped_tickets / total_tickets,
            "unclassified_root_cause_tickets": unclassified_tickets,
        }
    ])
    mapping_audit.to_csv(TABLES_DIR / "root_cause_mapping_audit.csv", index=False)

    recommendations = distribution.copy()
    recommendations["recommended_action"] = recommendations["root_cause_theme"].map(_recommendation_for)
    recommendations["maximum_addressable_share"] = recommendations["observed_sample_ticket_share"]
    recommendations["evidence_note"] = (
        "Maximum addressable share equals the observed share in the classified sample; "
        "it is not a forecast of ticket deflection."
    )
    recommendations.to_csv(TABLES_DIR / "root_cause_recommendations.csv", index=False)
    return distribution, recommendations
