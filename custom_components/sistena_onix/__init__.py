"""Sistena Onix integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_NAME, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import SistenaOnixAPI
from .auth import SistenaOnixAuth
from .const import CONF_API_KEY, DOMAIN
from .device import Regulator, RawRegulator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sistena Onix from a config entry."""
    config = entry.data
    name = config[CONF_NAME]

    # Create an aiohttp session for the integration
    session = aiohttp.ClientSession()
    
    # Create authentication instance
    auth = SistenaOnixAuth(
        api_key=config[CONF_API_KEY],
        email=config[CONF_EMAIL],
        password=config[CONF_PASSWORD],
        session=session,
    )
    
    api = SistenaOnixAPI(auth, session)
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Sistena Onix {name}",
        update_method=api.async_get_devices,
        update_interval=timedelta(seconds=30),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, Platform.CLIMATE)
    )
    
    hass.data[DOMAIN] = {"api": api, "name": name, "coordinator": coordinator}
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Close the aiohttp session
    if DOMAIN in hass.data:
        session = hass.data[DOMAIN].get("session")
        if session:
            await session.close()
        hass.data.pop(DOMAIN, None)
    
    # Unload the climate platform
    return await hass.config_entries.async_unload_platforms(entry, Platform.CLIMATE)