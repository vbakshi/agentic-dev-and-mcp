"""Load professional profile context from summary and resume."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "me"


@dataclass(frozen=True)
class ProfileContext:
    name: str
    summary: str
    resume_text: str


def load_resume_text(resume_path: Path) -> str:
    reader = PdfReader(str(resume_path))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def load_profile(
    data_dir: Path | None = None,
    name: str | None = None,
) -> ProfileContext:
    """Load summary and resume from the data directory."""
    data_dir = data_dir or DEFAULT_DATA_DIR
    summary_path = data_dir / "summary.txt"
    resume_path = data_dir / "Vinayak-Bakshi-Resume.pdf"

    if not summary_path.exists():
        raise FileNotFoundError(f"Summary not found: {summary_path}")
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    summary = summary_path.read_text(encoding="utf-8")
    resume_text = load_resume_text(resume_path)

    return ProfileContext(
        name=name or "Vinayak Bakshi",
        summary=summary,
        resume_text=resume_text,
    )
