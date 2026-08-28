from pathlib import Path
from typing import Any


def _youtube_requested_reload(error: Exception) -> bool:
    return "page needs to be reloaded" in str(error).lower()


def normalize_format(choice: str) -> str:
    formats = {"1": "mp4", "2": "mp3", "mp4": "mp4", "mp3": "mp3"}
    try:
        return formats[choice.strip().lower()]
    except KeyError as exc:
        raise ValueError(
            "Opção inválida. Escolha 1 para MP4 ou 2 para MP3."
        ) from exc


def build_options(media_format: str, output_dir: Path) -> dict[str, Any]:
    options: dict[str, Any] = {
        "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
        "noplaylist": True,
        "js_runtimes": {"node": {}},
    }

    if media_format == "mp4":
        return options | {
            "format": (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "best[ext=mp4]/best"
            ),
            "merge_output_format": "mp4",
        }

    if media_format == "mp3":
        return options | {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0",
                }
            ],
        }

    raise ValueError("Formato inválido.")


def download(
    url: str,
    media_format: str,
    output_dir: Path,
    ydl_class=None,
) -> None:
    clean_url = url.strip()
    if not clean_url:
        raise ValueError("O link não pode ficar vazio.")

    if ydl_class is None:
        from yt_dlp import YoutubeDL

        ydl_class = YoutubeDL

    output_dir.mkdir(parents=True, exist_ok=True)
    for attempt in range(2):
        try:
            with ydl_class(build_options(media_format, output_dir)) as ydl:
                ydl.download([clean_url])
            return
        except Exception as exc:
            if not _youtube_requested_reload(exc) or attempt == 1:
                raise


def download_audio(url: str, output_dir: Path, ydl_class=None) -> Path:
    clean_url = url.strip()
    if not clean_url:
        raise ValueError("O link não pode ficar vazio.")

    if ydl_class is None:
        from yt_dlp import YoutubeDL

        ydl_class = YoutubeDL

    output_dir.mkdir(parents=True, exist_ok=True)
    for attempt in range(2):
        try:
            with ydl_class(build_options("mp3", output_dir)) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                downloaded_path = Path(ydl.prepare_filename(info))
            return downloaded_path.with_suffix(".mp3")
        except Exception as exc:
            if not _youtube_requested_reload(exc) or attempt == 1:
                raise

    raise RuntimeError("Falha inesperada ao baixar o áudio.")


def run_downloader(
    input_fn=input,
    print_fn=print,
    downloader=download,
) -> bool:
    try:
        url = input_fn("Cole o link do YouTube: ").strip()
        choice = input_fn("Escolha o formato (1 = MP4, 2 = MP3): ")
        media_format = normalize_format(choice)
        output_dir = Path(__file__).resolve().parent / "downloads"
        downloader(url, media_format, output_dir)
    except (ValueError, ImportError) as exc:
        print_fn(f"Erro: {exc}")
        return False
    except Exception as exc:
        if "ffmpeg" in str(exc).lower():
            print_fn(
                "Erro: FFmpeg não encontrado. Instale-o e adicione-o ao PATH."
            )
        else:
            print_fn(f"Erro no download: {exc}")
        return False

    print_fn("Download concluído com sucesso!")
    return True
