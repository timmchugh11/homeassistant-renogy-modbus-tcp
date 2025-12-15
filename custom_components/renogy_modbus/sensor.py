from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# ============================================================
#  COMMON UTILITY FORMULAS (used by Smart Battery)
# ============================================================

def combine_capacity(reg1, reg2):
    """Renogy special 32-bit capacity combine."""
    if reg1 is None or reg2 is None:
        return None
    raw = reg1 * 32768 + (reg2 // 2)
    return raw * 0.002


def percentage(cap, maxcap):
    if cap is None or maxcap is None or maxcap == 0:
        return None
    pct = (cap / maxcap) * 100
    return max(0, min(100, pct))


def wattage(voltage, current):
    if current is None or voltage is None:
        return None
    return current * voltage


def remaining_wh(capacity_ah, voltage):
    if capacity_ah is None or voltage is None:
        return None
    return capacity_ah * voltage


def average_temp(t1, t2, t3, t4):
    values = [v for v in [t1, t2, t3, t4] if v is not None]
    return (sum(values) / len(values)) if values else None


def charging_state(current):
    if current is None:
        return None
    if current < 0:
        return "Discharging"
    if current > 0:
        return "Charging"
    return "Idle"


# ============================================================
#  DC-DC CHARGER FORMULA ENGINE
# ============================================================

def rated_voltage(d):
    raw = d.get("rated_voltage_raw")
    return raw // 256 if raw is not None else None


def rated_current(d):
    raw = d.get("rated_voltage_raw")
    return raw % 256 if raw is not None else None


def batt_soc(d):
    return d.get("batt_soc_raw")


def batt_voltage(d):
    raw = d.get("batt_voltage_raw")
    return raw * 0.1 if raw is not None else None


def batt_current(d):
    raw = d.get("batt_current_raw")
    return raw * 0.01 if raw is not None else None


def temp_internal(d):
    raw = d.get("temp_packed_raw")
    return raw // 256 if raw is not None else None


def temp_probe(d):
    raw = d.get("temp_packed_raw")
    return raw % 256 if raw is not None else None


def alt_voltage(d):
    raw = d.get("alt_voltage_raw")
    return raw * 0.1 if raw is not None else None


def alt_current(d):
    raw = d.get("alt_current_raw")
    return raw * 0.01 if raw is not None else None


def alt_power(d):
    return d.get("alt_power_raw")


def pv_voltage(d):
    raw = d.get("pv_voltage_raw")
    return raw * 0.1 if raw is not None else None


def pv_current(d):
    raw = d.get("pv_current_raw")
    return raw * 0.01 if raw is not None else None


def pv_power(d):
    v = pv_voltage(d)
    c = pv_current(d)
    if v is None or c is None:
        return None
    return v * c


def energy_today(d):
    return d.get("energy_today_raw")


def energy_total(d):
    return d.get("energy_total_raw")


def charger_state(d):
    raw = d.get("state_raw")
    mapping = {
        0: "Not Charging",
        2: "MPPT Charging",
        3: "Equalization",
        4: "Boost Charging",
        5: "Float Charging",
        6: "Current Limited",
        8: "Direct Charging",
    }
    return mapping.get(raw, f"Unknown ({raw})")


def alarms(d):
    a = d.get("alarm_a_raw", 0)
    b = d.get("alarm_b_raw", 0)
    msgs = []

    # Alarm A
    if a & (1 << 4): msgs.append("Controller Inside Over Temp")
    if a & (1 << 5): msgs.append("Alternator Input Over Current")
    if a & (1 << 8): msgs.append("Alternator Input Over Voltage")
    if a & (1 << 9): msgs.append("Starter Battery Reverse Polarity")
    if a & (1 << 10): msgs.append("BMS Over Charge Protection")
    if a & (1 << 11): msgs.append("Low Temperature Cutoff")

    # Alarm B
    if b & (1 << 1): msgs.append("Battery Over Discharged")
    if b & (1 << 2): msgs.append("Battery Over Charged")
    if b & (1 << 5): msgs.append("Controller Inside Temp Too High")
    if b & (1 << 6): msgs.append("Battery Over Temp")
    if b & (1 << 7): msgs.append("Hookup Input Too High")
    if b & (1 << 10): msgs.append("Hookup Input Over Voltage")
    if b & (1 << 12): msgs.append("Hookup Reverse Polarity")

    return ", ".join(msgs) if msgs else "OK"

def max_charge_current(d):
    raw = d.get("set_current_raw")  # your original raw register
    return raw * 0.01 if raw is not None else None


# ============================================================
#  FORMULA MAP (Smart Battery + DCDC)
# ============================================================

FORMULAS = {
    # Smart battery
    "capacity_ah": lambda d: combine_capacity(d.get("cap_reg1"), d.get("cap_reg2")),
    "max_capacity_ah": lambda d: combine_capacity(d.get("maxcap_reg1"), d.get("maxcap_reg2")),
    "percentage": lambda d: percentage(
        combine_capacity(d.get("cap_reg1"), d.get("cap_reg2")),
        combine_capacity(d.get("maxcap_reg1"), d.get("maxcap_reg2")),
    ),
    "wattage": lambda d: wattage(d.get("voltage"), d.get("current")),
    "remaining_wh": lambda d: remaining_wh(
        combine_capacity(d.get("cap_reg1"), d.get("cap_reg2")),
        d.get("voltage")
    ),
    "average_temp": lambda d: average_temp(d.get("temp1"), d.get("temp2"), d.get("temp3"), d.get("temp4")),
    "charging_state": lambda d: charging_state(d.get("current")),

    # DC-DC charger formulas
    "rated_voltage": rated_voltage,
    "rated_current": rated_current,
    "batt_soc": batt_soc,
    "batt_voltage": batt_voltage,
    "batt_current": batt_current,
    "temp_internal": temp_internal,
    "temp_probe": temp_probe,
    "alt_voltage": alt_voltage,
    "alt_current": alt_current,
    "alt_power": alt_power,
    "pv_voltage": pv_voltage,
    "pv_current": pv_current,
    "pv_power": pv_power,
    "energy_today": energy_today,
    "energy_total": energy_total,
    "charger_state": charger_state,
    "alarms": alarms,

    # Controls
    "max_charge_current": max_charge_current,

}



# ============================================================
#  RAW SENSOR ENTITY
# ============================================================

class RenogyRawSensor(CoordinatorEntity, SensorEntity):
    """Representation of a raw Modbus register (scaled by coordinator)."""

    def __init__(self, coordinator, device_name, key, cfg):
        super().__init__(coordinator)
        self._key = key
        self._cfg = cfg
        self._dev_name = device_name

        self._attr_name = f"{device_name} {cfg['name']}"
        self._attr_unique_id = f"{device_name}_{key}"
        self._attr_native_unit_of_measurement = cfg.get("unit")

        if cfg.get("category") == "diagnostic":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._dev_name)},
            "name": self._dev_name,
            "manufacturer": "Renogy",
            "model": self.coordinator.profile.get("name", "Renogy Device"),
        }


