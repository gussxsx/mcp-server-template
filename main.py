"""
Your MCP Server Template

A clean starting point for building Model Context Protocol servers with FastMCP.
This template includes everything you need to get started - just replace the example
tools with your own API integrations or data sources.

Built with real-world patterns learned from production MCP servers.
"""

import asyncio
import logging
from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from api_service import get_api_client, cleanup_api_client

# Set up logging so you can actually see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create your MCP server - this is what Claude will connect to
mcp = FastMCP("Your MCP Server", version="1.0.0")


@mcp.tool
async def search_items(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for items using a text query.

    This is your basic search tool - every MCP server needs one of these.
    Replace this with whatever search functionality your API provides.

    Args:
        query: What to search for (e.g., "python tutorials", "restaurants near me")
        limit: How many results to return (default: 10, max: 50)

    Returns:
        List of items with basic information. Structure this however makes sense
        for your data - just keep it consistent across all your tools.
    """
    try:
        # Get your API client (see api_service.py for the pattern)
        client = await get_api_client()

        # Make the actual API call
        result = await client.search(query, limit)

        # Transform the API response into something Claude can understand
        # This is where you decide what data to expose and how to structure it
        items = []
        for item in result.get("results", []):
            item_info = {
                "id": item.get("id"),
                "title": item.get("title") or item.get("name"),  # APIs are inconsistent
                "description": item.get("description", "").strip(),
                "url": item.get("url"),
                "tags": item.get("tags", []),
                # Add whatever fields make sense for your use case
            }
            items.append(item_info)

        return items

    except Exception as e:
        # Always log errors for debugging, but return user-friendly messages
        logger.error(f"Search failed: {str(e)}")
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool
async def get_item_details(item_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific item.

    The classic "get more info" tool. Your search gives basic info,
    this gives the full details when someone wants to dig deeper.

    Args:
        item_id: The unique identifier for the item

    Returns:
        Detailed information about the item. Include everything that might
        be useful - descriptions, metadata, related items, whatever your API provides.
    """
    try:
        client = await get_api_client()
        item = await client.get_details(item_id)

        # Structure all the detailed information
        details = {
            "id": item.get("id"),
            "title": item.get("title") or item.get("name"),
            "description": item.get("description", "").strip(),
            "full_description": item.get("full_description", "").strip(),
            "url": item.get("url"),
            "created_date": item.get("created_at") or item.get("date"),
            "author": item.get("author") or item.get("creator"),
            "tags": item.get("tags", []),
            "category": item.get("category"),
            "metadata": item.get("metadata", {}),
            # Add fields specific to your domain
        }

        return details

    except Exception as e:
        logger.error(f"Failed to get details for {item_id}: {str(e)}")
        return {"error": f"Failed to get item details: {str(e)}"}


@mcp.tool
async def list_categories() -> List[Dict[str, Any]]:
    """
    Get available categories or types.

    Most APIs have some way to browse by category. This makes it discoverable
    so users can explore what's available without knowing exactly what to search for.

    Returns:
        List of categories with counts and descriptions where available.
    """
    try:
        client = await get_api_client()
        result = await client.list_categories()

        categories = []
        for category in result.get("results", []):
            category_info = {
                "id": category.get("id"),
                "name": category.get("name"),
                "description": category.get("description"),
                "item_count": category.get("count") or category.get("items"),
                # Some APIs include preview images or icons
                "icon": category.get("icon"),
            }
            categories.append(category_info)

        return categories

    except Exception as e:
        logger.error(f"Failed to list categories: {str(e)}")
        return [{"error": f"Failed to list categories: {str(e)}"}]


@mcp.tool
async def get_popular_items(
    limit: int = 10, category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get trending, popular, or featured items.

    Every good MCP server needs a "discovery" tool for when users want to browse
    rather than search. This could be trending items, top rated, most recent, etc.

    Args:
        limit: Maximum number of items to return (default: 10, max: 50)
        category: Optional category to filter by

    Returns:
        List of popular items with the same structure as search results.
    """
    try:
        client = await get_api_client()

        # If they specified a category, filter by it
        if category:
            # First verify the category exists (good user experience)
            categories_result = await client.list_categories()
            category_id = None
            for cat in categories_result.get("results", []):
                if cat.get("name", "").lower() == category.lower():
                    category_id = cat.get("id")
                    break

            if category_id:
                result = await client.get_items_by_category(category_id, limit)
            else:
                return [{"error": f"Category '{category}' not found"}]
        else:
            # Get general popular/trending items
            result = await client.get_popular_items(limit)

        # Use the same structure as your search results for consistency
        items = []
        for item in result.get("results", []):
            item_info = {
                "id": item.get("id"),
                "title": item.get("title") or item.get("name"),
                "description": item.get("description", "").strip(),
                "url": item.get("url"),
                "tags": item.get("tags", []),
                "popularity_score": item.get("score") or item.get("rating"),
            }
            items.append(item_info)

        return items

    except Exception as e:
        logger.error(f"Failed to get popular items: {str(e)}")
        return [{"error": f"Failed to get popular items: {str(e)}"}]


async def cleanup():
    """
    Clean up resources when the server shuts down.

    This is important! Always close your HTTP clients, database connections,
    file handles, etc. when the server stops. Otherwise you'll leak resources.
    """
    await cleanup_api_client()


if __name__ == "__main__":
    try:
        # Set up cleanup to run when the program exits
        import atexit

        atexit.register(lambda: asyncio.run(cleanup()))

        # Start the MCP server - this will keep running until interrupted
        logger.info("Starting MCP server...")
        mcp.run()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("Server stopped by user")
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Server crashed: {e}")
    finally:
        # Always clean up, even if something went wrong
        asyncio.run(cleanup())
