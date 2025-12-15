from __future__ import annotations

import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class RenogyCoordinator(DataUpdateCoordinator):
    """Coordinator for polling Modbus data from a Renogy device."""

    def __init__(self, hass, client, profile, device_name, update_interval):
        super().__init__(
            hass,
            _LOGGER,
            name=f"Renogy {device_name}",
            update_interval=timedelta(seconds=update_interval),
        )

        self.client = client
        self.profile = profile
        self.device_name = device_name

    async def _async_update_data(self):
        """Fetch data from Modbus and return cleaned, scaled values."""

        result = {}

        try:
            for sensor in self.profile["sensors"]:

                key = sensor["key"]
                reg = sensor["register"]
                count = sensor.get("count", 1)
                reg_type = sensor.get("type")
                scale = sensor.get("scale")

                # Read register(s)
                raw = await self.client.read_register(reg, count=count)

                if raw is None:
                    _LOGGER.warning(
                        "Failed to read register 0x%04X for key '%s'",
                        reg, key
                    )
                    result[key] = None
                    continue

                value = raw[0]

                # Signed 16-bit conversion
                if reg_type == "int16" and value > 0x7FFF:
                    value -= 0x10000

                # Apply scale
                if scale:
                    value = value * scale

                result[key] = value

            return result

        except Exception as e:
            _LOGGER.error("Unexpected Modbus update failure: %s", e)
            raise