# ============================================================
#  VIRTUAL SENSOR ENTITY
# ============================================================

class RenogyVirtualSensor(CoordinatorEntity, SensorEntity):
    """Representation of a computed / derived sensor."""

    def __init__(self, coordinator, device_name, key, cfg):
        super().__init__(coordinator)
        self._key = key
        self._cfg = cfg
        self._dev_name = device_name

        self._attr_name = f"{device_name} {cfg['name']}"
        self._attr_unique_id = f"{device_name}_{key}"
        self._attr_native_unit_of_measurement = cfg.get("unit")

    @property
    def native_value(self):
        d = self.coordinator.data
        formula = self._cfg["formula"]

        try:
            func = FORMULAS.get(formula)
            if not func:
                return None

            val = func(d)

            # precision handling
            precision = self._cfg.get("precision")
            if precision is not None and val is not None:
                val = round(val, precision)

            return val

        except Exception as e:
            _LOGGER.error("Error computing virtual sensor '%s': %s", self._key, e)
            return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._dev_name)},
            "name": self._dev_name,
            "manufacturer": "Renogy",
            "model": self.coordinator.profile.get("name", "Renogy Device"),
        }


# ============================================================
#  ENTITY LOADER
# ============================================================

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up all sensors for this integration."""
    data = hass.data[DOMAIN][entry.entry_id]

    coordinator = data["coordinator"]
    profile = data["profile"]
    device_name = entry.data["name"]

    entities = []

    for sensor_cfg in profile["sensors"]:
        entities.append(RenogyRawSensor(coordinator, device_name, sensor_cfg["key"], sensor_cfg))

    for vcfg in profile.get("virtual_sensors", []):
        entities.append(RenogyVirtualSensor(coordinator, device_name, vcfg["key"], vcfg))

    async_add_entities(entities)
