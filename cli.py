from transcriber import run_transcriber
from youtube_downloader import run_downloader
from youtube_transcriber import run_youtube_transcriber


def run_menu(
    input_fn=input,
    print_fn=print,
    downloader_action=run_downloader,
    transcriber_action=run_transcriber,
    combined_action=run_youtube_transcriber,
) -> int:
    while True:
        print_fn("\n=== Ferramentas de Mídia ===")
        print_fn("1 - Baixar vídeo ou áudio do YouTube")
        print_fn("2 - Transcrever arquivo de áudio ou vídeo")
        print_fn("3 - Baixar do YouTube e transcrever")
        print_fn("0 - Sair")
        choice = input_fn("Escolha uma opção: ").strip()

        if choice == "1":
            downloader_action()
        elif choice == "2":
            transcriber_action()
        elif choice == "3":
            combined_action()
        elif choice == "0":
            print_fn("Até mais!")
            return 0
        else:
            print_fn("Opção inválida. Escolha 1, 2, 3 ou 0.")


def main() -> None:
    try:
        raise SystemExit(run_menu())
    except KeyboardInterrupt:
        print("\nOperação cancelada.")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
