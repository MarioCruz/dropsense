from machine import UART, Pin
import time
import config

# UART setup from config
uart = UART(config.UART_ID, baudrate=config.UART_BAUD, bits=8, parity=None, stop=1,
            tx=Pin(config.TX_PIN), rx=Pin(config.RX_PIN))

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
                    if buf:  # Only return if we have data
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
    # Note: Don't filter 'Event' - it's part of 'EventAcc' in data lines
    skip_patterns = ('overlow', 'overflow', '----', 'SW ')
    return any(p in line for p in skip_patterns)

print("RG-15 Rain Sensor Monitor")
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
        if config.DEBUG:
            print(f"  Response: {line}")
        break

    time.sleep(config.RETRY_DELAY)

if not sensor_ready:
    print("WARNING: No response from sensor. Check wiring.")
    print("Continuing anyway...")

print(f"Polling every {config.POLL_INTERVAL} seconds...")
if config.DEBUG:
    print("DEBUG MODE ON")
print("---")

while True:
    # Poll the sensor with 'R' command
    uart.write(b'R\n')
    time.sleep_ms(100)

    # Read multiple lines (sensor may send status + data)
    for _ in range(3):
        line = read_line(500)
        if not line:
            continue

        # Debug: show all raw output
        if config.DEBUG:
            print(f"RAW: {line}")

        # Skip diagnostic messages (unless debug)
        if is_diagnostic_message(line):
            if config.DEBUG:
                print(f"  -> (diagnostic, skipped)")
            continue

        # Check for status alerts
        if 'EmSat' in line:
            print("ALERT: Emitter Saturated (heavy rain or lens blocked)")
            continue
        elif 'Lens' in line:
            print("ALERT: Lens issue detected")
            continue

        # Parse and display data
        data = parse_rg15(line)
        if data:
            # Detect units from raw line
            unit = 'in' if ' in' in line or 'iph' in line else 'mm'
            rate_unit = 'in/hr' if 'iph' in line else 'mm/hr'

            print(f"Acc: {data.get('Acc', 0):.3f} {unit} | "
                  f"Event: {data.get('EventAcc', 0):.3f} {unit} | "
                  f"Total: {data.get('TotalAcc', 0):.3f} {unit} | "
                  f"Rate: {data.get('RInt', 0):.3f} {rate_unit}")

    time.sleep(config.POLL_INTERVAL)
