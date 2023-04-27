"""Definitions for OMV sensor entities."""
from dataclasses import dataclass, field
from typing import List
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfDataRate

from .const import (
    SCHEMA_SERVICE_SYSTEM_REBOOT,
    SCHEMA_SERVICE_SYSTEM_SHUTDOWN,
    SERVICE_SYSTEM_REBOOT,
    SERVICE_SYSTEM_SHUTDOWN,
    SERVICE_KVM_START,
    SCHEMA_SERVICE_KVM_START,
    SERVICE_KVM_STOP,
    SCHEMA_SERVICE_KVM_STOP,
    SERVICE_KVM_RESTART,
    SCHEMA_SERVICE_KVM_RESTART,
    SERVICE_KVM_SNAPSHOT,
    SCHEMA_SERVICE_KVM_SNAPSHOT,
)

DEVICE_ATTRIBUTES_CPUUSAGE = [
    "loadAverage_1",
    "loadAverage_5",
    "loadAverage_15",
]

DEVICE_ATTRIBUTES_FS = [
    "size",
    "available",
    "type",
    "devicename",
    "_readonly",
    "_used",
    "mounted",
    "propreadonly",
]

DEVICE_ATTRIBUTES_DISK = [
    "canonicaldevicefile",
    "size",
    "vendor",
    "model",
    "description",
    "serialnumber",
    "israid",
    "isroot",
    "isreadonly",
]

DEVICE_ATTRIBUTES_DISK_SMART = [
    "Raw_Read_Error_Rate",
    "Spin_Up_Time",
    "Start_Stop_Count",
    "Reallocated_Sector_Ct",
    "Seek_Error_Rate",
    "Load_Cycle_Count",
    "UDMA_CRC_Error_Count",
    "Multi_Zone_Error_Rate",
]

DEVICE_ATTRIBUTES_NETWORK = [
    "type",
    "method",
    "address",
    "netmask",
    "gateway",
    "mtu",
    "link",
    "wol",
]

DEVICE_ATTRIBUTES_KVM = [
    "type",
    "memory",
    "cpu",
    "architecture",
    "autostart",
    "vncexists",
    "spiceexists",
    "vncport",
    "snapshots",
]

DEVICE_ATTRIBUTES_COMPOSE = [
    "image",
    "project",
    "service",
    "created",
]


@dataclass
class OMVSensorEntityDescription(SensorEntityDescription):
    """Class describing OMV entities."""

    ha_group: str = ""
    ha_connection: str = ""
    ha_connection_value: str = ""
    data_path: str = ""
    data_attribute: str = ""
    data_name: str = ""
    data_uid: str = ""
    data_reference: str = ""
    data_attributes_list: List = field(default_factory=lambda: [])
    func: str = "OMVSensor"


SENSOR_TYPES = {
    "system_cpuUsage": OMVSensorEntityDescription(
        key="system_cpuUsage",
        name="CPU load",
        icon="mdi:speedometer",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        device_class=None,
        state_class=None,
        entity_category=None,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="cpuUsage",
        data_name="",
        data_uid="",
        data_reference="",
        data_attributes_list=DEVICE_ATTRIBUTES_CPUUSAGE,
    ),
    "system_memUsage": OMVSensorEntityDescription(
        key="system_memUsage",
        name="Memory",
        icon="mdi:memory",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        device_class=None,
        state_class=None,
        entity_category=None,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="memUsage",
        data_name="",
        data_uid="",
        data_reference="",
    ),
    "system_uptimeEpoch": OMVSensorEntityDescription(
        key="system_uptimeEpoch",
        name="Uptime",
        icon="mdi:clock-outline",
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.TIMESTAMP,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        ha_group="System",
        data_path="hwinfo",
        data_attribute="uptimeEpoch",
        data_name="",
        data_uid="",
        data_reference="",
        func="OMVUptimeSensor",
    ),
    "fs": OMVSensorEntityDescription(
        key="fs",
        name="",
        icon="mdi:file-tree",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        device_class=None,
        state_class=None,
        entity_category=None,
        ha_group="Filesystem",
        data_path="fs",
        data_attribute="percentage",
        data_name="devicename",
        data_uid="",
        data_reference="uuid",
        data_attributes_list=DEVICE_ATTRIBUTES_FS,
    ),
    "disk": OMVSensorEntityDescription(
        key="disk",
        name="",
        icon="mdi:harddisk",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_category=None,
        ha_group="Disk",
        data_path="disk",
        data_attribute="temperature",
        data_name="devicename",
        data_uid="",
        data_reference="devicename",
        data_attributes_list=DEVICE_ATTRIBUTES_DISK,
        func="OMVDiskSensor",
    ),
    "network_tx": OMVSensorEntityDescription(
        key="network_tx",
        name="TX",
        icon="mdi:upload-network-outline",
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        ha_group="System",
        data_path="network",
        data_attribute="tx",
        data_name="devicename",
        data_uid="",
        data_reference="uuid",
        data_attributes_list=DEVICE_ATTRIBUTES_NETWORK,
    ),
    "network_rx": OMVSensorEntityDescription(
        key="network_rx",
        name="RX",
        icon="mdi:download-network-outline",
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=None,
        ha_group="System",
        data_path="network",
        data_attribute="rx",
        data_name="devicename",
        data_uid="",
        data_reference="uuid",
        data_attributes_list=DEVICE_ATTRIBUTES_NETWORK,
    ),
    "kvm": OMVSensorEntityDescription(
        key="kvm",
        name="",
        icon="mdi:server",
        entity_category=None,
        ha_group="KVM",
        data_path="kvm",
        data_attribute="state",
        data_name="vmname",
        data_uid="",
        data_reference="vmname",
        data_attributes_list=DEVICE_ATTRIBUTES_KVM,
        func="OMVKVMSensor",
    ),
    "compose": OMVSensorEntityDescription(
        key="compose",
        name="",
        icon="mdi:text-box-multiple-outline",
        entity_category=None,
        ha_group="Compose",
        data_path="compose",
        data_attribute="state",
        data_name="name",
        data_uid="",
        data_reference="name",
        data_attributes_list=DEVICE_ATTRIBUTES_COMPOSE,
    ),
}

SENSOR_SERVICES = [
    [SERVICE_SYSTEM_REBOOT, SCHEMA_SERVICE_SYSTEM_REBOOT, "restart"],
    [SERVICE_SYSTEM_SHUTDOWN, SCHEMA_SERVICE_SYSTEM_SHUTDOWN, "stop"],
    [SERVICE_KVM_START, SCHEMA_SERVICE_KVM_START, "start"],
    [SERVICE_KVM_STOP, SCHEMA_SERVICE_KVM_STOP, "stop"],
    [SERVICE_KVM_RESTART, SCHEMA_SERVICE_KVM_RESTART, "restart"],
    [SERVICE_KVM_SNAPSHOT, SCHEMA_SERVICE_KVM_SNAPSHOT, "snapshot"],
]
