"""OpenMediaVault integration"""

import logging

from .const import (
    DOMAIN,
    DATA_CLIENT,
)

from .omv_controller import OpenMediaVaultControllerData

_LOGGER = logging.getLogger(__name__)


# ---------------------------
#   async_setup
# ---------------------------
async def async_setup(hass, _config):
    """Set up configured OMV Controller."""
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][DATA_CLIENT] = {}
    return True


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry):
    """Set up OMV config entry."""
    controller = OpenMediaVaultControllerData(hass, config_entry)
    await controller.async_update()
    await controller.async_init()

    hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id] = controller
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    device_registry = await hass.helpers.device_registry.async_get_registry()
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        manufacturer="OpenMediaVault",
        # model=controller.data["hwinfo"]["model"],
        name=controller.data["hwinfo"]["hostname"],
        sw_version=controller.data["hwinfo"]["version"],
    )

    return True


# ---------------------------
#   async_unload_entry
# ---------------------------
async def async_unload_entry(hass, config_entry):
    """Unload OMV config entry."""
    controller = hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id]
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    await controller.async_reset()
    hass.data[DOMAIN][DATA_CLIENT].pop(config_entry.entry_id)
    return True
