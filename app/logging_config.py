import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.
    """

    level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )