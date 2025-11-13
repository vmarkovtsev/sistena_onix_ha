"""API client for Sistena Onix."""

import logging
from typing import Any, Dict, Optional

import aiohttp

from .auth import SistenaOnixAuth

_LOGGER = logging.getLogger(__name__)


class SistenaOnixAPI:
    """Handle API calls to Sistena Onix."""

    def __init__(self, auth: SistenaOnixAuth, session: aiohttp.ClientSession) -> None:
        """Initialize Sistena Onix API."""
        self._auth = auth
        self._session = session

    async def async_get_devices(self) -> Optional[list]:
        """Get list of devices."""
        # TODO: Implement actual API call to get devices
        # This is a placeholder implementation
        return []

    async def async_get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device status by ID."""
        # TODO: Implement actual API call to get device status
        # This is a placeholder implementation
        return {}

    async def async_set_device_state(self, device_id: str, state: str) -> bool:
        """Set device state."""
        # TODO: Implement actual API call to set device state
        # This is a placeholder implementation
        return True

    async def async_make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make an authenticated request to the API."""
        token = await self._auth.async_get_token()
        if not token:
            _LOGGER.error("No valid token available")
            return None

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        try:
            async with self._session.request(method, url, headers=headers, **kwargs) as response:
                if response.status != 200:
                    _LOGGER.error("API request failed: %s", response.status)
                    return None

                return await response.json()
        except Exception as ex:
            _LOGGER.error("API request failed: %s", ex)
            return None