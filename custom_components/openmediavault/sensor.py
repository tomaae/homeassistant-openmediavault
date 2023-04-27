"""OpenMediaVault sensor platform."""
from logging import getLogger
from typing import Any
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.typing import StateType
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
        "OMVUptimeSensor": OMVUptimeSensor,
        "OMVKVMSensor": OMVKVMSensor,
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

    def __init__(
        self,
        inst,
        uid: "",
        omv_controller,
        entity_description,
    ):
        super().__init__(inst, uid, omv_controller, entity_description)
        self._attr_suggested_unit_of_measurement = (
            self.entity_description.suggested_unit_of_measurement
        )

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        return self._data[self.entity_description.data_attribute]

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

        if not self._ctrl.option_smart_disable:
            for variable in DEVICE_ATTRIBUTES_DISK_SMART:
                if variable in self._data:
                    attributes[format_attribute(variable)] = self._data[variable]

        return attributes


# ---------------------------
#   OMVUptimeSensor
# ---------------------------
class OMVUptimeSensor(OMVSensor):
    """Define an OpenMediaVault Uptime sensor."""

    async def restart(self) -> None:
        """Restart OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "System",
            "reboot",
            {"delay": 0},
        )

    async def stop(self) -> None:
        """Shutdown OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "System",
            "shutdown",
            {"delay": 0},
        )


# ---------------------------
#   OMVKVMSensor
# ---------------------------
class OMVKVMSensor(OMVSensor):
    """Define an OpenMediaVault VM sensor."""

    async def start(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "shutoff":
            _LOGGER.warning("VM %s is not powered off", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "poweron",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def stop(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "running":
            _LOGGER.warning("VM %s is not running", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "poweroff",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def restart(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "running":
            _LOGGER.warning("VM %s is not running", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "reboot",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def snapshot(self) -> None:
        """Shutdown OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "addSnapshot",
            {
                "virttype": f"{self._data['type']}",
                "vmname": f"{self._data['vmname']}",
            },
        )
