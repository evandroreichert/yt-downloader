import platform
from importlib import metadata


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "não instalado"


def _cuda_status() -> str:
    try:
        import ctranslate2

        count = ctranslate2.get_cuda_device_count()
        return f"disponível ({count} dispositivo(s))" if count else "indisponível"
    except (ImportError, RuntimeError) as exc:
        return f"indisponível ({exc})"


def collect_python_diagnostics() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "yt_dlp": _package_version("yt-dlp"),
        "faster_whisper": _package_version("faster-whisper"),
        "yt_dlp_ejs": _package_version("yt-dlp-ejs"),
        "cuda": _cuda_status(),
    }


if __name__ == "__main__":
    for key, value in collect_python_diagnostics().items():
        print(f"{key}: {value}")
