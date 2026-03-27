from mcp.server.fastmcp import FastMCP

from openproject_mcp.client import OpenProjectClient
from openproject_mcp.tools import projects, work_packages, users, statuses, types, priorities, versions, time_entries


def register_all(mcp: FastMCP, client: OpenProjectClient) -> None:
    projects.register(mcp, client)
    work_packages.register(mcp, client)
    users.register(mcp, client)
    statuses.register(mcp, client)
    types.register(mcp, client)
    priorities.register(mcp, client)
    versions.register(mcp, client)
    time_entries.register(mcp, client)
