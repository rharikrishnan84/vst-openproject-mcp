from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_versions(project_id: str) -> dict:
        """List all versions (milestones/sprints) for a project.

        Args:
            project_id: Numeric ID or identifier of the project.
        """
        return await client.get(f"/api/v3/projects/{project_id}/versions")

    @mcp.tool()
    async def get_version(version_id: int) -> dict:
        """Get details of a specific version.

        Args:
            version_id: Numeric ID of the version.
        """
        return await client.get(f"/api/v3/versions/{version_id}")

    @mcp.tool()
    async def create_version(
        project_id: str,
        name: str,
        description: str | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        status: str = "open",
        sharing: str = "none",
    ) -> dict:
        """Create a new version (milestone/sprint) in a project.

        Args:
            project_id: Numeric ID or identifier of the project.
            name: Display name of the version.
            description: Optional description.
            start_date: Start date in YYYY-MM-DD format.
            due_date: Due/end date in YYYY-MM-DD format.
            status: Version status: 'open', 'locked', 'closed'.
            sharing: Sharing scope: 'none', 'descendants', 'hierarchy', 'tree', 'system'.
        """
        body: dict = {
            "name": name,
            "status": status,
            "sharing": sharing,
            "_links": {"definingProject": {"href": f"/api/v3/projects/{project_id}"}},
        }
        if description:
            body["description"] = {"raw": description}
        if start_date:
            body["startDate"] = start_date
        if due_date:
            body["endDate"] = due_date
        return await client.post("/api/v3/versions", json=body)

    @mcp.tool()
    async def update_version(
        version_id: int,
        name: str | None = None,
        description: str | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        status: str | None = None,
        sharing: str | None = None,
    ) -> dict:
        """Update an existing version.

        Args:
            version_id: Numeric ID of the version to update.
            name: New display name.
            description: New description.
            start_date: New start date (YYYY-MM-DD).
            due_date: New end date (YYYY-MM-DD).
            status: New status: 'open', 'locked', 'closed'.
            sharing: New sharing scope.
        """
        body: dict = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = {"raw": description}
        if start_date is not None:
            body["startDate"] = start_date
        if due_date is not None:
            body["endDate"] = due_date
        if status is not None:
            body["status"] = status
        if sharing is not None:
            body["sharing"] = sharing
        return await client.patch(f"/api/v3/versions/{version_id}", json=body)
