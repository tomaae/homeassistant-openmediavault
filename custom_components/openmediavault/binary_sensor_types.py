"""Definitions for OMV binary sensor entities."""
from dataclasses import dataclass, field
from typing import List
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)

from .const import DOMAIN


DEVICE_ATTRIBUTES_SERVICE = [
    "name",
    "enabled",
]


@dataclass
class OMVBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing OMV entities."""

    icon_enabled: str = ""
    icon_disabled: str = ""
    ha_group: str = ""
    ha_connection: str = ""
    ha_connection_value: str = ""
    data_path: str = ""
    data_is_on: str = "available"
    data_name: str = ""
    data_uid: str = ""
    data_reference: str = ""
    data_attributes_list: List = field(default_factory=lambda: [])
    func: str = "OMVBinarySensor"


SENSOR_TYPES = {
    "system_pkgUpdatesAvailable": OMVBinarySensorEntityDescription(
        key="system_pkgUpdatesAvailable",
        name="Update available",
        icon_enabled="",
        icon_disabled="",
        device_class=BinarySensorDeviceClass.UPDATE,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="System",
        data_path="hwinfo",
        data_is_on="pkgUpdatesAvailable",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "system_rebootRequired": OMVBinarySensorEntityDescription(
        key="system_rebootRequired",
        name="Reboot pending",
        icon_enabled="",
        icon_disabled="",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="System",
        data_path="hwinfo",
        data_is_on="rebootRequired",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "system_configDirty": OMVBinarySensorEntityDescription(
        key="system_configDirty",
        name="Config dirty",
        icon_enabled="",
        icon_disabled="",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="System",
        data_path="hwinfo",
        data_is_on="configDirty",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "service": OMVBinarySensorEntityDescription(
        key="service",
        name="service",
        icon_enabled="mdi:cog",
        icon_disabled="mdi:cog-off",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="Services",
        ha_connection=DOMAIN,
        ha_connection_value="Services",
        data_path="service",
        data_is_on="running",
        data_name="title",
        data_uid="name",
        data_reference="name",
        data_attributes_list=DEVICE_ATTRIBUTES_SERVICE,
    ),
}

SENSOR_SERVICES = []
