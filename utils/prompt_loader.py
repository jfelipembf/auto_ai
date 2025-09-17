from __future__ import annotations

from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE / "prompts"


def load_prompt(name: str) -> Optional[str]:
    """Carrega um prompt em markdown de prompts/{name}.md.
    Retorna o conteúdo como string ou None se não existir.
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
