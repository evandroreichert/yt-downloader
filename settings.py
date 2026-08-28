import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ALLOWED_MODELS = {"tiny", "base", "small", "medium", "large-v3", "turbo"}
ALLOWED_TRANSCRIPT_FORMATS = {"txt", "srt"}


@dataclass(frozen=True)
class AppSettings:
    language: str = "pt"
    model: str = "turbo"
    batch_size: int = 4
    timestamps: bool = True
    transcript_formats: tuple[str, ...] = ("txt", "srt")
    keep_downloaded_audio: bool = True
    technical_logs: bool = True


DEFAULT_SETTINGS = AppSettings()


def _validate(data: dict[str, Any], path: Path) -> AppSettings:
    allowed_keys = set(asdict(DEFAULT_SETTINGS))
    unknown = set(data) - allowed_keys
    if unknown:
        raise ValueError(
            f"Configuração desconhecida em {path}: {', '.join(sorted(unknown))}"
        )

    merged = asdict(DEFAULT_SETTINGS) | data
    for key in ("language", "model"):
        if not isinstance(merged[key], str) or not merged[key].strip():
            raise ValueError(f"'{key}' deve ser um texto não vazio em {path}.")

    if merged["model"] not in ALLOWED_MODELS:
        choices = ", ".join(sorted(ALLOWED_MODELS))
        raise ValueError(f"Modelo inválido em {path}. Use: {choices}.")

    batch_size = merged["batch_size"]
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError(f"'batch_size' deve ser um inteiro positivo em {path}.")

    for key in ("timestamps", "keep_downloaded_audio", "technical_logs"):
        if not isinstance(merged[key], bool):
            raise ValueError(f"'{key}' deve ser true ou false em {path}.")

    formats = merged["transcript_formats"]
    if "transcript_formats" in data and not isinstance(formats, list):
        raise ValueError(f"'transcript_formats' deve ser uma lista em {path}.")
    if not isinstance(formats, (list, tuple)) or not formats:
        raise ValueError(f"'transcript_formats' deve conter txt e/ou srt em {path}.")
    if any(item not in ALLOWED_TRANSCRIPT_FORMATS for item in formats):
        raise ValueError(f"Formatos inválidos em {path}. Use apenas txt e/ou srt.")

    merged["language"] = merged["language"].strip()
    merged["transcript_formats"] = tuple(dict.fromkeys(formats))
    return AppSettings(**merged)


def load_settings(path: Path) -> AppSettings:
    if not path.exists():
        return DEFAULT_SETTINGS

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Não foi possível ler a configuração {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"A configuração {path} deve conter um objeto JSON.")
    return _validate(raw, path)
