import logging
import threading
import time

import serial

from app.config import settings


logger = logging.getLogger(__name__)


class PowerController:
    """
    Controls HM30 power through the microcontroller.

    Expected commands:
        ON
        OFF
        TEST

    Expected responses:
        ON_OK
        OFF_OK
        TEST_OK
    """

    def __init__(self) -> None:

        self.port = settings.power_port
        self.baudrate = settings.power_baudrate
        self.timeout = settings.power_timeout

        self._serial: serial.Serial | None = None
        self._lock = threading.Lock()

    # ==========================================
    # CONNECTION
    # ==========================================

    def connect(self) -> None:
        """
        Open serial connection to the power controller.
        """

        if self._serial and self._serial.is_open:
            return

        logger.info(
            "Connecting power controller: %s @ %s",
            self.port,
            self.baudrate,
        )

        try:

            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )

            # Some microcontrollers reset when serial opens.
            time.sleep(2)

            logger.info(
                "Power controller connected: %s",
                self.port,
            )

        except serial.SerialException as exc:

            self._serial = None

            logger.error(
                "Failed to connect power controller %s: %s",
                self.port,
                exc,
            )

            raise

    # ==========================================
    # DISCONNECT
    # ==========================================

    def disconnect(self) -> None:
        """
        Close serial connection.
        """

        if self._serial:

            try:
                if self._serial.is_open:
                    self._serial.close()

            except Exception as exc:

                logger.warning(
                    "Error closing power controller: %s",
                    exc,
                )

        self._serial = None

        logger.info("Power controller disconnected")

    # ==========================================
    # SEND COMMAND
    # ==========================================

    def send_command(
        self,
        command: str,
    ) -> str:

        with self._lock:

            try:

                self.connect()

                message = f"{command}\n"

                logger.info(
                    "POWER TX -> %s",
                    command,
                )

                self._serial.write(
                    message.encode("utf-8")
                )

                self._serial.flush()

                response = (
                    self._serial
                    .readline()
                    .decode(
                        "utf-8",
                        errors="ignore",
                    )
                    .strip()
                )

                logger.info(
                    "POWER RX <- %s",
                    response,
                )

                return response

            except Exception as exc:

                logger.error(
                    "Power controller communication error: %s",
                    exc,
                )

                self.disconnect()

                raise

    # ==========================================
    # ON
    # ==========================================

    def turn_on(self) -> str:

        return self.send_command("ON")

    # ==========================================
    # OFF
    # ==========================================

    def turn_off(self) -> str:

        return self.send_command("OFF")

    # ==========================================
    # TEST
    # ==========================================

    def test(self) -> str:

        return self.send_command("TEST")

    # ==========================================
    # STATUS
    # ==========================================

    def status(self) -> dict:

        connected = (
            self._serial is not None
            and self._serial.is_open
        )

        return {
            "port": self.port,
            "connected": connected,
            "baudrate": self.baudrate,
        }