"""Configuration helpers for the multi-agent project."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    llm_api_key: str
    llm_model: str
    llm_base_url: str
    project_root: Path
    intent_min_confidence: float
    max_history_turns: int


def load_settings(project_root: Path | None = None) -> Settings:
    """Load environment settings.

    Args:
        project_root: Optional project root. If omitted, infer from this file.
    """
    root = project_root or Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Configure it in 05_project/.env")

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    base_url = "https://api.groq.com/openai/v1"

    raw_threshold = os.getenv("INTENT_MIN_CONFIDENCE", "0.60")
    raw_history = os.getenv("MAX_HISTORY_TURNS", "4")

    try:
        threshold = float(raw_threshold)
        max_history = int(raw_history)
    except ValueError as exc:
        raise RuntimeError("Error en los valores numéricos del .env") from exc

    return Settings(
        llm_api_key=api_key,
        llm_model=model,
        llm_base_url=base_url,
        project_root=root,
        intent_min_confidence=threshold,
        max_history_turns=max_history,
    )
