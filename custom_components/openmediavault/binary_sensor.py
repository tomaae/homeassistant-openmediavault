"""OpenMediaVault binary sensor platform."""
from logging import getLogger
from homeassistant.components.binary_sensor import BinarySensorEntity
from .model import model_async_setup_entry, OMVEntity
from .binary_sensor_types import SENSOR_TYPES, SENSOR_SERVICES

_LOGGER = getLogger(__name__)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component"""
    dispatcher = {
        "OMVBinarySensor": OMVBinarySensor,
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
#   OMVBinarySensor
# ---------------------------
class OMVBinarySensor(OMVEntity, BinarySensorEntity):
    """Define an OpenMediaVault binary sensor."""

    @property
    def is_on(self) -> bool:
        """Return true if device is on"""
        return self._data[self.entity_description.data_is_on]

    @property
    def icon(self) -> str:
        """Return the icon"""
        if self.entity_description.icon_enabled:
            if self._data[self.entity_description.data_is_on]:
                return self.entity_description.icon_enabled
            else:
                return self.entity_description.icon_disabled
