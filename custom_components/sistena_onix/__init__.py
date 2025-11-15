"""Sistena Onix integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import SistenaOnixAPI
from .auth import SistenaOnixAuth
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sistena Onix from a config entry."""
    # Create an aiohttp session for the integration
    session = aiohttp.ClientSession()
    
    # Create authentication instance
    auth = SistenaOnixAuth(
        api_key=entry.data["api_key"],
        email=entry.data["email"],
        password=entry.data["password"],
        session=session,
    )
    
    api = SistenaOnixAPI(auth, session)
    
    hass.data[DOMAIN] = {"api": api}
    
    # TODO: Implement the actual setup logic
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Close the aiohttp session
    if DOMAIN in hass.data:
        session = hass.data[DOMAIN].get("session")
        if session:
            await session.close()
        hass.data.pop(DOMAIN, None)
    
    # TODO: Implement the actual unload logic
    return True