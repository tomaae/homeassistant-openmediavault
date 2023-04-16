"""OpenMediaVault sensor platform."""
from logging import getLogger
from typing import Any, Optional
from collections.abc import Mapping
from homeassistant.components.sensor import SensorEntity
from .helper import format_attribute
from .model import model_async_setup_entry, OMVEntity
from .sensor_types import (
    SENSOR_TYPES,
    SENSOR_SERVICES,
    DEVICE_ATTRIBUTES_DISK_SMART,
)

_LOGGER = getLogger(__name__)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component."""
    dispatcher = {
        "OMVSensor": OMVSensor,
        "OMVDiskSensor": OMVDiskSensor,
    }
    await model_async_setup_entry(
        hass,
        config_entry,
        async_add_entities,
        SENSOR_SERVICES,
        SENSOR_TYPES,
        dispatcher,
    )


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVSensor(OMVEntity, SensorEntity):
    """Define an OpenMediaVault sensor."""

    @property
    def state(self) -> Optional[str]:
        """Return the state"""
        if self.entity_description.data_attribute:
            return self._data[self.entity_description.data_attribute]
        else:
            return "unknown"

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        if self.entity_description.native_unit_of_measurement:
            if self.entity_description.native_unit_of_measurement.startswith("data__"):
                uom = self.entity_description.native_unit_of_measurement[6:]
                if uom in self._data:
                    return self._data[uom]

            return self.entity_description.native_unit_of_measurement

        return None


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVDiskSensor(OMVSensor):
    """Define an OpenMediaVault sensor."""

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        attributes = super().extra_state_attributes
        print(self._data)

        if not self._ctrl.option_smart_disable:
            for variable in DEVICE_ATTRIBUTES_DISK_SMART:
                if variable in self._data:
                    attributes[format_attribute(variable)] = self._data[variable]

        return attributes
