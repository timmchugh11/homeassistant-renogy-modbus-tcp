from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DEVICE_TYPES
from .modbus_client import RenogyModbusClient
from .coordinator import RenogyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


# ================================================================
#   SETUP ENTRY
# ================================================================
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Renogy Modbus device from a config entry."""

    host = entry.data["host"]
    port = entry.data["port"]
    slave = entry.data["slave"]
    name = entry.data["name"]
    device_type = entry.data["device_type"]

    profile = DEVICE_TYPES.get(device_type)
    if profile is None:
        _LOGGER.error("Unknown device type: %s", device_type)
        return False

    # ------------------------------------------------------------
    # Create Modbus client
    # ------------------------------------------------------------
    client = RenogyModbusClient(
        host=host,
        port=port,
        slave=slave,
    )

    try:
        await client.connect()
        _LOGGER.info("Connected to Renogy device %s at %s:%s", name, host, port)
    except Exception as err:
        _LOGGER.error("Modbus connection failed: %s", err)
        return False

    # ------------------------------------------------------------
    # Create coordinator (polling every 5 seconds)
    # ------------------------------------------------------------
    coordinator = RenogyCoordinator(
        hass=hass,
        client=client,
        profile=profile,
        device_name=name,
        update_interval=5,
    )

    # Initial data load
    await coordinator.async_config_entry_first_refresh()

    # Store integration data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
        "profile": profile,
        "name": name,
    }

    # ------------------------------------------------------------
    # Register services (only once per HA instance)
    # ------------------------------------------------------------
    if not hass.services.has_service(DOMAIN, "set_max_charge_current"):
        _LOGGER.debug("Registering Renogy services")

        async def handle_set_max_charge_current(call: ServiceCall):
            """Set max charging current (A) for a DC-DC charger."""

            device_id = call.data.get("device_id")
            amps = call.data.get("current")

            if device_id is None or amps is None:
                _LOGGER.error("Missing device_id or current value")
                return

            # ------------------------------------------------------------------
            # Look up the device in Home Assistant's device registry
            # ------------------------------------------------------------------
            device_registry = dr.async_get(hass)
            device = device_registry.async_get(device_id)

            if not device:
                _LOGGER.error("Device %s not found in registry", device_id)
                return

            if not device.config_entries:
                _LOGGER.error("Device %s has no related config entries", device_id)
                return

            # Renogy devices only have one config entry
            entry_id = list(device.config_entries)[0]

            data = hass.data[DOMAIN].get(entry_id)
            if not data:
                _LOGGER.error(
                    "Config entry %s for device %s not found in hass.data",
                    entry_id, device_id
                )
                return

            profile = data["profile"]

            # Ensure it's a DC-DC charger
            if profile.get("type") != "dc_to_dc":
                _LOGGER.error("Device %s is not a DC-DC charger", device_id)
                return

            client: RenogyModbusClient = data["client"]
            name = data["name"]

            # Register for max charging current
            register = 0xE001
            scaled_value = int(amps * 100)

            _LOGGER.info(
                "Writing max charge current %s A (scaled %d) to charger %s",
                amps, scaled_value, name
            )

            try:
                await client.write_register(register, scaled_value)
            except Exception as err:
                _LOGGER.error("Failed writing current: %s", err)
                return

        hass.services.async_register(
            DOMAIN,
            "set_max_charge_current",
            handle_set_max_charge_current,
        )

    # ------------------------------------------------------------
    # Load platform(s)
    # ------------------------------------------------------------
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


# ================================================================
#   UNLOAD ENTRY
# ================================================================
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Renogy Modbus config entry."""
    data = hass.data[DOMAIN].pop(entry.entry_id)

    client: RenogyModbusClient = data["client"]
    await client.close()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
