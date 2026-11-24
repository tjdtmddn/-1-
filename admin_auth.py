import os


ADMIN_PIN_ENV = "DAILY_MISSION_ADMIN_PIN"
DEFAULT_ADMIN_PIN = "1234"
MAX_PIN_ATTEMPTS = 5


def get_admin_pin() -> str:
    pin = os.environ.get(ADMIN_PIN_ENV, DEFAULT_ADMIN_PIN).strip()
    if not pin.isdigit() or not 4 <= len(pin) <= 8:
        return DEFAULT_ADMIN_PIN
    return pin
