"""
API Service Template

This is where you put all your external API interactions. Keep this separate from
your main.py so your MCP tools stay clean and focused on data transformation.

This template shows the patterns that work well in production - connection pooling,
error handling, retries, and proper resource cleanup.
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """
    Custom exception for API-related errors.

    Always create custom exceptions for your domain - it makes debugging
    so much easier when you can tell where an error came from.
    """

    pass


class APIClient:
    """
    Your main API client class.

    This handles all the HTTP requests, authentication, rate limiting, etc.
    Keep all the messy networking code here so your MCP tools can focus
    on the business logic.
    """

    def __init__(self):
        self.base_url = settings.api_base_url
        self.api_key = settings.api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create the HTTP client.

        Using a single client for all requests is more efficient than creating
        a new one each time. Connection pooling, keep-alive, all that good stuff.
        """
        if self._client is None:
            # Configure your HTTP client with sensible defaults
            self._client = httpx.AsyncClient(
                timeout=30.0,  # Don't wait forever for slow APIs
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
                headers={
                    "User-Agent": "Your MCP Server/1.0.0",
                    # Add any required headers here
                },
            )
        return self._client

    async def close(self):
        """Close the HTTP client and clean up connections."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling and retries.

        This is your central request method - all API calls go through here.
        Add authentication, rate limiting, retries, whatever your API needs.
        """
        client = await self.get_client()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Add authentication (adjust for your API)
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["api_key"] = self.api_key

        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()

            # Most APIs return JSON, but adjust as needed
            return response.json()

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors gracefully
            if e.response.status_code == 404:
                raise APIError(f"Not found: {endpoint}")
            elif e.response.status_code == 401:
                raise APIError("Invalid API key or authentication failed")
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded - try again later")
            else:
                raise APIError(f"API error {e.response.status_code}: {e.response.text}")

        except httpx.RequestError as e:
            # Network errors, timeouts, etc.
            raise APIError(f"Request failed: {str(e)}")

    async def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for items using the API.

        Replace this with whatever search endpoint your API provides.
        Keep the method names descriptive and the parameters simple.
        """
        params = {
            "q": query,
            "limit": min(limit, 50),  # Enforce reasonable limits
            # Add any other search parameters your API supports
        }

        return await self._make_request("GET", "/search", params=params)

    async def get_details(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific item.

        This usually maps to a GET /items/{id} or similar endpoint.
        """
        return await self._make_request("GET", f"/items/{item_id}")

    async def list_categories(self) -> Dict[str, Any]:
        """
        Get available categories or types.

        Most APIs have some kind of categorization system.
        This makes it browsable for users who don't know what to search for.
        """
        return await self._make_request("GET", "/categories")

    async def get_popular_items(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get trending, popular, or featured items.

        This could be sorted by popularity, date, rating, whatever makes
        sense for your domain.
        """
        params = {"limit": min(limit, 50)}
        return await self._make_request("GET", "/popular", params=params)

    async def get_items_by_category(
        self, category_id: str, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get items filtered by category.

        Usually this is either a query parameter on the main endpoint
        or a separate endpoint like /categories/{id}/items
        """
        params = {"limit": min(limit, 50)}
        return await self._make_request(
            "GET", f"/categories/{category_id}/items", params=params
        )


# Global client instance - reuse connections across requests
_client: Optional[APIClient] = None


async def get_api_client() -> APIClient:
    """
    Get the shared API client instance.

    This singleton pattern ensures we reuse the same HTTP client
    across all requests, which is much more efficient.
    """
    global _client
    if _client is None:
        _client = APIClient()
    return _client


async def cleanup_api_client():
    """
    Clean up the API client when shutting down.

    Always call this when your server stops to properly close
    HTTP connections and avoid resource leaks.
    """
    global _client
    if _client:
        await _client.close()
        _client = None
