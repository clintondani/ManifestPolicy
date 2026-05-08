# backend/scanner.py
import re
from utils import clean_text
from summarizer import summarize_policy


# Shady clause patterns and reasons
shady_patterns = [
    {
        "pattern": r"we may share.*third parties",
        "clause": "We may share your data with third parties",
        "reason": "Your data could be sold or shared without consent or transparency."
    },
    {
        "pattern": r"we are not responsible.*data breaches",
        "clause": "We are not responsible for data breaches",
        "reason": "Disclaiming responsibility violates accountability under DPDP."
    },
    {
        "pattern": r"we collect data.*without notice",
        "clause": "We collect data without informing users",
        "reason": "Users must be notified about data collection per DPDP Section 7."
    },
    {
        "pattern": r"we may sell.*your data",
        "clause": "We may sell your data",
        "reason": "Selling user data without explicit consent breaches Section 4."
    },
    {
        "pattern": r"your data may be transferred.*outside india",
        "clause": "Data may be transferred outside India",
        "reason": "Cross-border transfers must have safeguards (Section 16)."
    }
]

# DPDP Act compliance rules
dpdp_rules = [
    {
        "section": "Consent (Section 4)",
        "pattern": r"(no user consent|consent.*not required|implied consent)",
        "violation": "Lack of valid user consent",
        "description": "Consent must be free, informed, specific, and unambiguous."
    },
    {
        "section": "Purpose Limitation (Section 5)",
        "pattern": r"(data collected.*but purpose not specified|no stated purpose)",
        "violation": "Unclear or missing purpose",
        "description": "The purpose for data collection must be stated clearly."
    },
    {
        "section": "Data Minimisation (Section 6)",
        "pattern": r"(we collect.*all information|we may collect anything)",
        "violation": "Excessive data collection",
        "description": "Only necessary data should be collected."
    },
    {
        "section": "Notice to Data Principal (Section 7)",
        "pattern": r"(no notice.*collection|users not notified)",
        "violation": "No prior notice to users",
        "description": "Users must be notified before or at the time of data collection."
    },
    {
        "section": "Grievance Redressal (Section 9)",
        "pattern": r"(no grievance officer|no contact.*complaints)",
        "violation": "Missing grievance redressal contact",
        "description": "You must provide contact details for user complaints."
    },
    {
        "section": "Children’s Data (Section 10)",
        "pattern": r"(we may collect.*children|no age restriction)",
        "violation": "Improper handling of children’s data",
        "description": "Processing of children's data must follow stricter safeguards."
    },
    {
        "section": "Data Retention (Section 8)",
        "pattern": r"(retain.*indefinitely|no retention policy)",
        "violation": "Unclear data retention policy",
        "description": "Data should not be stored longer than necessary."
    },
    {
        "section": "User Rights (Section 11-12)",
        "pattern": r"(no right to access|no correction option|cannot delete data)",
        "violation": "Denial of user rights",
        "description": "Users must be able to access, correct, or delete their data."
    },
    {
        "section": "Data Sharing Transparency (Section 13)",
        "pattern": r"(shared.*without informing|third parties not disclosed)",
        "violation": "Opaque data sharing",
        "description": "Users must know who their data is shared with."
    },
    {
        "section": "Cross-border Transfer (Section 16)",
        "pattern": r"(transfer.*outside.*without safeguards|no info about data transfer)",
        "violation": "Unsafe international data transfers",
        "description": "Data should only be transferred with safeguards."
    },
    {
        "section": "Data Protection Officer (Section 8)",
        "pattern": r"(no dpo|no data protection officer)",
        "violation": "Missing Data Protection Officer",
        "description": "Organizations must appoint a DPO for compliance."
    }
]

def scan_policy(text):
    cleaned = clean_text(text.lower())

    if not cleaned or len(cleaned.split()) < 30:
        return {
            "error": "No valid policy text found or Please upload a text-based policy file."
        }

    shady_found = []
    for item in shady_patterns:
        match = re.search(item["pattern"], cleaned)
        if match:
            shady_found.append({
                "clause": item["clause"],
                "reason": item["reason"]
            })

    dpdp_found = []
    for rule in dpdp_rules:
        if re.search(rule["pattern"], cleaned):
            dpdp_found.append({
                "section": rule["section"],
                "violation": rule["violation"],
                "description": rule["description"]
            })

    from summary_formatter import format_summary

    raw_summary = summarize_policy(text)

    structured_summary = format_summary(
        raw_summary.get("summary_text") if isinstance(raw_summary, dict) else raw_summary
    )

    return {
        "summary": structured_summary,
        "shady_clauses": shady_found,
        "dpdp_violations": dpdp_found
    }



