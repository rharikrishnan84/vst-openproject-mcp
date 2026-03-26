from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_priorities() -> dict:
        """List all work package priorities (e.g. Low, Normal, High, Urgent, Immediate)."""
        return await client.get("/api/v3/priorities")

    @mcp.tool()
    async def get_priority(priority_id: int) -> dict:
        """Get details of a specific priority.

        Args:
            priority_id: Numeric ID of the priority.
        """
        return await client.get(f"/api/v3/priorities/{priority_id}")
