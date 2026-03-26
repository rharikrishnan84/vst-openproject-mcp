from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_statuses() -> dict:
        """List all available work package statuses (e.g. New, In Progress, Closed)."""
        return await client.get("/api/v3/statuses")

    @mcp.tool()
    async def get_status(status_id: int) -> dict:
        """Get details of a specific work package status.

        Args:
            status_id: Numeric ID of the status.
        """
        return await client.get(f"/api/v3/statuses/{status_id}")
