import logging


def configure_logging(level: str = "INFO"):

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        filename="expense_tracker.log",
        encoding="utf-8"
    )
