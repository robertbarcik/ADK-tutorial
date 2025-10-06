#!/usr/bin/env python3
"""
Ticket Database MCP Server for IT Support
Provides CRUD operations for support tickets via MCP protocol.
"""

import asyncio
import json
from datetime import datetime
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# In-memory ticket database for demo purposes
TICKETS = {
    "T-1001": {
        "id": "T-1001",
        "title": "Laptop won't boot",
        "description": "My laptop shows a black screen when I press the power button",
        "status": "open",
        "priority": "high",
        "assigned_to": "hardware_team",
        "created_at": "2025-10-05T10:30:00",
        "updated_at": "2025-10-05T10:30:00"
    },
    "T-1002": {
        "id": "T-1002",
        "title": "Password reset request",
        "description": "I forgot my password and need access to my account",
        "status": "resolved",
        "priority": "medium",
        "assigned_to": "security_team",
        "created_at": "2025-10-04T14:20:00",
        "updated_at": "2025-10-04T15:45:00"
    },
    "T-1003": {
        "id": "T-1003",
        "title": "WiFi connectivity issues",
        "description": "WiFi keeps disconnecting every 10 minutes in Conference Room B",
        "status": "in_progress",
        "priority": "high",
        "assigned_to": "network_team",
        "created_at": "2025-10-05T09:15:00",
        "updated_at": "2025-10-05T11:30:00"
    },
    "T-1004": {
        "id": "T-1004",
        "title": "Software installation request",
        "description": "Need Adobe Photoshop installed for design work",
        "status": "open",
        "priority": "low",
        "assigned_to": "software_team",
        "created_at": "2025-10-06T08:00:00",
        "updated_at": "2025-10-06T08:00:00"
    }
}

# Counter for generating new ticket IDs
TICKET_COUNTER = 1005

# Create MCP server instance
app = Server("ticket-database")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ticket database tools."""
    return [
        Tool(
            name="get_ticket",
            description="Retrieve a specific ticket by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID (e.g., T-1001)"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="list_tickets",
            description="List all tickets with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: open, in_progress, resolved, closed",
                        "enum": ["open", "in_progress", "resolved", "closed"]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Filter by priority: low, medium, high, critical",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Filter by team assignment"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="create_ticket",
            description="Create a new support ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title of the ticket"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Team to assign the ticket to"
                    }
                },
                "required": ["title", "description", "priority"]
            }
        ),
        Tool(
            name="update_ticket",
            description="Update an existing ticket's status or details",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to update"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status",
                        "enum": ["open", "in_progress", "resolved", "closed"]
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Reassign to a different team"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes or updates"
                    }
                },
                "required": ["ticket_id"]
            }
        ),
        Tool(
            name="search_tickets",
            description="Search tickets by keywords in title or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords)"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for ticket operations."""

    if name == "get_ticket":
        ticket_id = arguments.get("ticket_id")
        ticket = TICKETS.get(ticket_id)

        if ticket:
            return [TextContent(
                type="text",
                text=json.dumps(ticket, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Ticket {ticket_id} not found"})
            )]

    elif name == "list_tickets":
        # Filter tickets based on criteria
        filtered = list(TICKETS.values())

        if "status" in arguments and arguments["status"]:
            filtered = [t for t in filtered if t["status"] == arguments["status"]]

        if "priority" in arguments and arguments["priority"]:
            filtered = [t for t in filtered if t["priority"] == arguments["priority"]]

        if "assigned_to" in arguments and arguments["assigned_to"]:
            filtered = [t for t in filtered if t["assigned_to"] == arguments["assigned_to"]]

        return [TextContent(
            type="text",
            text=json.dumps({
                "count": len(filtered),
                "tickets": filtered
            }, indent=2)
        )]

    elif name == "create_ticket":
        global TICKET_COUNTER

        ticket_id = f"T-{TICKET_COUNTER}"
        TICKET_COUNTER += 1

        now = datetime.now().isoformat()

        new_ticket = {
            "id": ticket_id,
            "title": arguments["title"],
            "description": arguments["description"],
            "status": "open",
            "priority": arguments["priority"],
            "assigned_to": arguments.get("assigned_to", "unassigned"),
            "created_at": now,
            "updated_at": now
        }

        TICKETS[ticket_id] = new_ticket

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "ticket": new_ticket
            }, indent=2)
        )]

    elif name == "update_ticket":
        ticket_id = arguments.get("ticket_id")
        ticket = TICKETS.get(ticket_id)

        if not ticket:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Ticket {ticket_id} not found"})
            )]

        # Update fields
        if "status" in arguments:
            ticket["status"] = arguments["status"]

        if "assigned_to" in arguments:
            ticket["assigned_to"] = arguments["assigned_to"]

        if "notes" in arguments:
            if "notes" not in ticket:
                ticket["notes"] = []
            ticket["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "content": arguments["notes"]
            })

        ticket["updated_at"] = datetime.now().isoformat()

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "ticket": ticket
            }, indent=2)
        )]

    elif name == "search_tickets":
        query = arguments.get("query", "").lower()

        results = []
        for ticket in TICKETS.values():
            if (query in ticket["title"].lower() or
                query in ticket["description"].lower()):
                results.append(ticket)

        return [TextContent(
            type="text",
            text=json.dumps({
                "query": arguments.get("query"),
                "count": len(results),
                "tickets": results
            }, indent=2)
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
