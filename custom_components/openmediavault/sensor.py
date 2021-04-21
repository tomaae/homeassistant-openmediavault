"""OpenMediaVault sensor platform."""

import logging
from re import search as re_search

from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, TEMP_CELSIUS, PERCENTAGE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.sensor import SensorEntity

from .const import (
    ATTRIBUTION,
    DATA_CLIENT,
    DOMAIN,
    ATTR_ICON,
    ATTR_LABEL,
    ATTR_UNIT,
    ATTR_UNIT_ATTR,
    ATTR_GROUP,
    ATTR_PATH,
    ATTR_ATTR,
    SENSOR_TYPES,
    DEVICE_ATTRIBUTES_FS,
    DEVICE_ATTRIBUTES_DISK,
)

_LOGGER = logging.getLogger(__name__)


# ---------------------------
#   format_attribute
# ---------------------------
def format_attribute(attr):
    """Format state attributes"""
    res = attr.replace("-", " ")
    res = res.capitalize()
    res = res.replace(" ip ", " IP ")
    res = res.replace(" mac ", " MAC ")
    res = res.replace(" mtu", " MTU")
    return res


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component."""
    inst = config_entry.data[CONF_NAME]
    omv_controller = hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id]
    sensors = {}

    # ---------------------------
    #   update_contoller
    # ---------------------------
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
    """Update sensor state from the controller."""
    new_sensors = []

    # Add sensors
    for sensor in SENSOR_TYPES:
        item_id = f"{inst}-{sensor}"
        _LOGGER.debug("Updating sensor %s", item_id)
        if item_id in sensors:
            if sensors[item_id].enabled:
                sensors[item_id].async_schedule_update_ha_state()
            continue

        sensors[item_id] = OMVSensor(
            omv_controller=omv_controller, inst=inst, sensor=sensor
        )
        new_sensors.append(sensors[item_id])

    for sid, sid_uid, sid_name, sid_ref, sid_attr, sid_func in zip(
        # Data point name
        ["fs", "disk"],
        # Data point unique id
        ["uuid", "devicename"],
        # Entry Name
        ["label", "devicename"],
        # Entry Unique id
        ["uuid", "devicename"],
        # Attr
        [DEVICE_ATTRIBUTES_FS, DEVICE_ATTRIBUTES_DISK],
        # Tracker function
        [OMVFileSystemSensor, OMVDiskSensor],
    ):
        for uid in omv_controller.data[sid]:
            # Update entity
            item_id = f"{inst}-{sid}-{omv_controller.data[sid][uid][sid_uid]}"
            _LOGGER.debug("Updating sensor %s", item_id)
            if item_id in sensors:
                if sensors[item_id].enabled:
                    sensors[item_id].async_schedule_update_ha_state()
                continue

            # Create new entity
            sid_data = {
                "sid": sid,
                "sid_uid": sid_uid,
                "sid_name": sid_name,
                "sid_ref": sid_ref,
                "sid_attr": sid_attr,
            }
            sensors[item_id] = sid_func(
                omv_controller=omv_controller, inst=inst, uid=uid, sid_data=sid_data
            )

            new_sensors.append(sensors[item_id])

    if new_sensors:
        async_add_entities(new_sensors, True)


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVSensor(SensorEntity):
    """Define an OpenMediaVault sensor."""

    def __init__(self, omv_controller, inst, sensor=None):
        """Initialize."""
        self._inst = inst
        self._sensor = sensor
        self._ctrl = omv_controller
        if sensor:
            self._data = omv_controller.data[SENSOR_TYPES[sensor][ATTR_PATH]]
            self._type = SENSOR_TYPES[sensor]
            self._attr = SENSOR_TYPES[sensor][ATTR_ATTR]
            self._icon = self._type[ATTR_ICON]

        self._state = None
        self._unit_of_measurement = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def name(self):
        """Return the name."""
        return f"{self._inst} {self._type[ATTR_LABEL]}"

    @property
    def state(self):
        """Return the state."""
        val = "unknown"
        if self._attr in self._data:
            val = self._data[self._attr]

        return val

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attrs

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._inst.lower()}-{self._sensor.lower()}"

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        if ATTR_UNIT_ATTR in self._type:
            return self._data[SENSOR_TYPES[self._sensor][ATTR_UNIT_ATTR]]

        if ATTR_UNIT in self._type:
            return self._type[ATTR_UNIT]

    @property
    def available(self) -> bool:
        """Return if controller is available."""
        return self._ctrl.connected()

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "manufacturer": "OpenMediaVault",
            "name": f"{self._inst} {self._type[ATTR_GROUP]}",
        }
        if ATTR_GROUP in self._type:
            info["identifiers"] = {
                (
                    DOMAIN,
                    self._inst,
                    "sensor",
                    self._type[ATTR_GROUP],
                )
            }

        return info

    async def async_update(self):
        """Synchronize state with controller."""

    async def async_added_to_hass(self):
        """Entity created."""
        _LOGGER.debug("New sensor %s (%s)", self._inst, self._sensor)


# ---------------------------
#   OMVFileSystemSensor
# ---------------------------
class OMVFileSystemSensor(OMVSensor):
    """Define an OpenMediaVault FS sensor."""

    def __init__(self, omv_controller, inst, uid, sid_data):
        """Initialize."""
        super().__init__(omv_controller, inst)
        self._sid_data = sid_data
        self._uid = uid
        self._data = omv_controller.data[self._sid_data["sid"]][uid]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._inst} {self._data[self._sid_data['sid_name']]}"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._inst.lower()}-{self._sid_data['sid']}-{self._data[self._sid_data['sid_ref']]}"

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "identifiers": {(DOMAIN, self._inst, "sensor", "Filesystem")},
            "manufacturer": "OpenMediaVault",
            "name": f"{self._inst} Filesystem",
        }

        return info

    async def async_added_to_hass(self):
        """Entity created."""
        _LOGGER.debug(
            "New sensor %s (%s %s)",
            self._inst,
            self._sid_data["sid"],
            self._data[self._sid_data["sid_uid"]],
        )

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:file-tree"

    @property
    def state(self):
        """Return the state."""
        return self._data["percentage"]

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return PERCENTAGE

    @property
    def device_state_attributes(self):
        """Return the port state attributes."""
        attributes = self._attrs

        for variable in self._sid_data["sid_attr"]:
            if variable in self._data:
                attributes[format_attribute(variable)] = self._data[variable]

        return attributes


# ---------------------------
#   OMVDiskSensor
# ---------------------------
class OMVDiskSensor(OMVSensor):
    """Define an OpenMediaVault Disk sensor."""

    def __init__(self, omv_controller, inst, uid, sid_data):
        """Initialize."""
        super().__init__(omv_controller, inst)
        self._sid_data = sid_data
        self._uid = uid
        self._data = omv_controller.data[self._sid_data["sid"]][uid]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._inst} {self._data[self._sid_data['sid_name']]}"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._inst.lower()}-{self._sid_data['sid']}-{self._data[self._sid_data['sid_ref']]}"

    @property
    def device_info(self):
        """Return a port description for device registry."""
        info = {
            "identifiers": {(DOMAIN, self._inst, "sensor", "Disk")},
            "manufacturer": "OpenMediaVault",
            "name": f"{self._inst} Disk",
        }

        return info

    async def async_added_to_hass(self):
        """Entity created."""
        _LOGGER.debug(
            "New sensor %s (%s %s)",
            self._inst,
            self._sid_data["sid"],
            self._data[self._sid_data["sid_uid"]],
        )

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:harddisk"

    @property
    def state(self):
        """Return the state."""
        if self._data["Temperature_Celsius"] == "unknown":
            return self._data["Temperature_Celsius"]

        return re_search("[0-9]+", self._data["Temperature_Celsius"]).group()

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return TEMP_CELSIUS

    @property
    def device_state_attributes(self):
        """Return the port state attributes."""
        attributes = self._attrs

        for variable in self._sid_data["sid_attr"]:
            if variable in self._data:
                attributes[format_attribute(variable)] = self._data[variable]

        return attributes
