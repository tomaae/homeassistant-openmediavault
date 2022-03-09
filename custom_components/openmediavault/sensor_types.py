"""Definitions for OMV sensor entities."""
from dataclasses import dataclass, field
from typing import List
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.const import (
    PERCENTAGE,
)

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


@dataclass
class OMVSensorEntityDescription(SensorEntityDescription):
    """Class describing mikrotik entities."""

    ha_group: str = ""
    ha_connection: str = ""
    ha_connection_value: str = ""
    data_path: str = ""
    data_attribute: str = ""
    data_name: str = ""
    data_uid: str = ""
    data_reference: str = ""
    data_attributes_list: List = field(default_factory=lambda: [])


SENSOR_TYPES = {
    "system_cpuUsage": OMVSensorEntityDescription(
        key="system_cpuUsage",
        name="CPU load",
        icon="mdi:speedometer",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=None,
        entity_category=None,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="cpuUsage",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "system_memUsage": OMVSensorEntityDescription(
        key="system_memUsage",
        name="Memory",
        icon="mdi:memory",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=None,
        entity_category=None,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="memUsage",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "system_uptimeEpoch": OMVSensorEntityDescription(
        key="system_uptimeEpoch",
        name="Memory",
        icon=None,
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="uptimeEpoch",
        data_name="",
        data_uid="",
        data_reference="",
    ),
}
