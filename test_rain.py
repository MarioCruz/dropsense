# test_rain.py - Rain Sensor Test Script
# Tests Hydreon RG-15 connection and reads data

from machine import UART, Pin
import time

print("=" * 50)
print("Rain Sensor Test - Hydreon RG-15")
print("=" * 50)

# Configuration
UART_ID = 0
UART_BAUD = 9600
TX_PIN = 0  # Pico TX -> RG-15 RX
RX_PIN = 1  # Pico RX -> RG-15 TX

print(f"UART: ID={UART_ID}, Baud={UART_BAUD}")
print(f"Pins: TX=GP{TX_PIN}, RX=GP{RX_PIN}")
print("-" * 50)

# Initialize UART
try:
    uart = UART(UART_ID, baudrate=UART_BAUD, bits=8, parity=None, stop=1,
                tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    print("UART: Initialized")
except Exception as e:
    print(f"UART: FAILED - {e}")
    import sys
    sys.exit(1)

# Wait for sensor power-up
print("Waiting 2 seconds for sensor boot...")
time.sleep(2)

# Flush startup messages
print("Flushing startup data...")
while uart.any():
    uart.read()
time.sleep(0.5)

# Test 1: Poll sensor
print("\nTest 1: Polling sensor with 'R' command...")
uart.write(b'R\n')
time.sleep(0.3)

response_count = 0
for i in range(5):
    if uart.any():
        line = uart.readline()
        if line:
            response_count += 1
            print(f"  Response {response_count}: {line.decode('utf-8', 'ignore').strip()}")
    time.sleep(0.1)

if response_count == 0:
    print("  ERROR: No response from sensor")
    print("\nTroubleshooting:")
    print("  1. Check power (5V to RG-15)")
    print("  2. Check TX/RX wiring (crossed correctly)")
    print("  3. Verify RG-15 is powered on (LED should be visible)")
else:
    print(f"  SUCCESS: Received {response_count} response(s)")

# Test 2: Set to imperial units
print("\nTest 2: Setting imperial units (inches)...")
uart.write(b'I\n')
time.sleep(0.2)

# Test 3: Get settings
print("\nTest 3: Reading sensor settings...")
uart.write(b'O\n')
time.sleep(0.3)

for i in range(3):
    if uart.any():
        line = uart.readline()
        if line:
            print(f"  {line.decode('utf-8', 'ignore').strip()}")
    time.sleep(0.1)

# Test 4: Continuous reading
print("\nTest 4: Continuous reading (10 polls)...")
for poll in range(10):
    uart.write(b'R\n')
    time.sleep(0.3)
    
    if uart.any():
        line = uart.readline()
        if line:
            decoded = line.decode('utf-8', 'ignore').strip()
            print(f"  Poll {poll + 1}: {decoded}")
    else:
        print(f"  Poll {poll + 1}: No data")
    
    time.sleep(1)

print("\n" + "=" * 50)
print("Test Complete")
print("=" * 50)
