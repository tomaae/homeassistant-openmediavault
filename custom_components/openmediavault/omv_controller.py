"""OpenMediaVault Controller"""

import asyncio
import logging
from datetime import timedelta

from .omv_api import OpenMediaVaultAPI
from .helper import parse_api

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


# ---------------------------
#   OpenMediaVaultControllerData
# ---------------------------
class OpenMediaVaultControllerData(object):
    """OpenMediaVaultController Class"""

    def __init__(self, hass, config_entry):
        """Initialize OpenMediaVaultController."""
        self.hass = hass
        self.config_entry = config_entry
        self.name = config_entry.data[CONF_NAME]
        self.host = config_entry.data[CONF_HOST]

        self.data = {
            "hwinfo": {},
            "fs": {},
        }

        self.listeners = []
        self.lock = asyncio.Lock()

        self.api = OpenMediaVaultAPI(
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
        )

        self._force_update_callback = None

    async def async_init(self):
        self._force_update_callback = async_track_time_interval(
            self.hass, self.force_update, timedelta(seconds=60)
        )

    # ---------------------------
    #   signal_update
    # ---------------------------
    @property
    def signal_update(self):
        """Event to signal new data."""
        return f"{DOMAIN}-update-{self.name}"

    # ---------------------------
    #   async_reset
    # ---------------------------
    async def async_reset(self):
        """Reset dispatchers"""
        for unsub_dispatcher in self.listeners:
            unsub_dispatcher()

        self.listeners = []
        return True

    # ---------------------------
    #   connected
    # ---------------------------
    def connected(self):
        """Return connected state"""
        return self.api.connected()

    # ---------------------------
    #   force_update
    # ---------------------------
    @callback
    async def force_update(self, _now=None):
        """Trigger update by timer"""
        await self.async_update()

    # ---------------------------
    #   async_update
    # ---------------------------
    async def async_update(self):
        """Update OMV data"""
        try:
            await asyncio.wait_for(self.lock.acquire(), timeout=10)
        except:
            return

        await self.hass.async_add_executor_job(self.get_hwinfo)
        await self.hass.async_add_executor_job(self.get_fs)

        async_dispatcher_send(self.hass, self.signal_update)
        self.lock.release()

    # ---------------------------
    #   get_hwinfo
    # ---------------------------
    def get_hwinfo(self):
        """Get hardware info from OMV"""
        self.data["hwinfo"] = parse_api(
            data=self.data["hwinfo"],
            source=self.api.query("System", "getInformation"),
            vals=[
                {"name": "hostname", "default": "unknown"},
                {"name": "version", "default": "unknown"},
                {"name": "cpuUsage", "default": 0},
                {"name": "memTotal", "default": 0},
                {"name": "memUsed", "default": 0},
                {"name": "configDirty", "type": "bool", "default": False},
                {"name": "rebootRequired", "type": "bool", "default": False},
                {"name": "pkgUpdatesAvailable", "type": "bool", "default": False},
            ],
            ensure_vals=[{"name": "memUsage", "default": 0},],
        )

        self.data["hwinfo"]["cpuUsage"] = round(self.data["hwinfo"]["cpuUsage"], 1)
        if self.data["hwinfo"]["memTotal"] > 0:
            mem = (
                int(self.data["hwinfo"]["memUsed"])
                / int(self.data["hwinfo"]["memTotal"])
            ) * 100
        else:
            mem = 0
        self.data["hwinfo"]["memUsage"] = round(mem, 1)

    # ---------------------------
    #   get_fs
    # ---------------------------
    def get_fs(self):
        """Get all filesystems from OMV"""
        self.data["fs"] = parse_api(
            data=self.data["fs"],
            source=self.api.query(
                "FileSystemMgmt", "enumerateMountedFilesystems", {"includeroot": True}
            ),
            key="uuid",
            vals=[
                {"name": "uuid"},
                {"name": "parentdevicefile", "default": "unknown"},
                {"name": "label", "default": "unknown"},
                {"name": "type", "default": "unknown"},
                {"name": "mountpoint", "default": "unknown"},
                {"name": "available", "default": "unknown"},
                {"name": "size", "default": "unknown"},
                {"name": "percentage", "default": "unknown"},
            ],
        )

        for uid in self.data["fs"]:
            self.data["fs"][uid]["size"] = round(
                int(self.data["fs"][uid]["size"]) / 1073741824, 1
            )
            self.data["fs"][uid]["available"] = round(
                int(self.data["fs"][uid]["available"]) / 1073741824, 1
            )
