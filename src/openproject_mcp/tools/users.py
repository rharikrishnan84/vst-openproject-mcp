from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def get_current_user() -> dict:
        """Get the profile of the currently authenticated user."""
        return await client.get("/api/v3/users/me")

    @mcp.tool()
    async def list_users(
        page: int = 1,
        page_size: int = 25,
        name: str | None = None,
        status: str | None = None,
    ) -> dict:
        """List users. Requires admin privileges.

        Args:
            page: Page number (starts at 1).
            page_size: Results per page (max 200).
            name: Filter by name or email (substring match).
            status: Filter by status: 'active', 'registered', 'locked', 'invited'.
        """
        import json

        filters = []
        if name:
            filters.append({"name": {"operator": "~", "values": [name]}})
        if status:
            filters.append({"status": {"operator": "=", "values": [status]}})

        params: dict = {"offset": page, "pageSize": page_size}
        if filters:
            params["filters"] = json.dumps(filters)

        return await client.get("/api/v3/users", params=params)

    @mcp.tool()
    async def get_user(user_id: int) -> dict:
        """Get details of a specific user by ID.

        Args:
            user_id: Numeric user ID.
        """
        return await client.get(f"/api/v3/users/{user_id}")

    @mcp.tool()
    async def list_project_members(project_id: str, page: int = 1, page_size: int = 25) -> dict:
        """List all members of a project with their roles.

        Args:
            project_id: Numeric ID or identifier of the project.
            page: Page number (starts at 1).
            page_size: Results per page (max 200).
        """
        import json

        filters = json.dumps([{"project": {"operator": "=", "values": [str(project_id)]}}])
        return await client.get(
            "/api/v3/memberships",
            params={"offset": page, "pageSize": page_size, "filters": filters},
        )
