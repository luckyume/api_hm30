import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    hm30_monitor,
    power_controller,
    router,
)
from app.logging_config import setup_logging


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Application startup and shutdown lifecycle.
    """

    # ==========================================
    # STARTUP
    # ==========================================

    logger.info(
        "======================================"
    )

    logger.info(
        "Starting Drone Control API"
    )

    logger.info(
        "======================================"
    )

    # Start HM30 MAVLink monitor
    hm30_monitor.start()

    logger.info(
        "Application startup completed"
    )

    yield

    # ==========================================
    # SHUTDOWN
    # ==========================================

    logger.info(
        "Application shutdown started"
    )

    hm30_monitor.stop()

    power_controller.disconnect()

    logger.info(
        "Application shutdown completed"
    )


# ==========================================
# LOGGING
# ==========================================

setup_logging()


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(
    title="Drone Control API",
    description=(
        "FastAPI service for HM30 control "
        "and MAVLink monitoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================
# ROUTES
# ==========================================

app.include_router(router)