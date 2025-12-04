from __future__ import annotations

import asyncio
import logging

from .vendor.pymodbus.client import AsyncModbusTcpClient
from .vendor.pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)


class RenogyModbusClient:
    """Async Modbus TCP client using vendored pymodbus 3.11.4."""

    def __init__(self, host: str, port: int, slave: int):
        self._host = host
        self._port = port
        self._slave = slave
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Connect to the Modbus TCP device."""
        _LOGGER.debug("Connecting to Modbus %s:%s", self._host, self._port)

        try:
            # pymodbus 3.11.x uses keyword-only args for AsyncModbusTcpClient
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
            )

            await self._client.connect()

            if not self._client.connected:
                raise ConnectionError("Failed to connect to Modbus device")

            _LOGGER.info("Connected to Modbus device at %s:%s", self._host, self._port)

        except Exception as err:
            _LOGGER.error("Modbus connection error: %s", err)
            raise

    async def close(self):
        """Close the connection."""
        if self._client:
            await self._client.close()
            _LOGGER.info("Closed Modbus connection")
            self._client = None

    async def read_register(self, register: int, count: int = 1):
        """
        Read holding registers.

        Returns:
            list[int] | None: list of register values, or None on error.
        """
        if not self._client:
            await self.connect()

        async with self._lock:
            try:
                # pymodbus 3.11.x uses 'unit' for the slave / unit id
                resp = await self._client.read_holding_registers(
                    address=register,
                    count=count,
                    device_id=self._slave,
                )
            except ModbusException as err:
                _LOGGER.error("Modbus error on register %s: %s", register, err)
                return None
            except Exception as err:
                _LOGGER.error("Unexpected Modbus error on register %s: %s", register, err)
                return None

        if not resp or resp.isError():
            _LOGGER.error("Bad Modbus response for register %s: %s", register, resp)
            return None

        return resp.registers

    async def read_int(self, register: int) -> int | None:
        """Read a single register and return its integer value."""
        values = await self.read_register(register, 1)
        if not values:
            return None
        return values[0]

    async def write_register(self, register: int, value: int) -> bool:
        """
        Write a single holding register.

        Args:
            register: register address
            value: integer value to write

        Returns:
            True if success, False otherwise.
        """
        if not self._client:
            await self.connect()

        async with self._lock:
            try:
                resp = await self._client.write_registers(
                    address=register,
                    values=[value],
                    device_id=self._slave,
                )
            except ModbusException as err:
                _LOGGER.error("Modbus write error at %s: %s", register, err)
                return False
            except Exception as err:
                _LOGGER.error("Unexpected Modbus write error at %s: %s", register, err)
                return False

        if not resp or resp.isError():
            _LOGGER.error("Bad Modbus write response for register %s: %s", register, resp)
            return False

        return True
