"""OpenMediaVault Controller."""

import asyncio
import pytz
from datetime import datetime, timedelta

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    CONF_SMART_DISABLE,
    DEFAULT_SMART_DISABLE,
)
from .apiparser import parse_api
from .omv_api import OpenMediaVaultAPI

DEFAULT_TIME_ZONE = None


def utc_from_timestamp(timestamp: float) -> datetime:
    """Return a UTC time from a timestamp."""
    return pytz.utc.localize(datetime.utcfromtimestamp(timestamp))


# ---------------------------
#   OMVControllerData
# ---------------------------
class OMVControllerData(object):
    """OMVControllerData Class."""

    def __init__(self, hass, config_entry):
        """Initialize OMVController."""
        self.hass = hass
        self.config_entry = config_entry
        self.name = config_entry.data[CONF_NAME]
        self.host = config_entry.data[CONF_HOST]

        self.data = {
            "hwinfo": {},
            "plugin": {},
            "disk": {},
            "fs": {},
            "service": {},
            "network": {},
            "kvm": {},
            "compose": {},
        }

        self.listeners = []
        self.lock = asyncio.Lock()

        self.api = OpenMediaVaultAPI(
            hass,
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_SSL],
            config_entry.data[CONF_VERIFY_SSL],
        )

        self._force_update_callback = None
        self._force_hwinfo_update_callback = None

    # ---------------------------
    #   async_init
    # ---------------------------
    async def async_init(self) -> None:
        self._force_update_callback = async_track_time_interval(
            self.hass, self.force_update, self.option_scan_interval
        )
        self._force_hwinfo_update_callback = async_track_time_interval(
            self.hass, self.force_hwinfo_update, timedelta(seconds=3600)
        )

    # ---------------------------
    #   option_scan_interval
    # ---------------------------
    @property
    def option_scan_interval(self):
        """Config entry option scan interval."""
        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return timedelta(seconds=scan_interval)

    # ---------------------------
    #   option_smart_disable
    # ---------------------------
    @property
    def option_smart_disable(self):
        """Config entry option smart disable."""
        return self.config_entry.options.get(CONF_SMART_DISABLE, DEFAULT_SMART_DISABLE)

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
    async def async_reset(self) -> bool:
        """Reset dispatchers."""
        for unsub_dispatcher in self.listeners:
            unsub_dispatcher()

        self.listeners = []
        return True

    # ---------------------------
    #   connected
    # ---------------------------
    def connected(self):
        """Return connected state."""
        return self.api.connected()

    # ---------------------------
    #   force_hwinfo_update
    # ---------------------------
    @callback
    async def force_hwinfo_update(self, _now=None):
        """Trigger update by timer."""
        await self.async_hwinfo_update()

    # ---------------------------
    #   async_hwinfo_update
    # ---------------------------
    async def async_hwinfo_update(self):
        """Update OpenMediaVault hardware info."""
        try:
            await asyncio.wait_for(self.lock.acquire(), timeout=30)
        except Exception:
            return

        await self.hass.async_add_executor_job(self.get_hwinfo)
        if self.api.connected():
            await self.hass.async_add_executor_job(self.get_plugin)
        if self.api.connected():
            await self.hass.async_add_executor_job(self.get_disk)

        self.lock.release()

    # ---------------------------
    #   force_update
    # ---------------------------
    @callback
    async def force_update(self, _now=None):
        """Trigger update by timer."""
        await self.async_update()

    # ---------------------------
    #   async_update
    # ---------------------------
    async def async_update(self):
        """Update OMV data."""
        if self.api.has_reconnected():
            await self.async_hwinfo_update()

        try:
            await asyncio.wait_for(self.lock.acquire(), timeout=10)
        except Exception:
            return

        await self.hass.async_add_executor_job(self.get_hwinfo)
        if self.api.connected():
            await self.hass.async_add_executor_job(self.get_fs)

        if not self.option_smart_disable and self.api.connected():
            await self.hass.async_add_executor_job(self.get_smart)

        if self.api.connected():
            await self.hass.async_add_executor_job(self.get_network)

        if self.api.connected():
            await self.hass.async_add_executor_job(self.get_service)

        if (
            self.api.connected()
            and "openmediavault-kvm" in self.data["plugin"]
            and self.data["plugin"]["openmediavault-kvm"]["installed"]
        ):
            await self.hass.async_add_executor_job(self.get_kvm)
        if (
            self.api.connected()
            and "openmediavault-compose" in self.data["plugin"]
            and self.data["plugin"]["openmediavault-compose"]["installed"]
        ):
            await self.hass.async_add_executor_job(self.get_compose)

        async_dispatcher_send(self.hass, self.signal_update)
        self.lock.release()

    # ---------------------------
    #   get_hwinfo
    # ---------------------------
    def get_hwinfo(self):
        """Get hardware info from OMV."""
        self.data["hwinfo"] = parse_api(
            data=self.data["hwinfo"],
            source=self.api.query("System", "getInformation"),
            vals=[
                {"name": "hostname", "default": "unknown"},
                {"name": "version", "default": "unknown"},
                {"name": "cpuUsage", "default": 0.0},
                {"name": "memTotal", "default": 0},
                {"name": "memUsed", "default": 0},
                {"name": "loadAverage_1", "source": "loadAverage/1min", "default": 0.0},
                {"name": "loadAverage_5", "source": "loadAverage/5min", "default": 0.0},
                {
                    "name": "loadAverage_15",
                    "source": "loadAverage/15min",
                    "default": 0.0,
                },
                {"name": "uptime", "default": "0 days 0 hours 0 minutes 0 seconds"},
                {"name": "configDirty", "type": "bool", "default": False},
                {"name": "rebootRequired", "type": "bool", "default": False},
                {"name": "availablePkgUpdates", "default": 0},
            ],
            ensure_vals=[
                {"name": "memUsage", "default": 0.0},
                {"name": "pkgUpdatesAvailable", "type": "bool", "default": False},
            ],
        )

        if not self.api.connected():
            return

        tmp_uptime = 0
        if int(self.data["hwinfo"]["version"].split(".")[0]) > 5:
            tmp = float(self.data["hwinfo"]["uptime"])
            pos = abs(int(tmp))
            day = pos / (3600 * 24)
            rem = pos % (3600 * 24)
            hour = rem / 3600
            rem = rem % 3600
            mins = rem / 60
            secs = rem % 60
            res = "%d days %02d hours %02d minutes %02d seconds" % (
                day,
                hour,
                mins,
                secs,
            )
            if int(tmp) < 0:
                res = "-%s" % res
            tmp = res.split(" ")
        else:
            tmp = self.data["hwinfo"]["uptime"].split(" ")

        tmp_uptime += int(tmp[0]) * 86400  # days
        tmp_uptime += int(tmp[2]) * 3600  # hours
        tmp_uptime += int(tmp[4]) * 60  # minutes
        tmp_uptime += int(tmp[6])  # seconds
        now = datetime.now().replace(microsecond=0)
        uptime_tm = datetime.timestamp(now - timedelta(seconds=tmp_uptime))
        self.data["hwinfo"]["uptimeEpoch"] = utc_from_timestamp(uptime_tm)

        self.data["hwinfo"]["cpuUsage"] = round(self.data["hwinfo"]["cpuUsage"], 1)
        mem = (
            (int(self.data["hwinfo"]["memUsed"]) / int(self.data["hwinfo"]["memTotal"]))
            * 100
            if int(self.data["hwinfo"]["memTotal"]) > 0
            else 0
        )
        self.data["hwinfo"]["memUsage"] = round(mem, 1)

        self.data["hwinfo"]["pkgUpdatesAvailable"] = (
            self.data["hwinfo"]["availablePkgUpdates"] > 0
        )

    # ---------------------------
    #   get_disk
    # ---------------------------
    def get_disk(self):
        """Get all filesystems from OMV."""
        self.data["disk"] = parse_api(
            data=self.data["disk"],
            source=self.api.query("DiskMgmt", "enumerateDevices"),
            key="devicename",
            vals=[
                {"name": "devicename"},
                {"name": "canonicaldevicefile"},
                {"name": "size", "default": "unknown"},
                {"name": "vendor", "default": "unknown"},
                {"name": "model", "default": "unknown"},
                {"name": "description", "default": "unknown"},
                {"name": "serialnumber", "default": "unknown"},
                {"name": "israid", "type": "bool", "default": False},
                {"name": "isroot", "type": "bool", "default": False},
                {"name": "isreadonly", "type": "bool", "default": False},
            ],
            ensure_vals=[
                {"name": "temperature", "default": 0},
                {"name": "Raw_Read_Error_Rate", "default": "unknown"},
                {"name": "Spin_Up_Time", "default": "unknown"},
                {"name": "Start_Stop_Count", "default": "unknown"},
                {"name": "Reallocated_Sector_Ct", "default": "unknown"},
                {"name": "Seek_Error_Rate", "default": "unknown"},
                {"name": "Load_Cycle_Count", "default": "unknown"},
                {"name": "UDMA_CRC_Error_Count", "default": "unknown"},
                {"name": "Multi_Zone_Error_Rate", "default": "unknown"},
            ],
        )

    # ---------------------------
    #   get_smart
    # ---------------------------
    def get_smart(self):
        """Get S.M.A.R.T. information from OMV."""
        tmp_smart_get_list = self.api.query(
            "Smart", "getList", {"start": 0, "limit": -1}
        )
        if "data" in tmp_smart_get_list:
            tmp_smart_get_list = tmp_smart_get_list["data"]

        self.data["disk"] = parse_api(
            data=self.data["disk"],
            source=tmp_smart_get_list,
            key="devicename",
            vals=[
                {"name": "temperature", "default": 0},
            ],
        )

        for uid in self.data["disk"]:
            if self.data["disk"][uid]["devicename"].startswith("mmcblk"):
                continue

            if self.data["disk"][uid]["devicename"].startswith("sr"):
                continue

            if self.data["disk"][uid]["devicename"].startswith("bcache"):
                continue

            tmp_data = parse_api(
                data={},
                source=self.api.query(
                    "Smart",
                    "getAttributes",
                    {"devicefile": self.data["disk"][uid]["canonicaldevicefile"]},
                ),
                key="attrname",
                vals=[
                    {"name": "attrname"},
                    {"name": "threshold", "default": 0},
                    {"name": "rawvalue", "default": 0},
                ],
            )
            if not tmp_data:
                continue

            vals = [
                "Raw_Read_Error_Rate",
                "Spin_Up_Time",
                "Start_Stop_Count",
                "Reallocated_Sector_Ct",
                "Seek_Error_Rate",
                "Load_Cycle_Count",
                "UDMA_CRC_Error_Count",
                "Multi_Zone_Error_Rate",
            ]

            for tmp_val in vals:
                if tmp_val in tmp_data:
                    if (
                        isinstance(tmp_data[tmp_val]["rawvalue"], str)
                        and " " in tmp_data[tmp_val]["rawvalue"]
                    ):
                        tmp_data[tmp_val]["rawvalue"] = tmp_data[tmp_val][
                            "rawvalue"
                        ].split(" ")[0]

                    self.data["disk"][uid][tmp_val] = tmp_data[tmp_val]["rawvalue"]

    # ---------------------------
    #   get_fs
    # ---------------------------
    def get_fs(self):
        """Get all filesystems from OMV."""
        self.data["fs"] = parse_api(
            data=self.data["fs"],
            source=self.api.query("FileSystemMgmt", "enumerateFilesystems"),
            key="uuid",
            vals=[
                {"name": "uuid"},
                {"name": "parentdevicefile", "default": "unknown"},
                {"name": "label", "default": "unknown"},
                {"name": "type", "default": "unknown"},
                {"name": "mounted", "type": "bool", "default": False},
                {"name": "devicename", "default": "unknown"},
                {"name": "available", "default": 0},
                {"name": "size", "default": 0},
                {"name": "percentage", "default": 0},
                {"name": "_readonly", "type": "bool", "default": False},
                {"name": "_used", "type": "bool", "default": False},
                {"name": "propreadonly", "type": "bool", "default": False},
            ],
            skip=[
                {"name": "type", "value": "swap"},
                {"name": "type", "value": "iso9660"},
            ],
        )

        for uid in self.data["fs"]:
            tmp = self.data["fs"][uid]["devicename"]
            self.data["fs"][uid]["devicename"] = tmp[
                tmp.startswith("mapper/") and len("mapper/") :
            ]

            self.data["fs"][uid]["size"] = round(
                int(self.data["fs"][uid]["size"]) / 1073741824, 1
            )
            self.data["fs"][uid]["available"] = round(
                int(self.data["fs"][uid]["available"]) / 1073741824, 1
            )

    # ---------------------------
    #   get_service
    # ---------------------------
    def get_service(self):
        """Get OMV services status"""
        tmp = self.api.query("Services", "getStatus")
        if "data" in tmp:
            tmp = tmp["data"]

        self.data["service"] = parse_api(
            data=self.data["service"],
            source=tmp,
            key="name",
            vals=[
                {"name": "name"},
                {"name": "title", "default": "unknown"},
                {"name": "enabled", "type": "bool", "default": False},
                {"name": "running", "type": "bool", "default": False},
            ],
        )

    # ---------------------------
    #   get_plugin
    # ---------------------------
    def get_plugin(self):
        """Get OMV plugin status"""
        self.data["plugin"] = parse_api(
            data=self.data["plugin"],
            source=self.api.query("Plugin", "enumeratePlugins"),
            key="name",
            vals=[
                {"name": "name"},
                {"name": "installed", "type": "bool", "default": False},
            ],
        )

    # ---------------------------
    #   get_network
    # ---------------------------
    def get_network(self):
        """Get OMV plugin status"""
        self.data["network"] = parse_api(
            data=self.data["network"],
            source=self.api.query("Network", "enumerateDevices"),
            key="uuid",
            vals=[
                {"name": "uuid"},
                {"name": "devicename", "default": "unknown"},
                {"name": "type", "default": "unknown"},
                {"name": "method", "default": "unknown"},
                {"name": "address", "default": "unknown"},
                {"name": "netmask", "default": "unknown"},
                {"name": "gateway", "default": "unknown"},
                {"name": "mtu", "default": 0},
                {"name": "link", "type": "bool", "default": False},
                {"name": "wol", "type": "bool", "default": False},
                {"name": "rx-current", "source": "stats/rx_packets", "default": 0.0},
                {"name": "tx-current", "source": "stats/tx_packets", "default": 0.0},
            ],
            ensure_vals=[
                {"name": "rx-previous", "default": 0.0},
                {"name": "tx-previous", "default": 0.0},
                {"name": "rx", "default": 0.0},
                {"name": "tx", "default": 0.0},
            ],
            skip=[
                {"name": "type", "value": "loopback"},
            ],
        )

        for uid, vals in self.data["network"].items():
            current_tx = vals["tx-current"]
            previous_tx = vals["tx-previous"]
            if not previous_tx:
                previous_tx = current_tx

            delta_tx = max(0, current_tx - previous_tx) * 8
            self.data["network"][uid]["tx"] = round(
                delta_tx / self.option_scan_interval.seconds, 2
            )
            self.data["network"][uid]["tx-previous"] = current_tx

            current_rx = vals["rx-current"]
            previous_rx = vals["rx-previous"]
            if not previous_rx:
                previous_rx = current_rx

            delta_rx = max(0, current_rx - previous_rx) * 8
            self.data["network"][uid]["rx"] = round(
                delta_rx / self.option_scan_interval.seconds, 2
            )
            self.data["network"][uid]["rx-previous"] = current_rx

    # ---------------------------
    #   get_kvm
    # ---------------------------
    def get_kvm(self):
        """Get OMV KVM"""
        tmp = self.api.query("Kvm", "getVmList", {"start": 0, "limit": 999})
        if "data" not in tmp:
            return

        self.data["kvm"] = parse_api(
            data={},
            source=tmp["data"],
            key="vmname",
            vals=[
                {"name": "vmname"},
                {"name": "type", "source": "virttype", "default": "unknown"},
                {"name": "memory", "source": "mem", "default": "unknown"},
                {"name": "cpu", "default": "unknown"},
                {"name": "state", "default": "unknown"},
                {"name": "architecture", "source": "arch", "default": "unknown"},
                {"name": "autostart", "default": "unknown"},
                {"name": "vncexists", "type": "bool", "default": False},
                {"name": "spiceexists", "type": "bool", "default": False},
                {"name": "vncport", "default": "unknown"},
                {"name": "snapshots", "source": "snaps", "default": "unknown"},
            ],
        )

    # ---------------------------
    #   get_compose
    # ---------------------------
    def get_compose(self):
        """Get OMV compose"""
        tmp = self.api.query("compose", "getContainerList", {"start": 0, "limit": 999})
        if "data" not in tmp:
            return

        self.data["compose"] = parse_api(
            data={},
            source=tmp["data"],
            key="name",
            vals=[
                {"name": "name"},
                {"name": "image", "default": "unknown"},
                {"name": "project", "default": "unknown"},
                {"name": "service", "default": "unknown"},
                {"name": "created", "default": "unknown"},
                {"name": "state", "default": "unknown"},
            ],
        )
