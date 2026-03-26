from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_work_packages(
        project_id: str | None = None,
        status_id: int | None = None,
        assignee_id: int | None = None,
        type_id: int | None = None,
        priority_id: int | None = None,
        subject: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        """List work packages, optionally scoped to a project and filtered by attributes.

        Args:
            project_id: Numeric ID or identifier of the project. If omitted, lists across all projects.
            status_id: Filter by status ID.
            assignee_id: Filter by assignee user ID.
            type_id: Filter by work package type ID.
            priority_id: Filter by priority ID.
            subject: Filter by subject text (substring match).
            page: Page number (starts at 1).
            page_size: Results per page (max 200).
        """
        import json

        filters = []
        if status_id is not None:
            filters.append({"status": {"operator": "=", "values": [str(status_id)]}})
        if assignee_id is not None:
            filters.append({"assignee": {"operator": "=", "values": [str(assignee_id)]}})
        if type_id is not None:
            filters.append({"type": {"operator": "=", "values": [str(type_id)]}})
        if priority_id is not None:
            filters.append({"priority": {"operator": "=", "values": [str(priority_id)]}})
        if subject is not None:
            filters.append({"subject": {"operator": "~", "values": [subject]}})

        params: dict = {"offset": page, "pageSize": page_size}
        if filters:
            params["filters"] = json.dumps(filters)

        if project_id:
            path = f"/api/v3/projects/{project_id}/work_packages"
        else:
            path = "/api/v3/work_packages"

        return await client.get(path, params=params)

    @mcp.tool()
    async def get_work_package(work_package_id: int) -> dict:
        """Get full details of a single work package.

        Args:
            work_package_id: Numeric ID of the work package.
        """
        return await client.get(f"/api/v3/work_packages/{work_package_id}")

    @mcp.tool()
    async def create_work_package(
        project_id: str,
        subject: str,
        type_id: int | None = None,
        status_id: int | None = None,
        priority_id: int | None = None,
        assignee_id: int | None = None,
        description: str | None = None,
        version_id: int | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        estimated_hours: float | None = None,
    ) -> dict:
        """Create a new work package in a project.

        Args:
            project_id: Numeric ID or identifier of the project.
            subject: Title / short description of the work package.
            type_id: ID of the work package type (Task, Bug, Feature, etc.).
            status_id: ID of the initial status.
            priority_id: ID of the priority.
            assignee_id: User ID to assign to.
            description: Detailed description (plain text).
            version_id: ID of the version/milestone to assign to.
            start_date: Start date in YYYY-MM-DD format.
            due_date: Due date in YYYY-MM-DD format.
            estimated_hours: Estimated effort in hours.
        """
        body: dict = {"subject": subject}
        links: dict = {}

        if description:
            body["description"] = {"raw": description}
        if start_date:
            body["startDate"] = start_date
        if due_date:
            body["dueDate"] = due_date
        if estimated_hours is not None:
            body["estimatedTime"] = f"PT{estimated_hours}H"

        links["project"] = {"href": f"/api/v3/projects/{project_id}"}
        if type_id:
            links["type"] = {"href": f"/api/v3/types/{type_id}"}
        if status_id:
            links["status"] = {"href": f"/api/v3/statuses/{status_id}"}
        if priority_id:
            links["priority"] = {"href": f"/api/v3/priorities/{priority_id}"}
        if assignee_id:
            links["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}
        if version_id:
            links["version"] = {"href": f"/api/v3/versions/{version_id}"}

        if links:
            body["_links"] = links

        return await client.post(f"/api/v3/projects/{project_id}/work_packages", json=body)

    @mcp.tool()
    async def update_work_package(
        work_package_id: int,
        lock_version: int,
        subject: str | None = None,
        description: str | None = None,
        status_id: int | None = None,
        type_id: int | None = None,
        priority_id: int | None = None,
        assignee_id: int | None = None,
        version_id: int | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
        estimated_hours: float | None = None,
        percentage_done: int | None = None,
    ) -> dict:
        """Update attributes of an existing work package.

        OpenProject uses optimistic locking — you must supply the current lockVersion
        (obtained from get_work_package). The update will fail if another user has
        modified the work package since you last fetched it.

        Args:
            work_package_id: Numeric ID of the work package to update.
            lock_version: Current lockVersion from the work package (prevents conflicts).
            subject: New title.
            description: New description (plain text).
            status_id: New status ID.
            type_id: New type ID.
            priority_id: New priority ID.
            assignee_id: New assignee user ID. Set to 0 to unassign.
            version_id: New version/milestone ID.
            start_date: New start date (YYYY-MM-DD).
            due_date: New due date (YYYY-MM-DD).
            estimated_hours: New estimated effort in hours.
            percentage_done: Completion percentage (0–100).
        """
        body: dict = {"lockVersion": lock_version}
        links: dict = {}

        if subject is not None:
            body["subject"] = subject
        if description is not None:
            body["description"] = {"raw": description}
        if start_date is not None:
            body["startDate"] = start_date
        if due_date is not None:
            body["dueDate"] = due_date
        if estimated_hours is not None:
            body["estimatedTime"] = f"PT{estimated_hours}H"
        if percentage_done is not None:
            body["percentageDone"] = percentage_done

        if status_id is not None:
            links["status"] = {"href": f"/api/v3/statuses/{status_id}"}
        if type_id is not None:
            links["type"] = {"href": f"/api/v3/types/{type_id}"}
        if priority_id is not None:
            links["priority"] = {"href": f"/api/v3/priorities/{priority_id}"}
        if assignee_id is not None:
            links["assignee"] = (
                {"href": f"/api/v3/users/{assignee_id}"} if assignee_id else {"href": None}
            )
        if version_id is not None:
            links["version"] = {"href": f"/api/v3/versions/{version_id}"}

        if links:
            body["_links"] = links

        return await client.patch(f"/api/v3/work_packages/{work_package_id}", json=body)

    @mcp.tool()
    async def delete_work_package(work_package_id: int) -> str:
        """Delete a work package permanently.

        Args:
            work_package_id: Numeric ID of the work package to delete.
        """
        await client.delete(f"/api/v3/work_packages/{work_package_id}")
        return f"Work package #{work_package_id} deleted successfully."

    @mcp.tool()
    async def list_work_package_activities(work_package_id: int) -> dict:
        """List all activities (comments and change history) for a work package.

        Args:
            work_package_id: Numeric ID of the work package.
        """
        return await client.get(f"/api/v3/work_packages/{work_package_id}/activities")

    @mcp.tool()
    async def add_work_package_comment(work_package_id: int, comment: str) -> dict:
        """Add a comment to a work package.

        Args:
            work_package_id: Numeric ID of the work package.
            comment: Comment text to add (plain text).
        """
        body = {"comment": {"raw": comment}}
        return await client.post(
            f"/api/v3/work_packages/{work_package_id}/activities", json=body
        )

    @mcp.tool()
    async def list_work_package_relations(work_package_id: int) -> dict:
        """List all relations (blocks, follows, relates to, etc.) for a work package.

        Args:
            work_package_id: Numeric ID of the work package.
        """
        import json

        filters = json.dumps([{"involved": {"operator": "=", "values": [str(work_package_id)]}}])
        return await client.get("/api/v3/relations", params={"filters": filters})

    @mcp.tool()
    async def create_work_package_relation(
        from_work_package_id: int,
        to_work_package_id: int,
        relation_type: str = "relates",
        description: str | None = None,
    ) -> dict:
        """Create a relation between two work packages.

        Args:
            from_work_package_id: ID of the source work package.
            to_work_package_id: ID of the target work package.
            relation_type: Type of relation: 'relates', 'duplicates', 'duplicated', 'blocks',
                           'blocked', 'precedes', 'follows', 'includes', 'partof', 'requires', 'required'.
            description: Optional description of the relation.
        """
        body: dict = {
            "type": relation_type,
            "_links": {
                "from": {"href": f"/api/v3/work_packages/{from_work_package_id}"},
                "to": {"href": f"/api/v3/work_packages/{to_work_package_id}"},
            },
        }
        if description:
            body["description"] = description
        return await client.post(
            f"/api/v3/work_packages/{from_work_package_id}/relations", json=body
        )
