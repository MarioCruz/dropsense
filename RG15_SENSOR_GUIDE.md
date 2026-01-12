# Hydreon RG-15 Rain Sensor Guide

## Overview

The RG-15 is an industrial-grade optical rain gauge that uses infrared light to detect water droplets on its lens. Unlike traditional tipping bucket gauges, it has no moving parts and can detect very light rain.

**Model:** Industrial-Grade Optical Rain Gauge RG-15 (114992321)
**Manufacturer:** Hydreon

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Supply Voltage | 5-15V DC |
| Current (active) | ~2.5mA typical |
| Current (sleep) | ~0.4mA |
| Interface | UART (RS232 levels or 3.3V TTL) |
| Baud Rate | 9600 (default) |
| Data Format | 8 bits, no parity, 1 stop bit |
| Resolution | 0.01mm (high res) or 0.2mm (low res) |

---

## Wiring

```
RG-15 Pin    ->    Pico Pin
---------------------------------
VCC          ->    5V (or VSYS)
GND          ->    GND
OUT (TX)     ->    GP1 (RX)
IN  (RX)     ->    GP0 (TX)  [optional, only needed for commands]
```

**Note:** The RG-15 can output RS232 levels (+/-12V) or TTL (3.3V). Make sure your unit is set to TTL mode if connecting directly to a Pico, or use a level shifter.

---

## Serial Commands

All commands are single characters followed by a newline (`\n`).

### Data Commands

| Command | Description |
|---------|-------------|
| `R` | **Read** - Request current rain data. Returns accumulated rain and intensity. |
| `K` | **Kill accumulator** - Reset the accumulated rain counter to zero. |
| `A` | **Read accumulator** - Get accumulated rain since last reset. |

### Configuration Commands

| Command | Description |
|---------|-------------|
| `O` | **Output settings** - Display current configuration. |
| `P` | **Polling mode** - Sensor only sends data when polled with `R`. (Default) |
| `C` | **Continuous mode** - Sensor sends data automatically when rain is detected. |
| `H` | **High resolution** - 0.01mm resolution. |
| `L` | **Low resolution** - 0.2mm resolution (better noise immunity). |
| `I` | **Imperial units** - Output in inches. |
| `M` | **Metric units** - Output in millimeters. (Default) |

### System Commands

| Command | Description |
|---------|-------------|
| `B` | **Reboot** - Restart the sensor. |
| `?` | **Help** - Display available commands. |

---

## Response Format

When you send `R`, the sensor returns a line like:

```
Acc 0.00 mm, EventAcc 0.00 mm, TotalAcc 0.00 mm, RInt 0.00 mmph
```

### Response Fields

| Field | Description |
|-------|-------------|
| `Acc` | Accumulated rain since last `K` command (resettable) |
| `EventAcc` | Rain accumulated during current rain event |
| `TotalAcc` | Total lifetime accumulation (non-resettable) |
| `RInt` | Rain intensity in mm/hour |

**Note:** Exact field names may vary by firmware version. Some units output `mm=`, `in=`, `rate=` format.

---

## Operating Modes

### Polling Mode (Default)

- Sensor waits for `R` command
- Best for battery-powered applications
- You control when to check for rain

```python
uart.write(b'R\n')
time.sleep_ms(100)
response = read_line()
```

### Continuous Mode

- Sensor automatically sends data when rain state changes
- Good for always-on applications
- Enable with `C` command

```python
uart.write(b'C\n')  # Enable continuous mode (one time)
```

---

## Example Code Snippets

### Poll the sensor

```python
uart.write(b'R\n')
time.sleep_ms(100)
line = read_line(1000)
print(line)
```

### Reset accumulator

```python
uart.write(b'K\n')
```

### Switch to continuous mode

```python
uart.write(b'C\n')
```

### Switch to metric units

```python
uart.write(b'M\n')
```

### Check current settings

```python
uart.write(b'O\n')
time.sleep_ms(100)
print(read_line(1000))
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No response | Check wiring. TX on sensor goes to RX on Pico (GP1). |
| Garbled output | Verify baud rate is 9600. Check for voltage level mismatch. |
| Only responds when moved | Sensor is in continuous mode and lens needs cleaning, OR you're not sending the `R` command. |
| Readings stuck at 0 | Normal if no rain. Try dripping water on lens to test. |
| Very noisy readings | Try low resolution mode (`L` command). |

---

## Power Saving Tips

1. Use **polling mode** (`P`) instead of continuous
2. Increase polling interval (e.g., every 5 minutes instead of every second)
3. Use Pico's `lightsleep()` or `deepsleep()` between readings
4. Typical battery life with 5-minute polling: several months on 3x AA batteries

---

## Resources

- [Hydreon RG-15 Datasheet](https://rainsensors.com/products/rg-15/)
- [RG-15 Technical Manual](https://rainsensors.com/rg-15-manual/)
