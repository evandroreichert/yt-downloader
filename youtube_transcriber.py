from pathlib import Path

from progress import DownloadProgress
from settings import AppSettings
from transcriber import transcribe_file
from youtube_downloader import download_audio


def run_youtube_transcriber(
    input_fn=input,
    print_fn=print,
    audio_downloader=download_audio,
    transcriber=transcribe_file,
    settings: AppSettings | None = None,
    output_dir: Path | None = None,
    logger=None,
) -> bool:
    try:
        url = input_fn("Cole o link do YouTube: ").strip()
        output_dir = output_dir or Path(__file__).resolve().parent / "downloads"
        print_fn("Baixando o áudio...")
        mp3_path = audio_downloader(
            url,
            output_dir,
            progress_hook=DownloadProgress(print_fn),
            logger=logger,
        )
        print_fn(f"Áudio salvo em: {mp3_path}")
        print_fn("Iniciando transcrição...")
        transcript_paths = transcriber(mp3_path, settings=settings)
    except (ValueError, ImportError) as exc:
        print_fn(f"Erro: {exc}")
        return False
    except Exception as exc:
        print_fn(f"Erro ao baixar ou transcrever: {exc}")
        return False

    if isinstance(transcript_paths, (str, Path)):
        transcript_paths = (transcript_paths,)
    for transcript_path in transcript_paths:
        print_fn(f"Transcrição salva em: {transcript_path}")
    return True
