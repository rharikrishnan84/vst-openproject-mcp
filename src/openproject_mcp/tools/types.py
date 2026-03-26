from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_types() -> dict:
        """List all work package types available globally (e.g. Task, Bug, Feature, Milestone)."""
        return await client.get("/api/v3/types")

    @mcp.tool()
    async def list_project_types(project_id: str) -> dict:
        """List work package types enabled for a specific project.

        Args:
            project_id: Numeric ID or identifier of the project.
        """
        return await client.get(f"/api/v3/projects/{project_id}/types")

    @mcp.tool()
    async def get_type(type_id: int) -> dict:
        """Get details of a specific work package type.

        Args:
            type_id: Numeric ID of the type.
        """
        return await client.get(f"/api/v3/types/{type_id}")
