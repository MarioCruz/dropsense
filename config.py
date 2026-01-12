# RG-15 Rain Sensor Configuration

# Debug mode - shows raw sensor output and diagnostic messages
DEBUG = False

# Polling interval in seconds
POLL_INTERVAL = 15

# Startup sequence - wait for sensor to be ready
BOOT_DELAY = 2        # Initial delay for sensor power-up (seconds)
MAX_RETRIES = 5       # Max attempts to get sensor response
RETRY_DELAY = 1       # Delay between retries (seconds)

# UART settings
UART_ID = 0
UART_BAUD = 9600
TX_PIN = 0
RX_PIN = 1

# Battery saver settings
BATTERY_POLL_MINUTES = 5   # How often to check for rain in battery mode
RAIN_POLL_MINUTES = 1      # Poll more often when rain detected
SLEEP_MODE = "light"       # "light" = faster wake (~1.3mA), "deep" = max savings (~0.8mA)
LED_ENABLED = False        # Blink LED to show activity (causes CYW43 errors on Pico W)
