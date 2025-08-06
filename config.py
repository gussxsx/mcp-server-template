"""
Configuration Management

Keep all your settings in one place. This makes it easy to change API endpoints,
adjust timeouts, or switch between development and production environments.

The pattern here loads from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.

    This is a simple but effective pattern for configuration.
    Add new settings here as properties, and they'll automatically
    load from environment variables.
    """

    @property
    def api_base_url(self) -> str:
        """
        Base URL for your external API.

        Change this to point to your actual API. Could be REST, GraphQL,
        or whatever protocol your data source uses.
        """
        return os.getenv("API_BASE_URL", "https://api.example.com/v1")

    @property
    def api_key(self) -> str:
        """
        API key for authentication.

        Most APIs require some kind of authentication. This could be an API key,
        bearer token, or whatever your API uses. Load it from environment
        variables so it doesn't end up in your code.
        """
        key = os.getenv("API_KEY")
        if not key:
            raise ValueError(
                "API_KEY environment variable is required. "
                "Get your API key from [YOUR_API_PROVIDER] and add it to your .env file."
            )
        return key

    @property
    def api_timeout(self) -> float:
        """How long to wait for API responses (in seconds)."""
        return float(os.getenv("API_TIMEOUT", "30.0"))

    @property
    def max_results(self) -> int:
        """Maximum number of results to return from any single API call."""
        return int(os.getenv("MAX_RESULTS", "50"))

    @property
    def cache_ttl(self) -> int:
        """How long to cache API responses (in seconds). 0 = no caching."""
        return int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default


# Create a global settings instance
# This is imported by other modules that need configuration
settings = Settings()
