"""Authentication for Sistena Onix API."""

import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SistenaOnixAuth:
    """Handle authentication with Sistena Onix API."""

    def __init__(
        self,
        api_key: str,
        email: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize Sistena Onix authentication."""
        self._api_key = api_key
        self._email = email
        self._password = password
        self._session = session
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: datetime | None = None

    @property
    def token(self) -> str | None:
        """Return the current token."""
        return self._token

    async def async_get_token(self) -> str | None:
        """Get a valid token."""
        if not self._token or self._expires_at <= datetime.now() + timedelta(minutes=5):
            await self.async_refresh_token()
        return self._token

    async def async_refresh_token(self) -> bool:
        """Refresh the token."""
        if self._refresh_token:
            return await self._async_refresh_token()
        return await self._async_signin()

    async def _async_signin(self) -> bool:
        """Sign in to get initial token."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self._api_key}"
        
        data = {
            "returnSecureToken": True,
            "email": self._email,
            "password": self._password,
        }

        try:
            async with self._session.post(url, json=data) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to sign in: %s", response.status)
                    return False

                result = await response.json()
                self._token = result["idToken"]
                self._refresh_token = result["refreshToken"]
                expires_in = int(result["expiresIn"])
                self._expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                return bool(self._token)
        except Exception as ex:
            _LOGGER.error("Failed to sign in: %s", ex)
            return False

    async def _async_refresh_token(self) -> bool:
        """Refresh the token using refresh token."""
        url = f"https://securetoken.googleapis.com/v1/token?key={self._api_key}"
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }

        try:
            async with self._session.post(url, json=data) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to refresh token: %s", response.status)
                    return False

                result = await response.json()
                self._token = result["idToken"]
                self._refresh_token = result["refreshToken"]
                expires_in = int(result["expiresIn"])
                self._expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                return bool(self._token)
        except Exception as ex:
            _LOGGER.error("Failed to refresh token: %s", ex)
            return False