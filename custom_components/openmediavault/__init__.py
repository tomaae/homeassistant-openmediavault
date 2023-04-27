"""The OpenMediaVault integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS
from .omv_controller import OMVControllerData


# ---------------------------
#   async_setup
# ---------------------------
async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up configured OMV Controller."""
    hass.data[DOMAIN] = {}
    return True


# ---------------------------
#   update_listener
# ---------------------------
async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up OMV config entry."""
    hass.data.setdefault(DOMAIN, {})
    controller = OMVControllerData(hass, config_entry)
    await controller.async_hwinfo_update()
    await controller.async_update()

    if not controller.data:
        raise ConfigEntryNotReady()

    await controller.async_init()
    hass.data[DOMAIN][config_entry.entry_id] = controller

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    return True


# ---------------------------
#   async_unload_entry
# ---------------------------
async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload TrueNAS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        controller = hass.data[DOMAIN][config_entry.entry_id]
        await controller.async_reset()
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return True
