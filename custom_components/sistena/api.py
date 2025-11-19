"""API client for Sistena Onix."""

import logging
from typing import Any

import aiohttp

from .auth import SistenaOnixAuth

_LOGGER = logging.getLogger(__name__)


class SistenaOnixAPI:
    """Handle API calls to Sistena Onix."""

    # API base URL
    BASE_URL = "https://api.sistena.io/api/v2"

    def __init__(self, auth: SistenaOnixAuth, session: aiohttp.ClientSession) -> None:
        """Initialize Sistena Onix API."""
        self._auth = auth
        self._session = session

    async def async_get_devices(self) -> list:
        """Get list of devices."""
        result = await self.async_make_request("GET", f"{self.BASE_URL}/devices")
        if result is None:
            return []

        # Return the devices array from the response
        return result.get("devices", [])

    async def async_get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get device data by ID."""
        return await self.async_make_request(
            "GET",
            f"{self.BASE_URL}/devices/{device_id}",
        )

    async def async_make_request(self, method: str, url: str, **kwargs) -> dict[str, Any] | None:
        """Make an authenticated request to the API."""
        token = await self._auth.async_get_token()
        if not token:
            _LOGGER.error("No valid token available")
            return None

        _LOGGER.debug("Sending %s API request to %s: %s", method, url, kwargs)

        headers = {
            "Content-Type": "application/json",
            "from": "sistenaApp",
            "token": token,
        }

        try:
            async with self._session.request(method, url, headers=headers, **kwargs) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "API request failed: %s: %s\n%s",
                        url,
                        response.status,
                        "\n".join(f"{k}: {v}" for k, v in headers.items()),
                    )
                    return None

                return await response.json()
        except Exception as ex:
            _LOGGER.error("API request failed: %s", ex)
            return None

    async def async_set_register_value(self, device_id: str, register: int, value: int) -> bool:
        """Set register value for a device."""
        url = f"{self.BASE_URL}/devices/{device_id}/registers"
        data = {"register": register, "value": value}

        result = await self.async_make_request("POST", url, json=data)
        return result is not None
