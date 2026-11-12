
import asyncio
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient


# Get project root directory
BASE_DIR = Path(__file__).resolve().parents[1]


# Configure both MCP servers
server_config = {
    "expense": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [
            str(BASE_DIR / "servers" / "expense_server" / "server.py")
        ],
    },

    "calculation": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [
            str(BASE_DIR / "servers" / "calculation_server" / "server.py")
        ],
    },
}


async def main():

    # Connect to MCP servers
    client = MultiServerMCPClient(server_config)

    # Discover available tools
    tools = await client.get_tools()

    print("\nConnected to MCP Servers!")

    print("\nAvailable Tools:")

    for tool in tools:
        print(f"\nTool Name: {tool.name}")
        print(f"Description: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
