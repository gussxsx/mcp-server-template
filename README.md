# MCP Server Template

A production-ready template for building Model Context Protocol servers with Python. If you want to connect an API or data source to Claude Desktop, this template gives you the basic structure to get started.

## What you get

This template includes:

- **Four example MCP tools** that you can replace with your own:
  - Search for things
  - Get details about a specific item
  - List categories 
  - Get popular or trending items

- **Clean architecture** split into three files:
  - `main.py` - your MCP tools and server setup
  - `api_service.py` - HTTP client with connection pooling, error handling, and retries
  - `config.py` - settings and environment variable management

- **Production patterns** - proper async/await, resource cleanup, and error handling

## Quick Start

### 1. Set up your environment

```bash
# Install the required packages
pip install -r requirements.txt

# Copy the example environment file
cp .env.example .env
# Edit .env and add your API key and settings
```

### 2. Customize for your API

Open `api_service.py` and update:
- The API URL (currently `https://api.example.com/v1`)
- Authentication method (currently using API key in params)
- The endpoint paths to match your API

```python
# Update the base URL and authentication
self.base_url = settings.api_base_url  # Change in config.py
self.api_key = settings.api_key        # Set via environment variable

# Replace the example endpoints
async def search(self, query: str, limit: int = 10):
    return await self._make_request("GET", "/your-search-endpoint", ...)
```

### 3. Update your MCP tools

Edit `main.py` to replace the example tools with your domain-specific functionality:

```python
@mcp.tool
async def your_tool_name(param: str) -> Dict[str, Any]:
    """
    Describe what your tool does.
    
    Args:
        param: Explain your parameters
        
    Returns:
        Explain what you return
    """
    client = await get_api_client()
    result = await client.your_api_method(param)
    
    # Transform the API response into the format Claude needs
    return {"your": "data"}
```

### 4. Test your server

```bash
python main.py
```

### 5. Connect to Claude Desktop

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "your-server": {
      "command": "python",
      "args": ["/absolute/path/to/your-server/main.py"],
      "cwd": "/absolute/path/to/your-server",
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Advanced Configuration

### Adding custom settings

Edit `config.py` to add any settings your API needs:

```python
@property
def your_setting(self) -> str:
    """Description of what this setting controls."""
    return os.getenv("YOUR_SETTING", "default_value")
```

### Environment variables

All sensitive data should go in your `.env` file:

```bash
API_KEY=your_actual_api_key
API_BASE_URL=https://your-api.com/v1
# Add other settings as needed
```

## Learning More

### MCP Resources

- **[MCP Documentation](https://modelcontextprotocol.io/docs)** - Official docs and concepts
- **[FastMCP GitHub](https://github.com/jlowin/fastmcp)** - The framework this template uses
- **[Claude Desktop MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)** - How to connect your server to Claude
- **[MCP Examples](https://github.com/modelcontextprotocol/servers)** - Real MCP servers you can study

### Common Questions

**What is MCP?** Model Context Protocol lets you add custom tools to Claude Desktop. Instead of Claude only knowing what it was trained on, you can give it access to live data from APIs, databases, or files.

**What can I build?** Anything that involves getting data for Claude to use. Search your company docs, check recent emails, get weather data, look up product info, etc.

**Do I need to know a lot about APIs?** Basic knowledge helps, but this template handles the hard parts. You mainly need to know what data you want and where to get it.

## License

This template is released under the MIT License. See [LICENSE](LICENSE) for details.

**Note:** When using this template, make sure to update the LICENSE file with your own name or organization before publishing your MCP server.