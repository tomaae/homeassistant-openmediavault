"""OpenMediaVault sensor platform."""

import logging
from typing import Any, Optional
from collections.abc import Mapping
from re import search as re_search

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_NAME,
    CONF_HOST,
    TEMP_CELSIUS,
    PERCENTAGE,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    ATTRIBUTION,
)

from .sensor_types import (
    OMVSensorEntityDescription,
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
    omv_controller = hass.data[DOMAIN][config_entry.entry_id]
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
    """Update sensor state from the controller."""
    new_sensors = []

    # # Add sensors
    # for sensor in SENSOR_TYPES:
    #     item_id = f"{inst}-{sensor}"
    #     _LOGGER.debug("Updating sensor %s", item_id)
    #     if item_id in sensors:
    #         if sensors[item_id].enabled:
    #             sensors[item_id].async_schedule_update_ha_state()
    #         continue
    #
    #     sensors[item_id] = OMVSensor(
    #         omv_controller=omv_controller, inst=inst, sensor=sensor
    #     )
    #     new_sensors.append(sensors[item_id])

    # for sid, sid_uid, sid_name, sid_ref, sid_attr, sid_func in zip(
    #     # Data point name
    #     ["fs", "disk"],
    #     # Data point unique id
    #     ["uuid", "devicename"],
    #     # Entry Name
    #     ["label", "devicename"],
    #     # Entry Unique id
    #     ["uuid", "devicename"],
    #     # Attr
    #     [DEVICE_ATTRIBUTES_FS, DEVICE_ATTRIBUTES_DISK],
    #     # Tracker function
    #     [OMVFileSystemSensor, OMVDiskSensor],
    # ):
    #     for uid in omv_controller.data[sid]:
    #         # Update entity
    #         item_id = f"{inst}-{sid}-{omv_controller.data[sid][uid][sid_uid]}"
    #         _LOGGER.debug("Updating sensor %s", item_id)
    #         if item_id in sensors:
    #             if sensors[item_id].enabled:
    #                 sensors[item_id].async_schedule_update_ha_state()
    #             continue
    #
    #         # Create new entity
    #         sid_data = {
    #             "sid": sid,
    #             "sid_uid": sid_uid,
    #             "sid_name": sid_name,
    #             "sid_ref": sid_ref,
    #             "sid_attr": sid_attr,
    #         }
    #         sensors[item_id] = sid_func(
    #             omv_controller=omv_controller, inst=inst, uid=uid, sid_data=sid_data
    #         )
    #
    #         new_sensors.append(sensors[item_id])

    for sensor in SENSOR_TYPES:
        if sensor.startswith("system_"):
            uid_sensor = SENSOR_TYPES[sensor]
            if (
                uid_sensor.data_attribute
                not in omv_controller.data[uid_sensor.data_path]
                or omv_controller.data[uid_sensor.data_path][uid_sensor.data_attribute]
                == "unknown"
            ):
                continue
            item_id = f"{inst}-{sensor}"
            _LOGGER.debug("Updating sensor %s", item_id)
            if item_id in sensors:
                if sensors[item_id].enabled:
                    sensors[item_id].async_schedule_update_ha_state()
                continue

            sensors[item_id] = OMVSensor(
                inst=inst,
                uid="",
                omv_controller=omv_controller,
                entity_description=uid_sensor,
            )
            new_sensors.append(sensors[item_id])

    if new_sensors:
        async_add_entities(new_sensors, True)


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVSensor(SensorEntity):
    """Define an OpenMediaVault sensor."""

    def __init__(
        self,
        inst,
        uid: "",
        omv_controller,
        entity_description: OMVSensorEntityDescription,
    ):
        """Initialize."""
        self.entity_description = entity_description
        self._inst = inst
        self._ctrl = omv_controller
        self._attr_extra_state_attributes = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._uid = uid
        if self._uid:
            self._data = omv_controller.data[self.entity_description.data_path][
                self._uid
            ]
        else:
            self._data = omv_controller.data[self.entity_description.data_path]

    @property
    def name(self) -> str:
        """Return the name."""
        if self._uid:
            if self.entity_description.name:
                return f"{self._inst} {self._data[self.entity_description.data_name]} {self.entity_description.name}"

            return f"{self._inst} {self._data[self.entity_description.data_name]}"
        else:
            return f"{self._inst} {self.entity_description.name}"

    @property
    def unique_id(self) -> str:
        """Return a unique id for this entity."""
        if self._uid:
            return f"{self._inst.lower()}-{self.entity_description.key}-{self._data[self.entity_description.data_reference].lower()}"
        else:
            return f"{self._inst.lower()}-{self.entity_description.key}"

    @property
    def state(self) -> Optional[str]:
        """Return the state."""
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
                    uom = self._data[uom]
                    return uom

            return self.entity_description.native_unit_of_measurement

        return None

    @property
    def available(self) -> bool:
        """Return if controller is available."""
        return self._ctrl.connected()

    @property
    def device_info(self) -> DeviceInfo:
        """Return a description for device registry."""
        dev_connection = DOMAIN
        dev_connection_value = self.entity_description.data_reference
        dev_group = self.entity_description.ha_group
        if self.entity_description.ha_group == "System":
            # dev_group = self._ctrl.data["resource"]["board-name"]
            dev_connection_value = self._ctrl.data["hwinfo"]["hostname"]

        if self.entity_description.ha_group.startswith("data__"):
            dev_group = self.entity_description.ha_group[6:]
            if dev_group in self._data:
                dev_group = self._data[dev_group]
                dev_connection_value = dev_group

        if self.entity_description.ha_connection:
            dev_connection = self.entity_description.ha_connection

        if self.entity_description.ha_connection_value:
            dev_connection_value = self.entity_description.ha_connection_value
            if dev_connection_value.startswith("data__"):
                dev_connection_value = dev_connection_value[6:]
                dev_connection_value = self._data[dev_connection_value]

        info = DeviceInfo(
            connections={(dev_connection, f"{dev_connection_value}")},
            identifiers={(dev_connection, f"{dev_connection_value}")},
            default_name=f"{self._inst} {dev_group}",
            # model=f"{self._ctrl.data['resource']['board-name']}",
            manufacturer="OpenMediaVault",
            sw_version=f"{self._ctrl.data['hwinfo']['version']}",
            configuration_url=f"http://{self._ctrl.config_entry.data[CONF_HOST]}",
            via_device=(DOMAIN, f"{self._ctrl.data['hwinfo']['hostname']}"),
        )

        return info

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        attributes = super().extra_state_attributes
        for variable in self.entity_description.data_attributes_list:
            if variable in self._data:
                attributes[format_attribute(variable)] = self._data[variable]

        return attributes

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        _LOGGER.debug("New sensor %s (%s)", self._inst, self.unique_id)


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
    def extra_state_attributes(self):
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
    def extra_state_attributes(self):
        """Return the port state attributes."""
        attributes = self._attrs

        for variable in self._sid_data["sid_attr"]:
            if variable in self._data:
                attributes[format_attribute(variable)] = self._data[variable]

        return attributes
