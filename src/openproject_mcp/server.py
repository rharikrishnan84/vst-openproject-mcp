import asyncio
import sys

from mcp.server.fastmcp import FastMCP

from openproject_mcp.config import get_settings
from openproject_mcp.client import OpenProjectClient
from openproject_mcp.tools import register_all


def main() -> None:
    # Windows: use SelectorEventLoop for compatibility with some stdio transports
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    settings = get_settings()
    client = OpenProjectClient(settings)

    mcp = FastMCP(
        "openproject",
        instructions=(
            "You are connected to an OpenProject instance. "
            "Use the available tools to manage projects, work packages, users, "
            "versions, statuses, types, and priorities. "
            "Always fetch current lock versions before updating work packages."
        ),
    )

    register_all(mcp, client)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
