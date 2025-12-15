from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEVICE_TYPES


class RenogyModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renogy Modbus."""

    VERSION = 1

    def __init__(self):
        self._host: str | None = None
        self._port: int | None = None
        self._slave: int | None = None
        self._name: str | None = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Step 1 – host, port, slave, name."""
        errors = {}

        if user_input is not None:
            self._host = user_input["host"]
            self._port = user_input["port"]
            self._slave = user_input["slave"]
            self._name = user_input["name"]

            # you could add basic validation here later
            return await self.async_step_device_type()

        schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("port", default=502): int,
                vol.Required("slave", default=1): int,
                vol.Required("name"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_device_type(self, user_input=None) -> FlowResult:
        """Step 2 – pick device type (smart battery etc)."""

        if user_input is not None:
            device_type = user_input["device_type"]
            return self.async_create_entry(
                title=self._name or "Renogy Modbus Device",
                data={
                    "host": self._host,
                    "port": self._port,
                    "slave": self._slave,
                    "name": self._name,
                    "device_type": device_type,
                },
            )

        choices = {key: cfg["name"] for key, cfg in DEVICE_TYPES.items()}

        schema = vol.Schema(
            {
                vol.Required("device_type"): vol.In(choices),
            }
        )

        return self.async_show_form(
            step_id="device_type",
            data_schema=schema,
        )
