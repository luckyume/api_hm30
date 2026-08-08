import logging
import threading
import time
from typing import Any

from pymavlink import mavutil

from app.config import settings


logger = logging.getLogger(__name__)


class HM30Monitor:
    """
    Background MAVLink monitor for HM30.

    The monitor continuously reads MAVLink messages
    from the HM30 USB serial connection.
    """

    def __init__(self) -> None:

        self.port = settings.hm30_port
        self.baudrate = settings.hm30_baudrate

        self.heartbeat_timeout = (
            settings.hm30_heartbeat_timeout
        )

        self._connection = None
        self._thread: threading.Thread | None = None

        self._running = False

        self._lock = threading.Lock()

        # ==============================
        # STATUS
        # ==============================

        self._connected = False

        self._last_message_time: float | None = None
        self._last_heartbeat_time: float | None = None

        self._last_message_type: str | None = None

        self._system_id: int | None = None
        self._component_id: int | None = None

        self._message_count = 0

    # ==========================================
    # START
    # ==========================================

    def start(self) -> None:

        if self._running:
            logger.warning(
                "HM30 monitor already running"
            )
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="HM30-Monitor",
            daemon=True,
        )

        self._thread.start()

        logger.info(
            "HM30 monitor started: %s @ %s",
            self.port,
            self.baudrate,
        )

    # ==========================================
    # STOP
    # ==========================================

    def stop(self) -> None:

        logger.info("Stopping HM30 monitor")

        self._running = False

        if self._thread:

            self._thread.join(
                timeout=3
            )

        self._close_connection()

        logger.info("HM30 monitor stopped")

    # ==========================================
    # CONNECTION
    # ==========================================

    def _connect(self) -> bool:

        try:

            logger.info(
                "Connecting HM30: %s @ %s",
                self.port,
                self.baudrate,
            )

            self._connection = (
                mavutil.mavlink_connection(
                    self.port,
                    baud=self.baudrate,
                    autoreconnect=False,
                )
            )

            self._connected = True

            logger.info(
                "HM30 serial connected: %s",
                self.port,
            )

            return True

        except Exception as exc:

            self._connected = False
            self._connection = None

            logger.error(
                "HM30 connection failed: %s",
                exc,
            )

            return False

    # ==========================================
    # CLOSE
    # ==========================================

    def _close_connection(self) -> None:

        if self._connection:

            try:
                self._connection.close()

            except Exception as exc:

                logger.warning(
                    "Error closing HM30 connection: %s",
                    exc,
                )

        self._connection = None
        self._connected = False

    # ==========================================
    # MONITOR LOOP
    # ==========================================

    def _monitor_loop(self) -> None:

        logger.info(
            "HM30 background monitor running"
        )

        while self._running:

            if self._connection is None:

                connected = self._connect()

                if not connected:

                    time.sleep(2)

                    continue

            try:

                message = (
                    self._connection.recv_match(
                        blocking=True,
                        timeout=1,
                    )
                )

                if message is None:

                    continue

                self._process_message(message)

            except Exception as exc:

                logger.error(
                    "HM30 MAVLink read error: %s",
                    exc,
                )

                self._close_connection()

                time.sleep(2)

    # ==========================================
    # PROCESS MAVLINK
    # ==========================================

    def _process_message(
        self,
        message: Any,
    ) -> None:

        now = time.time()

        message_type = message.get_type()

        with self._lock:

            self._last_message_time = now

            self._last_message_type = (
                message_type
            )

            self._message_count += 1

            self._system_id = (
                message.get_srcSystem()
            )

            self._component_id = (
                message.get_srcComponent()
            )

            if message_type == "HEARTBEAT":

                self._last_heartbeat_time = now

        logger.debug(
            "HM30 MAVLink RX: %s",
            message_type,
        )

        if message_type == "HEARTBEAT":

            logger.debug(
                "HM30 HEARTBEAT received "
                "system=%s component=%s",
                self._system_id,
                self._component_id,
            )

    # ==========================================
    # STATUS
    # ==========================================

    def get_status(self) -> dict:

        now = time.time()

        with self._lock:

            if self._last_message_time:

                last_message_age = (
                    now
                    - self._last_message_time
                )

            else:

                last_message_age = None

            if self._last_heartbeat_time:

                heartbeat_age = (
                    now
                    - self._last_heartbeat_time
                )

            else:

                heartbeat_age = None

            online = (
                heartbeat_age is not None
                and
                heartbeat_age
                <= self.heartbeat_timeout
            )

            return {
                "port": self.port,
                "baudrate": self.baudrate,
                "serial_connected": self._connected,

                "online": online,

                "last_message_type": (
                    self._last_message_type
                ),

                "last_message_age": (
                    round(
                        last_message_age,
                        2,
                    )
                    if last_message_age
                    is not None
                    else None
                ),

                "heartbeat_age": (
                    round(
                        heartbeat_age,
                        2,
                    )
                    if heartbeat_age
                    is not None
                    else None
                ),

                "system_id": self._system_id,
                "component_id": self._component_id,

                "message_count": (
                    self._message_count
                ),
            }