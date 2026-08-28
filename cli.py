from pathlib import Path

from progress import configure_logging
from settings import load_settings
from terminal_ui import RetroTerminal
from transcriber import run_transcriber
from youtube_downloader import run_downloader
from youtube_transcriber import run_youtube_transcriber


def build_actions(settings, root: Path, print_fn=print):
    logger = configure_logging(settings.technical_logs, root)
    output_dir = root / "downloads"
    return (
        lambda: run_downloader(
            print_fn=print_fn, output_dir=output_dir, logger=logger
        ),
        lambda: run_transcriber(print_fn=print_fn, settings=settings),
        lambda: run_youtube_transcriber(
            print_fn=print_fn,
            settings=settings,
            output_dir=output_dir,
            logger=logger,
        ),
    )


def run_menu(
    input_fn=input,
    print_fn=print,
    downloader_action=run_downloader,
    transcriber_action=run_transcriber,
    combined_action=run_youtube_transcriber,
    pause_fn=None,
    ui=None,
) -> int:
    ui = ui or RetroTerminal(print_fn)
    while True:
        ui.show_menu()
        choice = input_fn("  Escolha uma opção > ").strip()

        if choice == "1":
            downloader_action()
        elif choice == "2":
            transcriber_action()
        elif choice == "3":
            combined_action()
        elif choice == "0":
            ui.status("success", "Até mais!")
            return 0
        else:
            ui.status("error", "Opção inválida. Escolha 1, 2, 3 ou 0.")
            continue

        if pause_fn is not None:
            pause_fn("Pressione ENTER para voltar ao menu...")


def run_app(
    root: Path | None = None,
    settings_loader=load_settings,
    print_fn=print,
    menu_runner=run_menu,
) -> int:
    root = root or Path(__file__).resolve().parent
    ui = RetroTerminal(print_fn)
    try:
        settings = settings_loader(root / "config.json")
    except ValueError as exc:
        ui.status("error", f"Erro de configuração: {exc}")
        return 1

    downloader_action, transcriber_action, combined_action = build_actions(
        settings, root, ui.output
    )
    return menu_runner(
        print_fn=ui.print_fn,
        downloader_action=downloader_action,
        transcriber_action=transcriber_action,
        combined_action=combined_action,
        pause_fn=input,
        ui=ui,
    )


def main() -> None:
    try:
        raise SystemExit(run_app())
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
