# RG-15 Rain Sensor for Raspberry Pi Pico

MicroPython driver for the Hydreon RG-15 Industrial-Grade Optical Rain Gauge.

## Hardware

- **Sensor:** Hydreon RG-15 (114992321)
- **Microcontroller:** Raspberry Pi Pico / Pico W
- **Interface:** UART (9600 baud)

### Wiring

| RG-15 Pin | Pico Pin | Description |
|-----------|----------|-------------|
| VCC | VSYS (5V) | Power (5-15V) |
| GND | GND | Ground |
| OUT (TX) | GP1 (RX) | Sensor data output |
| IN (RX) | GP0 (TX) | Commands to sensor |

## Files

| File | Description |
|------|-------------|
| `main.py` | Standard monitor - polls sensor at configurable interval |
| `main_battery_saver.py` | Battery mode - uses sleep between readings |
| `rg15_utility.py` | Interactive utility for testing and configuration |
| `config.py` | All settings in one place |
| `RG15_SENSOR_GUIDE.md` | Detailed sensor documentation |

## Quick Start

1. Copy all `.py` files to your Pico
2. Edit `config.py` to adjust settings
3. The Pico will run `main.py` automatically on boot

To use battery saver mode instead:
```python
# Rename on Pico:
# main.py -> main_standard.py
# main_battery_saver.py -> main.py
```

## Configuration

Edit `config.py` to customize:

```python
# Debug mode - shows raw sensor output
DEBUG = False

# Polling interval in seconds (main.py)
POLL_INTERVAL = 15

# Startup timing
BOOT_DELAY = 2        # Wait for sensor power-up
MAX_RETRIES = 5       # Connection attempts
RETRY_DELAY = 1       # Between retries

# UART pins
UART_ID = 0
UART_BAUD = 9600
TX_PIN = 0
RX_PIN = 1

# Battery saver settings (main_battery_saver.py)
BATTERY_POLL_MINUTES = 5   # Normal poll interval
RAIN_POLL_MINUTES = 1      # Poll faster when raining
SLEEP_MODE = "light"       # "light" or "deep"
LED_ENABLED = False        # LED indicator (causes errors on Pico W)
```

## Output

### Standard Mode (main.py)
```
RG-15 Rain Sensor Monitor
Initializing sensor...
Sensor connected!
Polling every 15 seconds...
---
Acc: 0.000 in | Event: 0.000 in | Total: 0.315 in | Rate: 0.000 in/hr
Acc: 0.001 in | Event: 0.001 in | Total: 0.316 in | Rate: 0.025 in/hr
```

### Battery Saver Mode (main_battery_saver.py)
```
RG-15 Battery Saver Mode
Initializing sensor...
Sensor connected!
Poll interval: 5 min
Sleep mode: light
---
Acc: 0.000 in | Event: 0.000 in | Total: 0.315 in | Rate: 0.000 in/hr
Light sleep for 5 min...
```

When rain is detected, it automatically polls more frequently.

## Utility Tool

Run `rg15_utility.py` for interactive sensor control:

```
==================================================
        RG-15 RAIN SENSOR UTILITY
==================================================

  DATA
  ------------------------------
    1  [R]   Read current data
    2  [A]   Read accumulator only
    3  [K]   Reset accumulator (set to 0)

  MODE
  ------------------------------
    4  [P]   Polling mode
    5  [C]   Continuous mode

  UNITS
  ------------------------------
    6  [M]   Metric (mm)
    7  [I]   Imperial (inches)

  RESOLUTION
  ------------------------------
    8  [H]   High resolution (0.01mm)
    9  [L]   Low resolution (0.2mm)

  SYSTEM
  ------------------------------
    0  [O]   Show current settings
    b  [B]   Reboot sensor

  UTILITY
  ------------------------------
    t        Test mode (poll every 2 sec)
    q        Quit
```

## Sensor Commands

Send these commands directly via UART:

| Command | Description |
|---------|-------------|
| `R` | Read current rain data |
| `K` | Reset accumulator to zero |
| `P` | Set polling mode (default) |
| `C` | Set continuous mode |
| `M` | Set metric units (mm) |
| `I` | Set imperial units (inches) |
| `H` | High resolution (0.01mm) |
| `L` | Low resolution (0.2mm) |
| `O` | Show current settings |
| `B` | Reboot sensor |

## Data Fields

| Field | Description |
|-------|-------------|
| `Acc` | Accumulated rain since last reset |
| `EventAcc` | Rain during current event |
| `TotalAcc` | Lifetime total (non-resettable) |
| `RInt` | Rain intensity (rate) |

## Power Consumption

| Mode | Current |
|------|---------|
| Active | ~25-40mA |
| Light sleep | ~1.3mA |
| Deep sleep | ~0.8mA |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No response | Check TX/RX wiring (they cross over) |
| CYW43 errors | Set `LED_ENABLED = False` in config.py |
| Garbled output | Verify baud rate is 9600 |
| Always zero | Normal if no rain - drip water to test |
| "EmSat" message | Emitter saturated - clean the lens |

## Pico W Notes

The Pico W's LED is controlled through the WiFi chip (CYW43). This causes error messages if you try to use the LED without initializing WiFi. Set `LED_ENABLED = False` in config.py to avoid these errors.

WiFi can be enabled later for data transmission - the code is structured to support this.

## License

MIT
