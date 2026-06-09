"""Runtime configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_project_env() -> Path:
    """
    Load `.env` from the project root (multi-agent-orchestration/).

    Call this before Settings.from_env(). Works regardless of the shell cwd.
    `uv run` does not load .env automatically — python-dotenv handles it here.
    """
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    return PROJECT_ROOT


@dataclass(frozen=True)
class Settings:
    """Central settings for the sales orchestration workflow."""

    openai_api_key: str
    sendgrid_api_key: str | None
    from_email: str
    to_email: str
    agent_model: str
    dry_run: bool
    output_dir: str
    max_output_files: int

    @classmethod
    def from_env(
        cls,
        output_dir: str = "output",
        max_output_files: int = 3,
        *,
        load_env: bool = True,
    ) -> "Settings":
        if load_env:
            load_project_env()

        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        dry_run = os.getenv("SALES_WORKFLOW_DRY_RUN", "false").lower() in {
            "1",
            "true",
            "yes",
        }

        return cls(
            openai_api_key=openai_api_key,
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY", "").strip() or None,
            from_email=os.getenv("SALES_FROM_EMAIL", "vinayak.kayaniv91@gmail.com"),
            to_email=os.getenv("SALES_TO_EMAIL", "vinayak.kayaniv91@gmail.com"),
            agent_model=os.getenv("SALES_AGENT_MODEL", "gpt-4o-mini"),
            dry_run=dry_run,
            output_dir=output_dir,
            max_output_files=max_output_files,
        )

    def require_sendgrid(self) -> None:
        if self.dry_run:
            return
        if not self.sendgrid_api_key:
            raise ValueError(
                "SENDGRID_API_KEY is required unless SALES_WORKFLOW_DRY_RUN=true"
            )
