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


SERVICE_SYSTEM_REBOOT = "system_reboot"
SCHEMA_SERVICE_SYSTEM_REBOOT = {}

SERVICE_SYSTEM_SHUTDOWN = "system_shutdown"
SCHEMA_SERVICE_SYSTEM_SHUTDOWN = {}

SERVICE_KVM_START = "kvm_start"
SCHEMA_SERVICE_KVM_START = {}
SERVICE_KVM_STOP = "kvm_stop"
SCHEMA_SERVICE_KVM_STOP = {}
SERVICE_KVM_RESTART = "kvm_restart"
SCHEMA_SERVICE_KVM_RESTART = {}
SERVICE_KVM_SNAPSHOT = "kvm_snapshot"
SCHEMA_SERVICE_KVM_SNAPSHOT = {}
