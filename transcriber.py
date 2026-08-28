import os
from pathlib import Path


def normalize_media_path(raw: str) -> Path:
    path = Path(raw.strip().strip('"')).expanduser()
    if not path.is_file():
        raise ValueError(f"Arquivo não encontrado: {path}")
    return path


def format_segment(segment) -> str:
    return f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"


def write_transcript(segments, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as stream:
        for segment in segments:
            stream.write(format_segment(segment) + "\n")


def configure_nvidia_dlls() -> None:
    try:
        import nvidia
    except ImportError:
        return

    nvidia_root = Path(nvidia.__path__[0]).parent / "nvidia"
    for directory, _, filenames in os.walk(nvidia_root):
        if "bin" not in Path(directory).parts:
            continue
        if not any(filename.lower().endswith(".dll") for filename in filenames):
            continue

        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(directory)
        os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")


def create_model(model_factory, print_fn=print):
    try:
        return model_factory("turbo", device="cuda", compute_type="int8")
    except Exception as cuda_error:
        print_fn(
            f"GPU indisponível ({cuda_error}). Continuando pela CPU; "
            "isso pode ser mais lento."
        )
        return model_factory("turbo", device="cpu", compute_type="int8")


def transcribe_file(
    media_path: Path,
    model_factory=None,
    pipeline_factory=None,
    print_fn=print,
) -> Path:
    configure_nvidia_dlls()

    if model_factory is None or pipeline_factory is None:
        from faster_whisper import BatchedInferencePipeline, WhisperModel

        model_factory = model_factory or WhisperModel
        pipeline_factory = pipeline_factory or BatchedInferencePipeline

    model = create_model(model_factory, print_fn)
    pipeline = pipeline_factory(model=model)
    segments, _ = pipeline.transcribe(
        str(media_path),
        language="pt",
        batch_size=4,
    )
    output_path = media_path.with_suffix(".txt")
    write_transcript(segments, output_path)
    return output_path


def run_transcriber(
    input_fn=input,
    print_fn=print,
    transcriber=transcribe_file,
) -> bool:
    try:
        raw_path = input_fn("Cole o caminho do arquivo de áudio ou vídeo: ")
        media_path = normalize_media_path(raw_path)
        print_fn("Iniciando transcrição...")
        output_path = transcriber(media_path)
    except (ValueError, ImportError) as exc:
        print_fn(f"Erro: {exc}")
        return False
    except Exception as exc:
        print_fn(f"Erro na transcrição: {exc}")
        return False

    print_fn(f"Transcrição salva em: {output_path}")
    return True
