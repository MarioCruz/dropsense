"""
RG-15 Rain Sensor - Battery Saver Mode
Uses sleep modes to minimize power consumption.
"""

from machine import UART, Pin, lightsleep, deepsleep
import time
import config

# UART setup from config
uart = UART(config.UART_ID, baudrate=config.UART_BAUD, bits=8, parity=None, stop=1,
            tx=Pin(config.TX_PIN), rx=Pin(config.RX_PIN))

# LED indicator - Pico W requires network module for onboard LED
# Disabled by default to avoid CYW43 errors - enable in config.py when needed
led = None
if getattr(config, 'LED_ENABLED', False):
    try:
        import network
        # Pico W - LED is controlled via CYW43 WiFi chip
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)  # Keep WiFi off for now but LED will work
        led = Pin("LED", Pin.OUT)
    except:
        try:
            # Regular Pico - LED is just a GPIO pin
            led = Pin(25, Pin.OUT)
        except:
            led = None

MAX_LINE_LENGTH = 256  # Prevent buffer overflow

def read_line(timeout_ms=500):
    """Read a line from UART with timeout and buffer protection."""
    start = time.ticks_ms()
    buf = b""
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        if uart.any():
            b = uart.read(1)
            if b:
                if b in (b'\n', b'\r'):
                    if buf:
                        return buf.decode('utf-8', 'ignore').strip()
                else:
                    buf += b
                    if len(buf) > MAX_LINE_LENGTH:
                        return buf.decode('utf-8', 'ignore').strip()
        else:
            time.sleep_ms(5)
    return buf.decode('utf-8', 'ignore').strip() if buf else None

def parse_rg15(line: str):
    """Parse RG-15 response - handles multiple firmware formats."""
    if not line:
        return {}

    data = {}

    # Format 1: "Key=Value" (some firmware versions)
    for token in line.split():
        if '=' in token:
            k, v = token.split('=', 1)
            try:
                data[k] = float(v)
            except ValueError:
                data[k] = v

    # Format 2: "Acc 0.000 in, EventAcc 0.000 in, ..." (your firmware)
    if not data and 'Acc' in line:
        parts = line.replace(',', '').split()
        i = 0
        while i < len(parts) - 1:
            key = parts[i]
            if key in ('Acc', 'EventAcc', 'TotalAcc', 'RInt'):
                try:
                    data[key] = float(parts[i + 1])
                except ValueError:
                    pass
            i += 1

    return data

def is_diagnostic_message(line: str) -> bool:
    """Check if line is a diagnostic/status message to skip."""
    skip_patterns = ('overlow', 'overflow', '----', 'SW ')
    return any(p in line for p in skip_patterns)

def blink(times=1):
    """Quick LED blink to show activity."""
    if led is None:
        return
    for _ in range(times):
        led.on()
        time.sleep_ms(50)
        led.off()
        time.sleep_ms(50)

def poll_sensor():
    """Poll sensor, return (data dict, raw line, unit info)."""
    # Flush any stale data
    while uart.any():
        uart.read()

    # Request reading
    uart.write(b'R\n')
    time.sleep_ms(100)

    # Read multiple lines
    for _ in range(3):
        line = read_line(500)
        if not line:
            continue

        # Skip diagnostic messages
        if is_diagnostic_message(line):
            continue

        # Skip status alerts but log them
        if 'EmSat' in line:
            print("ALERT: Emitter Saturated")
            continue

        # Parse data
        data = parse_rg15(line)
        if data:
            # Detect units
            unit = 'in' if ' in' in line or 'iph' in line else 'mm'
            rate_unit = 'in/hr' if 'iph' in line else 'mm/hr'
            return data, line, unit, rate_unit

    return None, None, None, None

def go_to_sleep(minutes):
    """Put the Pico to sleep to save battery."""
    ms = minutes * 60 * 1000

    if config.SLEEP_MODE == "deep":
        print(f"Deep sleep for {minutes} min...")
        deepsleep(ms)
    else:
        print(f"Light sleep for {minutes} min...")
        lightsleep(ms)

# ======================
# Startup sequence
# ======================
print("RG-15 Battery Saver Mode")
print("Initializing sensor...")

# Wait for sensor to power up
time.sleep(config.BOOT_DELAY)

# Flush any startup messages
while uart.any():
    uart.read()

# Try to get a response from sensor
sensor_ready = False
for attempt in range(1, config.MAX_RETRIES + 1):
    if config.DEBUG:
        print(f"  Attempt {attempt}/{config.MAX_RETRIES}...")

    uart.write(b'R\n')
    time.sleep_ms(200)

    line = read_line(1000)
    if line and 'Acc' in line:
        sensor_ready = True
        print("Sensor connected!")
        break

    time.sleep(config.RETRY_DELAY)

if not sensor_ready:
    print("WARNING: No sensor response. Check wiring.")

print(f"Poll interval: {config.BATTERY_POLL_MINUTES} min")
print(f"Sleep mode: {config.SLEEP_MODE}")
if config.DEBUG:
    print("DEBUG MODE ON")
print("---")

# ======================
# Main loop
# ======================
while True:
    blink(1)  # Show we're awake

    # Brief delay after wake for sensor to stabilize
    time.sleep_ms(500)

    data, raw, unit, rate_unit = poll_sensor()

    if data:
        if config.DEBUG:
            print(f"RAW: {raw}")

        print(f"Acc: {data.get('Acc', 0):.3f} {unit} | "
              f"Event: {data.get('EventAcc', 0):.3f} {unit} | "
              f"Total: {data.get('TotalAcc', 0):.3f} {unit} | "
              f"Rate: {data.get('RInt', 0):.3f} {rate_unit}")

        # Wake more often if rain detected
        rain_intensity = data.get('RInt', 0)
        if rain_intensity > 0:
            print("Rain detected!")
            blink(3)
            go_to_sleep(config.RAIN_POLL_MINUTES)
        else:
            go_to_sleep(config.BATTERY_POLL_MINUTES)
    else:
        print("No sensor response")
        go_to_sleep(config.BATTERY_POLL_MINUTES)
