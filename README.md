# MCP Server Template

A simple starting point for building Model Context Protocol servers. If you want to connect an API or data source to Claude Desktop, this template gives you the basic structure to get started.

## What you get

This template has four example tools that you can replace with your own:

- Search for things
- Get details about a specific item
- List categories 
- Get popular or trending items

The code is split into three files:
- `main.py` - your MCP tools
- `api_service.py` - code that talks to your API
- `config.py` - settings and API keys

## How to use this template

### Step 1: Set up your environment

```bash
# Install the required packages
pip install -r requirements.txt

# Copy the example environment file
cp .env.example .env
# Edit .env and add your API key
```

### Step 2: Replace the example API

Open `api_service.py` and change:
- The API URL (currently `https://api.example.com/v1`)
- How authentication works 
- The endpoint paths to match your API

### Step 3: Update your MCP tools

Open `main.py` and replace the example tools with ones that make sense for your data:

```python
@mcp.tool
async def search_my_data(query: str) -> List[Dict[str, Any]]:
    """Search through my data source."""
    client = await get_api_client()
    result = await client.search(query)
    return result
```

### Step 4: Test it

```bash
python main.py
```

### Step 5: Connect to Claude Desktop

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/your/main.py"],
      "cwd": "/path/to/your/folder"
    }
  }
}
```

## Learning more about MCP

If you're new to building MCP servers, these resources will help:

- **[MCP Documentation](https://modelcontextprotocol.io/docs)** - Official docs and concepts
- **[FastMCP GitHub](https://github.com/jlowin/fastmcp)** - The framework this template uses
- **[Claude Desktop MCP Guide](https://docs.anthropic.com/en/docs/build-with-claude/mcp)** - How to connect your server to Claude
- **[MCP Examples](https://github.com/modelcontextprotocol/servers)** - Real MCP servers you can study

## Common questions

**What is MCP?** Model Context Protocol lets you add custom tools to Claude Desktop. Instead of Claude only knowing what it was trained on, you can give it access to live data from APIs, databases, or files.

**What can I build?** Anything that involves getting data for Claude to use. Search your company docs, check recent emails, get weather data, look up product info, etc.

**Do I need to know a lot about APIs?** Basic knowledge helps, but this template handles the hard parts. You mainly need to know what data you want and where to get it.

```python
# Update the base URL and authentication
self.base_url = settings.api_base_url  # Change in config.py
self.api_key = settings.api_key        # Set via environment variable

# Replace the example endpoints
async def search(self, query: str, limit: int = 10):
    return await self._make_request("GET", "/your-search-endpoint", ...)
```

### 2. Customize the MCP tools

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

### 3. Update configuration

Edit `config.py` to add any settings your API needs:

```python
@property
def your_setting(self) -> str:
    """Description of what this setting controls."""
    return os.getenv("YOUR_SETTING", "default_value")
```

### 4. Set up environment

Copy `.env.example` to `.env` and add your actual API credentials:

```bash
cp .env.example .env
# Edit .env with your API key and other settings
```

## Running the server

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
python main.py
```

Connect to Claude Desktop by adding this to your `claude_desktop_config.json`:

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