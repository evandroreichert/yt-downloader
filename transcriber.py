import os
import site
from pathlib import Path

from settings import AppSettings, DEFAULT_SETTINGS


_DLL_DIRECTORY_HANDLES = []
_CONFIGURED_DLL_DIRS = set()


def normalize_media_path(raw: str) -> Path:
    path = Path(raw.strip().strip('"')).expanduser()
    if not path.is_file():
        raise ValueError(f"Arquivo não encontrado: {path}")
    return path


def format_segment(segment) -> str:
    return f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"


def format_srt_timestamp(seconds: float) -> str:
    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def render_txt(segments, timestamps: bool = True) -> str:
    lines = [
        format_segment(segment) if timestamps else segment.text.strip()
        for segment in segments
    ]
    return "".join(f"{line}\n" for line in lines)


def render_srt(segments) -> str:
    blocks = []
    for index, segment in enumerate(segments, start=1):
        start = format_srt_timestamp(segment.start)
        end = format_srt_timestamp(segment.end)
        blocks.append(f"{index}\n{start} --> {end}\n{segment.text.strip()}\n")
    return "\n".join(blocks)


def write_transcript(segments, output_path: Path) -> None:
    output_path.write_text(render_txt(segments), encoding="utf-8")


def write_transcripts(
    segments,
    media_path: Path,
    formats: tuple[str, ...],
    timestamps: bool,
) -> tuple[Path, ...]:
    segment_list = list(segments)
    renderers = {
        "txt": lambda: render_txt(segment_list, timestamps),
        "srt": lambda: render_srt(segment_list),
    }
    outputs = tuple(media_path.with_suffix(f".{extension}") for extension in formats)
    temporary_paths = []
    try:
        for extension, output_path in zip(formats, outputs):
            temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
            temporary_path.write_text(renderers[extension](), encoding="utf-8")
            temporary_paths.append(temporary_path)
        for temporary_path, output_path in zip(temporary_paths, outputs):
            temporary_path.replace(output_path)
    finally:
        for temporary_path in temporary_paths:
            temporary_path.unlink(missing_ok=True)
    return outputs


def configure_nvidia_dlls(
    user_site: Path | None = None,
    add_dll_directory=None,
) -> tuple[Path, ...]:
    roots = []
    try:
        import nvidia
        roots.extend(Path(path) for path in nvidia.__path__)
    except ImportError:
        pass

    user_site = user_site or Path(site.getusersitepackages())
    roots.append(Path(user_site) / "nvidia")
    add_dll_directory = add_dll_directory or getattr(
        os, "add_dll_directory", None
    )

    configured = []
    for root in dict.fromkeys(roots):
        for directory, _, filenames in os.walk(root):
            directory_path = Path(directory)
            if "bin" not in directory_path.parts:
                continue
            if not any(
                filename.lower().endswith(".dll") for filename in filenames
            ):
                continue

            configured.append(directory_path)
            directory_text = str(directory_path)
            if directory_text in _CONFIGURED_DLL_DIRS:
                continue
            if add_dll_directory is not None:
                _DLL_DIRECTORY_HANDLES.append(
                    add_dll_directory(directory_text)
                )
            os.environ["PATH"] = (
                directory_text + os.pathsep + os.environ.get("PATH", "")
            )
            _CONFIGURED_DLL_DIRS.add(directory_text)
    return tuple(configured)


def cuda_available() -> bool:
    try:
        import ctranslate2

        return ctranslate2.get_cuda_device_count() > 0
    except (ImportError, RuntimeError):
        return False


def create_model(model_factory, print_fn=print, cuda_detector=cuda_available):
    if not cuda_detector():
        return model_factory("turbo", device="cpu", compute_type="int8")
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
    settings: AppSettings | None = None,
    cuda_detector=cuda_available,
) -> tuple[Path, ...]:
    settings = settings or DEFAULT_SETTINGS
    configure_nvidia_dlls()

    if model_factory is None or pipeline_factory is None:
        from faster_whisper import BatchedInferencePipeline, WhisperModel

        model_factory = model_factory or WhisperModel
        pipeline_factory = pipeline_factory or BatchedInferencePipeline

    def transcribe_on(device: str):
        model = model_factory(settings.model, device=device, compute_type="int8")
        pipeline = pipeline_factory(model=model)
        segments, _ = pipeline.transcribe(
            str(media_path),
            language=settings.language,
            batch_size=settings.batch_size,
        )
        return list(segments)

    if cuda_detector():
        try:
            segments = transcribe_on("cuda")
        except Exception as cuda_error:
            print_fn(
                f"GPU indisponível ({cuda_error}). Continuando pela CPU; "
                "isso pode ser mais lento."
            )
            segments = transcribe_on("cpu")
    else:
        segments = transcribe_on("cpu")

    return write_transcripts(
        segments,
        media_path,
        settings.transcript_formats,
        settings.timestamps,
    )


def run_transcriber(
    input_fn=input,
    print_fn=print,
    transcriber=transcribe_file,
    settings: AppSettings | None = None,
) -> bool:
    try:
        raw_path = input_fn("Cole o caminho do arquivo de áudio ou vídeo: ")
        media_path = normalize_media_path(raw_path)
        print_fn("Iniciando transcrição...")
        output_paths = transcriber(media_path, settings=settings)
    except (ValueError, ImportError) as exc:
        print_fn(f"Erro: {exc}")
        return False
    except Exception as exc:
        print_fn(f"Erro na transcrição: {exc}")
        return False

    for output_path in output_paths:
        print_fn(f"Transcrição salva em: {output_path}")
    return True
