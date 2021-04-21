"""Config flow to configure OpenMediaVault."""

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)
from homeassistant.config_entries import CONN_CLASS_LOCAL_POLL, ConfigFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SSL,
    CONF_VERIFY_SSL,
    CONF_USERNAME,
)
from homeassistant.core import callback

from .const import (
    DEFAULT_DEVICE_NAME,
    DEFAULT_HOST,
    DEFAULT_PASSWORD,
    DEFAULT_SSL,
    DEFAULT_SSL_VERIFY,
    DEFAULT_USERNAME,
    DOMAIN,
)
from .omv_api import OpenMediaVaultAPI

# ---------------------------
#   configured_instances
# ---------------------------
@callback
def configured_instances(hass):
    """Return a set of configured instances."""
    return set(
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    )


# ---------------------------
#   OMVConfigFlow
# ---------------------------
class OMVConfigFlow(ConfigFlow, domain=DOMAIN):
    """OMVConfigFlow class."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize OMVConfigFlow."""

    async def async_step_import(self, user_input=None):
        """Occurs when a previous entry setup fails and is re-initiated."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            # Check if instance with this name already exists
            if user_input[CONF_NAME] in configured_instances(self.hass):
                errors["base"] = "name_exists"

            # Test connection
            api = await self.hass.async_add_executor_job(
                OpenMediaVaultAPI,
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_SSL],
                user_input[CONF_VERIFY_SSL],
            )

            if not await self.hass.async_add_executor_job(api.connect):
                _LOGGER.error("OpenMediaVault %s connect error", api.error)
                errors[CONF_HOST] = api.error

            # Save instance
            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

            return self._show_config_form(user_input=user_input, errors=errors)

        return self._show_config_form(
            user_input={
                CONF_NAME: DEFAULT_DEVICE_NAME,
                CONF_HOST: DEFAULT_HOST,
                CONF_USERNAME: DEFAULT_USERNAME,
                CONF_PASSWORD: DEFAULT_PASSWORD,
                CONF_SSL: DEFAULT_SSL,
                CONF_VERIFY_SSL: DEFAULT_SSL_VERIFY,
            },
            errors=errors,
        )

    def _show_config_form(self, user_input, errors=None):
        """Show the configuration form."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                    vol.Optional(CONF_SSL, default=user_input[CONF_SSL]): bool,
                    vol.Optional(
                        CONF_VERIFY_SSL, default=user_input[CONF_VERIFY_SSL]
                    ): bool,
                }
            ),
            errors=errors,
        )
