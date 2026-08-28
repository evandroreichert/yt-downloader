import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path


class DownloadProgress:
    def __init__(self, print_fn=print):
        self.print_fn = print_fn
        self._last_percent = None

    def __call__(self, data: dict) -> None:
        status = data.get("status")
        if status == "finished":
            self.print_fn("Download concluído. Convertendo...")
            return
        if status != "downloading":
            return

        percent = data.get("_percent_str", "").strip()
        match = re.search(r"(\d+(?:\.\d+)?)", percent)
        integer_percent = int(float(match.group(1))) if match else None
        if integer_percent is not None and integer_percent == self._last_percent:
            return
        self._last_percent = integer_percent

        message = f"Baixando: {percent or 'em andamento'}"
        eta = data.get("_eta_str")
        if eta:
            message += f" | restante: {eta.strip()}"
        self.print_fn(message)


def configure_logging(enabled: bool, root: Path) -> logging.Logger:
    logger = logging.getLogger(f"media_tools.{hash(root.resolve())}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    if enabled:
        log_dir = root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_dir / "media-tools.log",
            maxBytes=1_000_000,
            backupCount=2,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
    else:
        handler = logging.NullHandler()
    logger.addHandler(handler)
    return logger
