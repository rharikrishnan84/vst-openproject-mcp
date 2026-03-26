from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_projects(page: int = 1, page_size: int = 25) -> dict:
        """List all projects accessible to the current user.

        Args:
            page: Page number (starts at 1).
            page_size: Number of results per page (max 200).
        """
        return await client.get("/api/v3/projects", params={"offset": page, "pageSize": page_size})

    @mcp.tool()
    async def get_project(project_id: str) -> dict:
        """Get details of a single project by its numeric ID or string identifier.

        Args:
            project_id: Numeric project ID or string identifier (e.g. 'my-project').
        """
        return await client.get(f"/api/v3/projects/{project_id}")

    @mcp.tool()
    async def create_project(
        name: str,
        identifier: str,
        description: str | None = None,
        parent_id: int | None = None,
        public: bool = False,
    ) -> dict:
        """Create a new project.

        Args:
            name: Display name of the project.
            identifier: URL-friendly unique identifier (lowercase, hyphens allowed).
            description: Optional project description.
            parent_id: Optional numeric ID of parent project for sub-projects.
            public: Whether the project is publicly visible.
        """
        body: dict = {
            "name": name,
            "identifier": identifier,
            "public": public,
        }
        if description:
            body["description"] = {"raw": description}
        if parent_id:
            body["_links"] = {"parent": {"href": f"/api/v3/projects/{parent_id}"}}
        return await client.post("/api/v3/projects", json=body)

    @mcp.tool()
    async def update_project(
        project_id: str,
        name: str | None = None,
        description: str | None = None,
        public: bool | None = None,
        status: str | None = None,
        status_explanation: str | None = None,
    ) -> dict:
        """Update an existing project's attributes.

        Args:
            project_id: Numeric project ID or string identifier.
            name: New display name.
            description: New description text.
            public: Set visibility (True = public, False = private).
            status: Project status code: 'on_track', 'at_risk', 'off_track', 'on_hold', 'finished', 'discontinued'.
            status_explanation: Explanation text for the status.
        """
        body: dict = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = {"raw": description}
        if public is not None:
            body["public"] = public
        if status is not None:
            body["statusExplanation"] = {"raw": status_explanation or ""}
            body["_links"] = {"status": {"href": f"/api/v3/project_statuses/{status}"}}
        return await client.patch(f"/api/v3/projects/{project_id}", json=body)

    @mcp.tool()
    async def delete_project(project_id: str, confirm: bool = False) -> str:
        """Delete a project permanently. This action is irreversible and removes all work packages inside.

        IMPORTANT: Always call this first WITHOUT confirm to show the user what will be deleted.
        Only pass confirm=True after the user has explicitly approved the deletion.

        Args:
            project_id: Numeric project ID or string identifier of the project to delete.
            confirm: Must be True to actually delete. Defaults to False (preview only).
        """
        project = await client.get(f"/api/v3/projects/{project_id}")
        name = project.get("name", project_id)
        identifier = project.get("identifier", "")

        if not confirm:
            return (
                f"[!] CONFIRMATION REQUIRED\n"
                f"\n"
                f"You are about to permanently delete:\n"
                f"  Project : {name}\n"
                f"  ID      : {project_id}\n"
                f"  URL key : {identifier}\n"
                f"\n"
                f"This will delete ALL work packages, versions, and data inside this project.\n"
                f"This action CANNOT be undone.\n"
                f"\n"
                f"Please ask the user: \"Are you sure you want to delete the project '{name}'?\"\n"
                f"If they confirm, call delete_project(project_id='{project_id}', confirm=True)."
            )

        await client.delete(f"/api/v3/projects/{project_id}")
        return f"Project '{name}' (ID: {project_id}) has been permanently deleted."
