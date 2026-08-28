from pathlib import Path

from transcriber import transcribe_file
from youtube_downloader import download_audio


def run_youtube_transcriber(
    input_fn=input,
    print_fn=print,
    audio_downloader=download_audio,
    transcriber=transcribe_file,
) -> bool:
    try:
        url = input_fn("Cole o link do YouTube: ").strip()
        output_dir = Path(__file__).resolve().parent / "downloads"
        print_fn("Baixando o áudio...")
        mp3_path = audio_downloader(url, output_dir)
        print_fn(f"Áudio salvo em: {mp3_path}")
        print_fn("Iniciando transcrição...")
        transcript_path = transcriber(mp3_path)
    except (ValueError, ImportError) as exc:
        print_fn(f"Erro: {exc}")
        return False
    except Exception as exc:
        print_fn(f"Erro ao baixar ou transcrever: {exc}")
        return False

    print_fn(f"Transcrição salva em: {transcript_path}")
    return True
