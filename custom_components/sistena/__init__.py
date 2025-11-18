"""Sistena Onix integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import SistenaOnixAPI
from .auth import SistenaOnixAuth
from .const import CONF_API_KEY, DATA_NAME, DATA_COORDINATOR, DATA_API, DOMAIN
from .climate import Regulator, RawRegulator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sistena Onix from a config entry."""
    config = entry.data

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
        name=f"Sistena Onix",
        update_method=api.async_get_devices,
        update_interval=timedelta(seconds=60),
    )
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady
    
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {}).update(
        {
            DATA_API: api,
            DATA_COORDINATOR: coordinator,
        }
    )

    await hass.config_entries.async_forward_entry_setups(entry, [Platform.CLIMATE])
    
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