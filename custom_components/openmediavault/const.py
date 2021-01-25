"""Constants used by the OpenMediaVault integration."""

DOMAIN = "openmediavault"
DEFAULT_NAME = "OpenMediaVault"
DATA_CLIENT = "client"
ATTRIBUTION = "Data provided by OpenMediaVault integration"

DEFAULT_HOST = "10.0.0.1"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "openmediavault"

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

SENSOR_TYPES = {
    "system_cpuUsage": {
        ATTR_ICON: "mdi:speedometer",
        ATTR_LABEL: "CPU load",
        ATTR_UNIT: "%",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "cpuUsage",
    },
    "system_memUsage": {
        ATTR_ICON: "mdi:memory",
        ATTR_LABEL: "Memory",
        ATTR_UNIT: "%",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "memUsage",
    },
    "system_uptimeEpoch": {
        ATTR_ICON: "mdi:clock-outline",
        ATTR_LABEL: "Uptime",
        ATTR_UNIT: "hours",
        ATTR_GROUP: "System",
        ATTR_PATH: "hwinfo",
        ATTR_ATTR: "uptimeEpoch",
    },
}

DEVICE_ATTRIBUTES_FS = [
    "size",
    "available",
    "type",
    "mountpoint",
    "_readonly",
    "_used",
]

DEVICE_ATTRIBUTES_DISK = [
    "canonicaldevicefile",
    "size",
    "israid",
    "isroot",
    "devicemodel",
    "serialnumber",
    "firmwareversion",
    "sectorsize",
    "rotationrate",
    "writecacheis",
    "smartsupportis",
    "Raw_Read_Error_Rate",
    "Spin_Up_Time",
    "Start_Stop_Count",
    "Reallocated_Sector_Ct",
    "Seek_Error_Rate",
    "Load_Cycle_Count",
    "UDMA_CRC_Error_Count",
    "Multi_Zone_Error_Rate",
]
