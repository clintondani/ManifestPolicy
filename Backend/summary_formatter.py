def format_summary(summary_text: str) -> dict:
    """
    Converts raw summary text into a structured summary object
    expected by frontend and PDF.
    """

    if not summary_text:
        return {
            "overview": "Not available",
            "data_collected": "Not clearly stated",
            "data_sharing": "Not clearly stated",
            "user_rights": "Not clearly stated",
            "data_retention": "Not clearly stated"
        }

    text = summary_text.lower()

    return {
        "overview": summary_text[:300] + "..." if len(summary_text) > 300 else summary_text,

        "data_collected": (
            "Usage data, device data, and interaction data are collected."
            if "collect" in text or "usage data" in text
            else "Not clearly stated"
        ),

        "data_sharing": (
            "Data may be shared with third parties or government authorities."
            if "share" in text or "third parties" in text
            else "Not clearly stated"
        ),

        "user_rights": (
            "Users can request access, deletion, and correction of personal data."
            if "right" in text or "access" in text or "deletion" in text
            else "Not clearly stated"
        ),

        "data_retention": (
            "Data retention period is mentioned."
            if "retain" in text or "retention" in text
            else "Not clearly stated"
        )
    }
