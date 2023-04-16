"""Constants used by the OpenMediaVault integration."""
from homeassistant.const import Platform

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

DOMAIN = "openmediavault"
DEFAULT_NAME = "OpenMediaVault"
ATTRIBUTION = "Data provided by OpenMediaVault integration"

DEFAULT_HOST = "10.0.0.1"
DEFAULT_USERNAME = "admin"

DEFAULT_DEVICE_NAME = "OMV"
DEFAULT_SSL = False
DEFAULT_SSL_VERIFY = True

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 60
CONF_SMART_DISABLE = "smart_disable"
DEFAULT_SMART_DISABLE = False

TO_REDACT = {
    "username",
    "password",
}
