import os
import sys


RESET = "\033[0m"
COLORS = {
    "accent": "\033[96m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "error": "\033[91m",
    "muted": "\033[90m",
}
LABELS = {
    "info": "INFO",
    "success": "OK",
    "warning": "AVISO",
    "error": "ERRO",
}


def terminal_supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    return (
        os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
        and hasattr(stream, "isatty")
        and stream.isatty()
    )


def colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{COLORS[color]}{text}{RESET}"


def style_status(kind: str, message: str, use_color: bool = False) -> str:
    label = LABELS[kind]
    color = "accent" if kind == "info" else kind
    return colorize(f"[{label}] {message}", color, use_color)


class RetroTerminal:
    def __init__(self, print_fn=print, use_color=None):
        self.print_fn = print_fn
        self.use_color = (
            terminal_supports_color() if use_color is None else use_color
        )

    def clear(self) -> None:
        if self.use_color:
            self.print_fn("\033[2J\033[H")

    def show_menu(self) -> None:
        self.clear()
        border = "+" + "-" * 54 + "+"

        def row(text: str, centered: bool = False) -> str:
            content = text.center(52) if centered else f"{text:<52}"
            return f"| {content} |"

        lines = (
            border,
            row("MEDIA TOOLS", centered=True),
            row("YouTube + Whisper CLI", centered=True),
            border,
            row("[1]  Baixar video ou audio do YouTube"),
            row("[2]  Transcrever arquivo local"),
            row("[3]  Baixar e transcrever"),
            row("[0]  Sair"),
            border,
        )
        for line in lines:
            highlighted = line == border or "MEDIA TOOLS" in line
            color = "accent" if highlighted else "muted"
            self.print_fn(colorize(line, color, self.use_color))

    def status(self, kind: str, message: str) -> None:
        self.print_fn(style_status(kind, message, self.use_color))

    def output(self, message: str) -> None:
        lowered = message.lower()
        if message.startswith("["):
            self.print_fn(message)
        elif "erro" in lowered:
            self.status("error", message)
        elif "aviso" in lowered or "cpu" in lowered:
            self.status("warning", message)
        elif "salv" in lowered or "conclu" in lowered:
            self.status("success", message)
        else:
            self.status("info", message)
