"""OpenMediaVault sensor platform."""
from logging import getLogger
from typing import Optional
from homeassistant.components.sensor import SensorEntity
from .model import model_async_setup_entry, OMVEntity
from .sensor_types import SENSOR_TYPES, SENSOR_SERVICES

_LOGGER = getLogger(__name__)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component."""
    dispatcher = {
        "OMVSensor": OMVSensor,
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
