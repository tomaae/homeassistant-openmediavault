"""OpenMediaVault binary sensor platform."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    ATTRIBUTION,
    DATA_CLIENT,
    DOMAIN,
    ATTR_LABEL,
    ATTR_GROUP,
    ATTR_PATH,
    ATTR_ATTR,
    BINARY_SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)

# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component."""
    inst = config_entry.data[CONF_NAME]
    omv_controller = hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id]
    sensors = {}

    @callback
    def update_controller():
        """Update the values of the controller."""
        update_items(inst, omv_controller, async_add_entities, sensors)

    omv_controller.listeners.append(
        async_dispatcher_connect(hass, omv_controller.signal_update, update_controller)
    )
    update_controller()


# ---------------------------
#   update_items
# ---------------------------
@callback
def update_items(inst, omv_controller, async_add_entities, sensors):
    """Update sensor state from controller."""
    new_sensors = []

    for sensor in BINARY_SENSOR_TYPES:
        item_id = f"{inst}-{sensor}"
        _LOGGER.debug("Updating binary_sensor %s", item_id)
        if item_id in sensors:
            if sensors[item_id].enabled:
                sensors[item_id].async_schedule_update_ha_state()
            continue

        sensors[item_id] = OMVBinarySensor(
            omv_controller=omv_controller, inst=inst, sensor=sensor
        )
        new_sensors.append(sensors[item_id])

    if new_sensors:
        async_add_entities(new_sensors, True)


# ---------------------------
#   OMVBinarySensor
# ---------------------------
class OMVBinarySensor(BinarySensorEntity):
    """Define an OMV Binary Sensor."""

    def __init__(self, omv_controller, inst, sensor):
        """Initialize."""
        self._inst = inst
        self._sensor = sensor
        self._ctrl = omv_controller
        self._data = omv_controller.data[BINARY_SENSOR_TYPES[sensor][ATTR_PATH]]
        self._type = BINARY_SENSOR_TYPES[sensor]
        self._attr = BINARY_SENSOR_TYPES[sensor][ATTR_ATTR]

        self._state = None
        self._icon = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._inst} {self._type[ATTR_LABEL]}"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attrs

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._inst.lower()}-{self._sensor.lower()}"

    @property
    def available(self) -> bool:
        """Return if controller is available."""
        return self._ctrl.connected()

    @property
    def device_info(self):
        """Return a description for device registry."""
        info = {
            "manufacturer": "OpenMediaVault",
            "name": f"{self._inst} {self._type[ATTR_GROUP]}",
        }
        if ATTR_GROUP in self._type:
            info["identifiers"] = {
                (DOMAIN, self._inst, "sensor", self._type[ATTR_GROUP])
            }

        return info

    async def async_update(self):
        """Synchronize state with controller."""

    async def async_added_to_hass(self):
        """Entity created."""
        _LOGGER.debug("New sensor %s (%s)", self._inst, self._sensor)

    @property
    def is_on(self):
        """Return true if binary sensor is on."""
        val = False
        if self._attr in self._data:
            val = self._data[self._attr]

        return val
