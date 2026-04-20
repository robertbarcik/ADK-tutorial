#!/usr/bin/env python3
"""
Knowledge Base MCP Server for IT Support
Provides documentation search and article retrieval via MCP protocol.
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# In-memory knowledge base for demo purposes
KNOWLEDGE_BASE = {
    "KB-001": {
        "id": "KB-001",
        "title": "How to Reset Windows Password",
        "category": "Security",
        "tags": ["password", "windows", "reset", "login"],
        "content": """
        **Steps to Reset Windows Password:**

        1. Press Ctrl+Alt+Delete on the login screen
        2. Click "Reset Password" link
        3. Answer your security questions
        4. Enter new password (must be 8+ characters)
        5. Confirm new password
        6. Click Submit

        **Requirements:**
        - Security questions must be set up beforehand
        - Password must meet complexity requirements

        **If forgotten security questions:**
        - Contact IT Support at ext. 5000
        - Bring photo ID for verification
        """,
        "views": 1250,
        "helpful_count": 89
    },
    "KB-002": {
        "id": "KB-002",
        "title": "WiFi Troubleshooting Guide",
        "category": "Network",
        "tags": ["wifi", "network", "connectivity", "internet"],
        "content": """
        **Common WiFi Issues and Solutions:**

        **Problem: Can't connect to WiFi**
        1. Check if WiFi is enabled on your device
        2. Verify you're selecting the correct network (Corp-WiFi)
        3. Ensure you're entering the correct password
        4. Restart your device

        **Problem: Connected but no internet**
        1. Disconnect and reconnect to WiFi
        2. Run Windows Network Troubleshooter
        3. Check if other devices have internet
        4. Contact IT if issue persists

        **Problem: Slow WiFi**
        1. Move closer to access point
        2. Check for interference (microwaves, other devices)
        3. Disconnect unused devices
        4. Use ethernet cable for bandwidth-intensive tasks

        **WiFi Network Names:**
        - Corp-WiFi: Main corporate network
        - Corp-Guest: For visitors (no company resources access)
        """,
        "views": 2100,
        "helpful_count": 156
    },
    "KB-003": {
        "id": "KB-003",
        "title": "VPN Setup and Connection Guide",
        "category": "Network",
        "tags": ["vpn", "remote", "connection", "security"],
        "content": """
        **Setting Up VPN for Remote Work:**

        **Initial Setup:**
        1. Download Cisco AnyConnect from company portal
        2. Install using admin credentials (contact IT if needed)
        3. Launch Cisco AnyConnect
        4. Enter VPN address: vpn.company.com
        5. Use your regular company username and password

        **Connecting to VPN:**
        1. Open Cisco AnyConnect
        2. Click Connect
        3. Enter credentials
        4. Accept 2FA prompt on your phone
        5. Wait for "Connected" status

        **Troubleshooting VPN Issues:**
        - "Connection Failed": Check internet connection first
        - "Authentication Failed": Verify username/password
        - "Certificate Error": Contact IT to update certificates
        - Can't access resources: Ensure VPN shows "Connected"

        **Important:** VPN required for accessing:
        - File shares
        - Internal websites
        - Company databases
        """,
        "views": 890,
        "helpful_count": 67
    },
    "KB-004": {
        "id": "KB-004",
        "title": "Printer Setup and Troubleshooting",
        "category": "Hardware",
        "tags": ["printer", "printing", "hardware", "driver"],
        "content": """
        **Adding Network Printer:**

        1. Open Settings > Devices > Printers & Scanners
        2. Click "Add a printer or scanner"
        3. Select your floor's printer from list
        4. Click Add Device

        **Common Printer Issues:**

        **Printer Not Found:**
        - Ensure you're connected to Corp-WiFi
        - Verify printer is powered on
        - Check printer display for error messages

        **Print Job Stuck:**
        - Open print queue (click printer icon in taskbar)
        - Right-click stuck job > Cancel
        - Restart Print Spooler service if needed

        **Print Quality Issues:**
        - Check toner/ink levels
        - Run printer cleaning cycle
        - Check paper type settings
        - Contact IT if streaking continues

        **Printer Names by Floor:**
        - Floor 1: CORP-PR-01
        - Floor 2: CORP-PR-02
        - Floor 3: CORP-PR-03
        """,
        "views": 1450,
        "helpful_count": 102
    },
    "KB-005": {
        "id": "KB-005",
        "title": "Microsoft Office Installation Guide",
        "category": "Software",
        "tags": ["office", "microsoft", "software", "installation"],
        "content": """
        **Installing Microsoft Office 365:**

        **For Company Computers:**
        1. Visit portal.office.com
        2. Sign in with company email
        3. Click "Install Office" > "Office 365 apps"
        4. Run downloaded installer
        5. Sign in when prompted
        6. Wait for installation (15-20 minutes)

        **Activation:**
        - Should activate automatically with company account
        - If not activated, open any Office app
        - Click "Sign In" and use company email

        **Available Applications:**
        - Word, Excel, PowerPoint (all employees)
        - Outlook (email client)
        - Teams (communication)
        - OneDrive (cloud storage - 1TB)
        - Access, Publisher (request if needed)

        **Troubleshooting:**
        - "Unlicensed Product": Sign out and sign back in
        - Installation Failed: Use Office uninstaller tool first
        - Activation Issues: Contact IT with employee ID

        **License Types:**
        - Standard: Word, Excel, PowerPoint, Outlook
        - Professional: Adds Access, Publisher
        - Enterprise: All apps + advanced features
        """,
        "views": 3200,
        "helpful_count": 245
    },
    "KB-006": {
        "id": "KB-006",
        "title": "Two-Factor Authentication (2FA) Setup",
        "category": "Security",
        "tags": ["2fa", "security", "authentication", "mfa"],
        "content": """
        **Enabling Two-Factor Authentication:**

        **Why 2FA?**
        - Protects your account even if password is compromised
        - Required for VPN and sensitive system access
        - Company policy for all employees

        **Setup Steps:**
        1. Visit security.company.com/2fa
        2. Sign in with your credentials
        3. Click "Enable 2FA"
        4. Download authenticator app:
           - Microsoft Authenticator (recommended)
           - Google Authenticator
           - Duo Mobile
        5. Scan QR code with app
        6. Enter 6-digit code to verify
        7. Save backup codes in safe place

        **Using 2FA:**
        - Enter password as normal
        - Open authenticator app
        - Enter current 6-digit code
        - Check "Trust this device" for 30 days (optional)

        **Lost Phone?**
        - Use backup codes (received during setup)
        - Contact IT with photo ID for emergency access
        - Re-enable 2FA with new device

        **Backup Codes:**
        - 10 single-use codes provided
        - Store securely (password manager or safe)
        - Request new codes if used up
        """,
        "views": 980,
        "helpful_count": 78
    }
}

# Create MCP server instance
app = Server("knowledge-base")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available knowledge base tools."""
    return [
        Tool(
            name="search_knowledge_base",
            description="Search documentation by keywords, returns relevant articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords or phrases)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                        "enum": ["Security", "Network", "Hardware", "Software"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_article",
            description="Retrieve a specific knowledge base article by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_id": {
                        "type": "string",
                        "description": "The article ID (e.g., KB-001)"
                    }
                },
                "required": ["article_id"]
            }
        ),
        Tool(
            name="list_articles",
            description="List all available articles with optional category filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                        "enum": ["Security", "Network", "Hardware", "Software"]
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_popular_articles",
            description="Get most viewed or most helpful articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "description": "Sort by views or helpful count",
                        "enum": ["views", "helpful"],
                        "default": "views"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of articles to return",
                        "default": 5
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for knowledge base operations."""

    if name == "search_knowledge_base":
        query = arguments.get("query", "").lower()
        category = arguments.get("category")
        limit = arguments.get("limit", 5)

        results = []
        for article in KNOWLEDGE_BASE.values():
            # Check if query matches title, content, or tags
            matches = (
                query in article["title"].lower() or
                query in article["content"].lower() or
                any(query in tag for tag in article["tags"])
            )

            # Apply category filter if specified
            if category and article["category"] != category:
                matches = False

            if matches:
                # Include relevance score
                score = 0
                if query in article["title"].lower():
                    score += 10
                score += sum(2 for tag in article["tags"] if query in tag)
                score += article["content"].lower().count(query)

                results.append({
                    "article": article,
                    "relevance_score": score
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Limit results
        results = results[:limit]

        return [TextContent(
            type="text",
            text=json.dumps({
                "query": arguments.get("query"),
                "count": len(results),
                "results": [
                    {
                        "id": r["article"]["id"],
                        "title": r["article"]["title"],
                        "category": r["article"]["category"],
                        "relevance": r["relevance_score"],
                        "snippet": r["article"]["content"][:200] + "..."
                    }
                    for r in results
                ]
            }, indent=2)
        )]

    elif name == "get_article":
        article_id = arguments.get("article_id")
        article = KNOWLEDGE_BASE.get(article_id)

        if article:
            # Increment view count (simulated)
            article["views"] += 1

            return [TextContent(
                type="text",
                text=json.dumps(article, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Article {article_id} not found"})
            )]

    elif name == "list_articles":
        category = arguments.get("category")

        articles = list(KNOWLEDGE_BASE.values())

        if category:
            articles = [a for a in articles if a["category"] == category]

        # Return summary info only
        article_list = [
            {
                "id": a["id"],
                "title": a["title"],
                "category": a["category"],
                "tags": a["tags"],
                "views": a["views"]
            }
            for a in articles
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "count": len(article_list),
                "articles": article_list
            }, indent=2)
        )]

    elif name == "get_popular_articles":
        sort_by = arguments.get("sort_by", "views")
        limit = arguments.get("limit", 5)

        # Sort articles
        articles = list(KNOWLEDGE_BASE.values())

        if sort_by == "helpful":
            articles.sort(key=lambda x: x["helpful_count"], reverse=True)
        else:  # views
            articles.sort(key=lambda x: x["views"], reverse=True)

        # Limit results
        articles = articles[:limit]

        # Return summary
        popular = [
            {
                "id": a["id"],
                "title": a["title"],
                "category": a["category"],
                "views": a["views"],
                "helpful_count": a["helpful_count"]
            }
            for a in articles
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "sort_by": sort_by,
                "count": len(popular),
                "articles": popular
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
