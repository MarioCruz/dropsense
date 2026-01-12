"""
RG-15 Rain Sensor Utility
Interactive tool for testing, configuring, and controlling the sensor.
"""

from machine import UART, Pin
import time
import config

# UART setup
uart = UART(config.UART_ID, baudrate=config.UART_BAUD, bits=8, parity=None, stop=1,
            tx=Pin(config.TX_PIN), rx=Pin(config.RX_PIN))

def read_response(timeout_ms=1000, multi_line=True):
    """Read response from sensor, optionally multiple lines."""
    responses = []
    start = time.ticks_ms()
    buf = b""

    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        if uart.any():
            b = uart.read(1)
            if b:
                if b in (b'\n', b'\r'):
                    if buf:
                        line = buf.decode('utf-8', 'ignore').strip()
                        if line:
                            responses.append(line)
                            if not multi_line:
                                return responses
                        buf = b""
                else:
                    buf += b
        else:
            time.sleep_ms(10)

    # Get any remaining data
    if buf:
        line = buf.decode('utf-8', 'ignore').strip()
        if line:
            responses.append(line)

    return responses

def send_command(cmd, description=""):
    """Send command and display response."""
    # Flush buffer
    while uart.any():
        uart.read()

    print(f"\n>> Sending: {cmd}" + (f" ({description})" if description else ""))
    uart.write(f"{cmd}\n".encode())
    time.sleep_ms(200)

    responses = read_response(1500)
    if responses:
        for line in responses:
            print(f"   {line}")
    else:
        print("   (no response)")
    return responses

MENU_ITEMS = [
    ("DATA", [
        ('1', 'R', 'Read current data'),
        ('2', 'A', 'Read accumulator only'),
        ('3', 'K', 'Reset accumulator (set to 0)'),
    ]),
    ("MODE", [
        ('4', 'P', 'Polling mode (responds to R command)'),
        ('5', 'C', 'Continuous mode (auto-send on change)'),
    ]),
    ("UNITS", [
        ('6', 'M', 'Metric (mm)'),
        ('7', 'I', 'Imperial (inches)'),
    ]),
    ("RESOLUTION", [
        ('8', 'H', 'High resolution (0.01mm)'),
        ('9', 'L', 'Low resolution (0.2mm)'),
    ]),
    ("SYSTEM", [
        ('0', 'O', 'Show current settings'),
        ('b', 'B', 'Reboot sensor'),
    ]),
    ("UTILITY", [
        ('t', None, 'Test mode (poll every 2 sec)'),
        ('q', None, 'Quit'),
    ]),
]

def show_menu():
    """Display interactive menu."""
    print("\n" + "=" * 50)
    print("        RG-15 RAIN SENSOR UTILITY")
    print("=" * 50)

    for section, items in MENU_ITEMS:
        print(f"\n  {section}")
        print("  " + "-" * 30)
        for key, cmd, desc in items:
            cmd_str = f"[{cmd}]" if cmd else "   "
            print(f"    {key}  {cmd_str:5} {desc}")

    print("\n" + "=" * 50)

def run_test_mode():
    """Continuous polling test mode."""
    print("\n[TEST MODE] Polling every 2 seconds. Press Ctrl+C to stop.\n")
    try:
        while True:
            send_command("R", "read data")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[TEST MODE] Stopped.")

def main():
    """Main interactive loop."""
    print("\nInitializing RG-15 Utility...")
    time.sleep(1)

    # Flush startup messages
    while uart.any():
        uart.read()

    # Show initial reading
    print("\nGetting initial sensor reading...")
    send_command("R", "read data")

    show_menu()

    # Build command lookup from menu items
    commands = {}
    for section, items in MENU_ITEMS:
        for key, sensor_cmd, desc in items:
            if sensor_cmd:
                commands[key] = (sensor_cmd, desc)

    while True:
        try:
            print("\n[Press number/letter or 's' for menu]")
            cmd = input(">> ").strip().lower()

            if not cmd:
                continue
            elif cmd == 'q':
                print("Exiting utility.")
                break
            elif cmd == 's':
                show_menu()
            elif cmd == 't':
                run_test_mode()
            elif cmd in commands:
                sensor_cmd, desc = commands[cmd]
                send_command(sensor_cmd, desc)
            else:
                # Send raw command
                print(f"Sending raw command: {cmd.upper()}")
                send_command(cmd.upper())
        except KeyboardInterrupt:
            print("\nExiting utility.")
            break
        except EOFError:
            print("\nExiting utility.")
            break

if __name__ == "__main__":
    main()
