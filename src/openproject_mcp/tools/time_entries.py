from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient


def register(mcp: FastMCP, client: OpenProjectClient) -> None:

    @mcp.tool()
    async def list_time_entries(
        work_package_id: int | None = None,
        project_id: str | None = None,
        user_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        """List time entries, optionally filtered by work package, project, user, or date range.

        Args:
            work_package_id: Filter by work package ID.
            project_id: Filter by project ID or identifier.
            user_id: Filter by user ID.
            from_date: Filter entries on or after this date (YYYY-MM-DD).
            to_date: Filter entries on or before this date (YYYY-MM-DD).
            page: Page number (starts at 1).
            page_size: Results per page (max 200).
        """
        import json

        filters = []
        if work_package_id is not None:
            filters.append({"work_package": {"operator": "=", "values": [str(work_package_id)]}})
        if project_id is not None:
            filters.append({"project": {"operator": "=", "values": [str(project_id)]}})
        if user_id is not None:
            filters.append({"user": {"operator": "=", "values": [str(user_id)]}})
        if from_date is not None:
            filters.append({"spent_on": {"operator": ">=", "values": [from_date]}})
        if to_date is not None:
            filters.append({"spent_on": {"operator": "<=", "values": [to_date]}})

        params: dict = {"offset": page, "pageSize": page_size}
        if filters:
            params["filters"] = json.dumps(filters)

        return await client.get("/api/v3/time_entries", params=params)

    @mcp.tool()
    async def get_time_entry(time_entry_id: int) -> dict:
        """Get full details of a single time entry.

        Args:
            time_entry_id: Numeric ID of the time entry.
        """
        return await client.get(f"/api/v3/time_entries/{time_entry_id}")

    @mcp.tool()
    async def create_time_entry(
        work_package_id: int,
        hours: float,
        spent_on: str,
        activity_id: int | None = None,
        comment: str | None = None,
        user_id: int | None = None,
    ) -> dict:
        """Log a time entry against a work package.

        Args:
            work_package_id: ID of the work package to log time against.
            hours: Number of hours spent (e.g. 1.5 for 1h 30m).
            spent_on: Date the time was spent (YYYY-MM-DD).
            activity_id: ID of the time entry activity (e.g. Development, Testing). Use list_time_entry_activities to find IDs.
            comment: Optional comment describing the work done.
            user_id: User to log time for. Defaults to the authenticated user.
        """
        body: dict = {
            "hours": f"PT{hours}H",
            "spentOn": spent_on,
        }
        links: dict = {
            "workPackage": {"href": f"/api/v3/work_packages/{work_package_id}"},
        }

        if comment:
            body["comment"] = {"raw": comment}
        if activity_id is not None:
            links["activity"] = {"href": f"/api/v3/time_entries/activities/{activity_id}"}
        if user_id is not None:
            links["user"] = {"href": f"/api/v3/users/{user_id}"}

        body["_links"] = links
        return await client.post("/api/v3/time_entries", json=body)

    @mcp.tool()
    async def update_time_entry(
        time_entry_id: int,
        hours: float | None = None,
        spent_on: str | None = None,
        activity_id: int | None = None,
        comment: str | None = None,
    ) -> dict:
        """Update an existing time entry.

        Args:
            time_entry_id: Numeric ID of the time entry to update.
            hours: New number of hours spent.
            spent_on: New date the time was spent (YYYY-MM-DD).
            activity_id: New activity ID.
            comment: New comment (plain text).
        """
        body: dict = {}
        links: dict = {}

        if hours is not None:
            body["hours"] = f"PT{hours}H"
        if spent_on is not None:
            body["spentOn"] = spent_on
        if comment is not None:
            body["comment"] = {"raw": comment}
        if activity_id is not None:
            links["activity"] = {"href": f"/api/v3/time_entries/activities/{activity_id}"}

        if links:
            body["_links"] = links

        return await client.patch(f"/api/v3/time_entries/{time_entry_id}", json=body)

    @mcp.tool()
    async def delete_time_entry(time_entry_id: int, confirm: bool = False) -> str:
        """Delete a time entry permanently. This action is irreversible.

        IMPORTANT: Always call this first WITHOUT confirm to show the user what will be deleted.
        Only pass confirm=True after the user has explicitly approved the deletion.

        Args:
            time_entry_id: Numeric ID of the time entry to delete.
            confirm: Must be True to actually delete. Defaults to False (preview only).
        """
        entry = await client.get(f"/api/v3/time_entries/{time_entry_id}")
        hours = entry.get("hours", "unknown")
        spent_on = entry.get("spentOn", "unknown")
        comment_raw = entry.get("comment", {}).get("raw", "")
        wp = entry.get("_links", {}).get("workPackage", {}).get("title", "unknown")
        user = entry.get("_links", {}).get("user", {}).get("title", "unknown")

        if not confirm:
            return (
                f"[!] CONFIRMATION REQUIRED\n"
                f"\n"
                f"You are about to permanently delete:\n"
                f"  Time Entry #{time_entry_id}\n"
                f"  Hours      : {hours}\n"
                f"  Date       : {spent_on}\n"
                f"  Work Pkg   : {wp}\n"
                f"  User       : {user}\n"
                f"  Comment    : {comment_raw or '(none)'}\n"
                f"\n"
                f"This action CANNOT be undone.\n"
                f"\n"
                f"Please ask the user: \"Are you sure you want to delete time entry #{time_entry_id}?\"\n"
                f"If they confirm, call delete_time_entry(time_entry_id={time_entry_id}, confirm=True)."
            )

        await client.delete(f"/api/v3/time_entries/{time_entry_id}")
        return f"Time entry #{time_entry_id} ({hours} on {spent_on} for '{wp}') has been permanently deleted."

    @mcp.tool()
    async def list_time_entry_activities() -> dict:
        """List all available time entry activities (e.g. Development, Testing, Design).

        Use the activity IDs returned here when creating or updating time entries.
        """
        return await client.get("/api/v3/time_entries/activities")
