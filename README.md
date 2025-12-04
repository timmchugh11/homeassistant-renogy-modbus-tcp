
# Renogy Modbus TCP Integration for Home Assistant

Custom Home Assistant integration that provides **full Modbus TCP support for Renogy devices**, including:
- Renogy **Smart Lithium Batteries (with RS485 Ports)**
- Renogy **DC-DC Chargers**

This integration exposes **all raw Modbus registers** as Home Assistant sensors, and includes **automatic scaling, bit decoding, human-readable states**, and optional **template helpers**.

## Features
- Reads all Renogy Modbus TCP registers
- Converts raw register data into battery and charger metrics
- High-resolution 32-bit register support
- Automatic scaling for Renogy formats
- Works entirely over Modbus TCP
- Template-friendly

## Installation
Copy the integration into your Home Assistant custom_components directory and restart Home Assistant.

## Configuration
Use the UI intergration to enter the IP, port Address and device

## Entities Created
Includes sensors for batteries and chargers such as:
- Voltage
- Current
- Temperature
- State of Charge
- Charger Status

## Contributing
PRs welcome!

## Support
Star the repo if helpful.
