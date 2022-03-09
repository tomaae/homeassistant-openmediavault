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

ATTR_ICON = "icon"
ATTR_LABEL = "label"
ATTR_UNIT = "unit"
ATTR_UNIT_ATTR = "unit_attr"
ATTR_GROUP = "group"
ATTR_PATH = "data_path"
ATTR_ATTR = "data_attr"

BINARY_SENSOR_TYPES = {
    "system_pkgUpdatesAvailable": {
        ATTR_LABEL: "Update available",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "pkgUpdatesAvailable",
    },
    "system_rebootRequired": {
        ATTR_LABEL: "Reboot pending",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "rebootRequired",
    },
    "system_configDirty": {
        ATTR_LABEL: "Config dirty",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "configDirty",
    },
}
