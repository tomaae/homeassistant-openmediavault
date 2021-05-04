"""The OpenMediaVault integration."""

from .const import DATA_CLIENT, DOMAIN
from .omv_controller import OMVControllerData
from homeassistant.const import CONF_HOST

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
    controller = OMVControllerData(hass, config_entry)
    await controller.async_hwinfo_update()
    await controller.async_update()
    await controller.async_init()

    hass.data[DOMAIN][DATA_CLIENT][config_entry.entry_id] = controller
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "binary_sensor")
    )
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(config_entry, "switch")
    # )

    device_registry = await hass.helpers.device_registry.async_get_registry()
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={(DOMAIN, config_entry.data[CONF_HOST])},
        manufacturer="OpenMediaVault",
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
    await hass.config_entries.async_forward_entry_unload(config_entry, "binary_sensor")
    # await hass.config_entries.async_forward_entry_unload(config_entry, "switch")
    await controller.async_reset()
    hass.data[DOMAIN][DATA_CLIENT].pop(config_entry.entry_id)
    return True
