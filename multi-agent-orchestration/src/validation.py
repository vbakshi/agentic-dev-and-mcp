"""Input validation and email text normalization helpers."""

import re


_DRAFT_SIGNALS = (
    r"^\s*(dear|hi|hello|hey)\b",
    r"\bbest regards\b",
    r"\bsincerely\b",
    r"\[your name\]",
    r"\[your position\]",
    r"looking forward to your response",
)

_MIN_BRIEF_LEN = 12
_MAX_BRIEF_LEN = 500


class BriefValidationError(ValueError):
    """Raised when a sales writer tool receives an invalid brief."""


def looks_like_email_draft(text: str) -> bool:
    """Heuristic: true when input resembles a finished email rather than a brief."""
    normalized = text.strip().lower()
    if len(normalized) > _MAX_BRIEF_LEN:
        return True

    hits = sum(1 for pattern in _DRAFT_SIGNALS if re.search(pattern, normalized, re.I))
    paragraph_breaks = normalized.count("\n\n")
    return hits >= 2 or (hits >= 1 and paragraph_breaks >= 1)


def validate_writer_brief(brief: str) -> str:
    """
    Validate and normalize a sales-writer tool brief.

    Returns the stripped brief or raises BriefValidationError with guidance
    the manager agent can act on.
    """
    cleaned = brief.strip()
    if not cleaned:
        raise BriefValidationError(
            "Brief is empty. Pass a short instruction such as: "
            "'Write a professional cold email to a CEO opening with Dear CEO.'"
        )
    if len(cleaned) < _MIN_BRIEF_LEN:
        raise BriefValidationError(
            "Brief is too short. Include recipient, salutation, and goal in 1-2 sentences."
        )
    if looks_like_email_draft(cleaned):
        raise BriefValidationError(
            "Input looks like a draft email, not a brief. Pass generation instructions only."
        )
    return cleaned


# Leading "Subject: ..." block (optionally followed by blank line)
_EMBEDDED_SUBJECT_RE = re.compile(
    r"^\s*subject\s*:\s*.+?(?:\n\s*\n|\n(?=\S)|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def strip_embedded_subject_line(text: str) -> str:
    """
    Remove a leading Subject: line from email text if present.

    Used before the subject-line and HTML tools so a writer-included subject
    does not anchor or duplicate the SendGrid subject field.
    """
    cleaned = text.strip()
    if not cleaned:
        return cleaned

    match = _EMBEDDED_SUBJECT_RE.match(cleaned)
    if match:
        return cleaned[match.end() :].strip()

    first_line, _, rest = cleaned.partition("\n")
    if re.match(r"^\s*subject\s*:", first_line, re.IGNORECASE):
        return rest.strip()

    return cleaned
