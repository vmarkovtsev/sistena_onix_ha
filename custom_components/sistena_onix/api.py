"""API client for Sistena Onix."""

import logging
from typing import Any

import aiohttp

from .auth import SistenaOnixAuth

_LOGGER = logging.getLogger(__name__)


class SistenaOnixAPI:
    """Handle API calls to Sistena Onix."""

    def __init__(self, auth: SistenaOnixAuth, session: aiohttp.ClientSession) -> None:
        """Initialize Sistena Onix API."""
        self._auth = auth
        self._session = session

    async def async_get_devices(self) -> list | None:
        """Get list of devices."""
        url = "https://api.sistena.io/api/v2/devices"
        headers = {
            "Content-Type": "application/json",
            "from": "sistenaApp",
        }
        
        result = await self.async_make_request("GET", url, headers=headers)
        if result is None:
            return None
            
        # Return the devices array from the response
        return result.get("devices", [])

    async def async_get_device_status(self, device_id: str) -> dict[str, Any] | None:
        """Get device status by ID."""
        # TODO: Implement actual API call to get device status
        # This is a placeholder implementation
        return {}

    async def async_set_device_state(self, device_id: str, state: str) -> bool:
        """Set device state."""
        # TODO: Implement actual API call to set device state
        # This is a placeholder implementation
        return True

    async def async_create_device(self, device_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new device."""
        url = "https://api.sistena.io/api/v2/devices"
        headers = {
            "Content-Type": "application/json",
            "from": "sistenaApp"
        }
        
        result = await self.async_make_request("POST", url, headers=headers, json=device_data)
        return result

    async def async_make_request(self, method: str, url: str, **kwargs) -> dict[str, Any] | None:
        """Make an authenticated request to the API."""
        token = await self._auth.async_get_token()
        if not token:
            _LOGGER.error("No valid token available")
            return None

        headers = {
            "Content-Type": "application/json",
            "from": "sistenaApp",
            "token": token,
        }

        try:
            async with self._session.request(method, url, headers=headers, **kwargs) as response:
                if response.status != 200:
                    _LOGGER.error("API request failed: %s", response.status)
                    return None

                return await response.json()
        except Exception as ex:
            _LOGGER.error("API request failed: %s", ex)
            return None