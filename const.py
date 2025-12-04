DOMAIN = "renogy_modbus"

DEVICE_TYPES = {
    "smart_battery": {
        "name": "Smart Battery",
        "type": "battery",
        "sensors": [
            # Current
            {
                "key": "current",
                "name": "Current",
                "register": 0x13B2,
                "type": "int16",
                "scale": 0.01,
                "unit": "A",
            },

            # Voltage
            {
                "key": "voltage",
                "name": "Voltage",
                "register": 0x13B3,
                "type": "uint16",
                "scale": 0.1,
                "unit": "V",
            },

            # Capacity raw
            {
                "key": "cap_reg1",
                "name": "Capacity Reg1",
                "register": 0x13B4,
                "type": "uint16",
                "category": "diagnostic",
            },
            {
                "key": "cap_reg2",
                "name": "Capacity Reg2",
                "register": 0x13B5,
                "type": "uint16",
                "category": "diagnostic",
            },

            # Max capacity raw
            {
                "key": "maxcap_reg1",
                "name": "Max Capacity Reg1",
                "register": 0x13B6,
                "type": "uint16",
                "category": "diagnostic",
            },
            {
                "key": "maxcap_reg2",
                "name": "Max Capacity Reg2",
                "register": 0x13B7,
                "type": "uint16",
                "category": "diagnostic",
            },

            # Cycles raw
            {
                "key": "cycles",
                "name": "Cycles",
                "register": 0x13B8,
                "type": "uint16",
                "unit": "cycles",
            },

            # Raw cell temps
            {
                "key": "temp1",
                "name": "Cell 1 Temperature Raw",
                "register": 5018,
                "type": "int16",
                "scale": 0.1,
                "unit": "°C",
                "category": "diagnostic",
            },
            {
                "key": "temp2",
                "name": "Cell 2 Temperature Raw",
                "register": 5019,
                "type": "int16",
                "scale": 0.1,
                "unit": "°C",
                "category": "diagnostic",
            },
            {
                "key": "temp3",
                "name": "Cell 3 Temperature Raw",
                "register": 5020,
                "type": "int16",
                "scale": 0.1,
                "unit": "°C",
                "category": "diagnostic",
            },
            {
                "key": "temp4",
                "name": "Cell 4 Temperature Raw",
                "register": 5021,
                "type": "int16",
                "scale": 0.1,
                "unit": "°C",
                "category": "diagnostic",
            },
        ],

        "virtual_sensors": [
            {"key": "capacity_ah", "name": "Capacity", "unit": "Ah", "formula": "capacity_ah"},
            {"key": "max_capacity_ah", "name": "Max Capacity", "unit": "Ah", "formula": "max_capacity_ah"},
            {"key": "percentage", "name": "Percentage", "unit": "%", "formula": "percentage"},
            {"key": "remaining_wh", "name": "Remaining Wh", "unit": "Wh", "formula": "remaining_wh"},
            {"key": "temperature", "name": "Temperature", "unit": "°C", "formula": "average_temp"},
            {"key": "state", "name": "State", "formula": "charging_state"},
            {"key": "wattage", "name": "Wattage", "unit": "W", "formula": "wattage"},
        ],
    },

    "dc_to_dc": {
        "name": "DC-DC Charger (DCC50S / DCC30S / Smart Charger)",
        "type": "dc_to_dc",
        "sensors": [
            # -------------------------
            # Product information
            # -------------------------
            {"key": "modbus_address", "name": "Modbus Address", "register": 0x001A, "type": "uint16", "category": "diagnostic"},
            {"key": "rated_voltage_raw", "name": "Rated Voltage Raw", "register": 0x000A, "type": "uint16", "category": "diagnostic"},
            {"key": "set_current_raw", "name": "Set Current Raw", "register": 0xE001, "type": "uint16", "category": "diagnostic"},
            {"key": "serial_raw", "name": "Serial Raw", "register": 0x0018, "type": "uint32", "category": "diagnostic"},
            {"key": "software_raw", "name": "Software Raw", "register": 0x0014, "type": "uint32", "category": "diagnostic"},
            {"key": "hardware_raw", "name": "Hardware Raw", "register": 0x0016, "type": "uint32", "category": "diagnostic"},

            # -------------------------
            # Battery Side
            # -------------------------
            {"key": "batt_soc_raw", "name": "Battery SOC Raw", "register": 0x100, "type": "uint16", "category": "diagnostic"},
            {"key": "batt_voltage_raw", "name": "Battery Voltage Raw", "register": 0x101, "type": "uint16", "category": "diagnostic"},
            {"key": "batt_current_raw", "name": "Battery Current Raw", "register": 0x102, "type": "int16", "category": "diagnostic"},

            # -------------------------
            # Packed temperature (internal + probe)
            # -------------------------
            {"key": "temp_packed_raw", "name": "Temperature Packed Raw", "register": 0x103, "type": "uint16", "category": "diagnostic"},

            # -------------------------
            # Alternator Input
            # -------------------------
            {"key": "alt_voltage_raw", "name": "Alternator Voltage Raw", "register": 0x104, "type": "uint16", "category": "diagnostic"},
            {"key": "alt_current_raw", "name": "Alternator Current Raw", "register": 0x105, "type": "int16", "category": "diagnostic"},
            {"key": "alt_power_raw", "name": "Alternator Power Raw", "register": 0x106, "type": "int16", "category": "diagnostic"},

            # -------------------------
            # Hookup / PV Input
            # -------------------------
            {"key": "pv_voltage_raw", "name": "Hookup Voltage Raw", "register": 0x107, "type": "uint16", "category": "diagnostic"},
            {"key": "pv_current_raw", "name": "Hookup Current Raw", "register": 0x108, "type": "int16", "category": "diagnostic"},

            # -------------------------
            # Energy
            # -------------------------
            {"key": "energy_today_raw", "name": "Energy Today Raw", "register": 0x113, "type": "uint16", "category": "diagnostic"},
            {"key": "energy_total_raw", "name": "Energy Total Raw", "register": 0x11C, "type": "uint32", "category": "diagnostic"},

            # -------------------------
            # State / Alarms
            # -------------------------
            {"key": "state_raw", "name": "State Raw", "register": 0x120, "type": "uint16", "category": "diagnostic"},
            {"key": "alarm_a_raw", "name": "Alarm A Raw", "register": 0x121, "type": "uint16", "category": "diagnostic"},
            {"key": "alarm_b_raw", "name": "Alarm B Raw", "register": 0x122, "type": "uint16", "category": "diagnostic"},
        ],

        "virtual_sensors": [
            # -------- Rated voltage + current --------
            {"key": "rated_voltage", "name": "Rated Voltage", "unit": "V", "formula": "rated_voltage", "precision": 0},
            {"key": "rated_current", "name": "Rated Current",   "unit": "A", "formula": "rated_current", "precision": 0},

            # -------- Battery side --------
            {"key": "batt_soc", "name": "Battery SOC", "unit": "%", "formula": "batt_soc"},
            {"key": "batt_voltage", "name": "Battery Voltage", "unit": "V", "formula": "batt_voltage", "precision": 1},
            {"key": "batt_current", "name": "Battery Current", "unit": "A", "formula": "batt_current", "precision": 2},

            # -------- Temperatures --------
            {"key": "temp_internal", "name": "Internal Temperature", "unit": "°C", "formula": "temp_internal"},
            {"key": "temp_probe", "name": "Probe Temperature", "unit": "°C", "formula": "temp_probe"},

            # -------- Alternator input --------
            {"key": "alt_voltage", "name": "Alternator Voltage", "unit": "V", "formula": "alt_voltage", "precision": 1},
            {"key": "alt_current", "name": "Alternator Current", "unit": "A", "formula": "alt_current", "precision": 2},
            {"key": "alt_power", "name": "Alternator Power", "unit": "W", "formula": "alt_power"},

            # -------- PV / Hookup --------
            {"key": "pv_voltage", "name": "Hookup Voltage", "unit": "V", "formula": "pv_voltage", "precision": 1},
            {"key": "pv_current", "name": "Hookup Current", "unit": "A", "formula": "pv_current", "precision": 2},
            {"key": "pv_power", "name": "Hookup Power", "unit": "W", "formula": "pv_power"},

            # -------- Energy --------
            {"key": "energy_today", "name": "Energy Today", "unit": "Wh", "formula": "energy_today"},
            {"key": "energy_total", "name": "Energy Total", "unit": "Wh", "formula": "energy_total"},

            # -------- State --------
            {"key": "charger_state", "name": "Charger State", "formula": "charger_state"},
            {"key": "alarms", "name": "Charger Alarms", "formula": "alarms"},

            # ------- Control ---------
            {"key": "max_charge_current", "name": "Max Charge Current", "unit": "A", "formula": "max_charge_current", "precision": 1}

        ],
    }
}
