"""Config flow for Sistena Onix integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .auth import SistenaOnixAuth
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sistena Onix."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("api_key"): str,
                        vol.Required("email"): str,
                        vol.Required("password"): str,
                    }
                ),
            )
    
        # Check authentication
        auth = SistenaOnixAuth(**user_input, session=aiohttp.ClientSession())
        if not await auth.async_refresh_token():
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(sch.STEP_USER),
                errors={"base": "Failed to authenticate"},
            )

        return self.async_create_entry(title="Sistena Onix", data=user_input)
