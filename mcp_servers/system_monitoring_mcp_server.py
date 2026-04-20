#!/usr/bin/env python3
"""
System Monitoring MCP Server for IT Support
Provides system health checks and monitoring via MCP protocol.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Simulated system data for demo purposes
SYSTEMS = {
    "web-server-01": {
        "name": "web-server-01",
        "type": "Web Server",
        "location": "Data Center A",
        "ip": "10.0.1.10",
        "status": "healthy",
        "uptime_days": 45,
        "last_check": datetime.now().isoformat()
    },
    "db-server-01": {
        "name": "db-server-01",
        "type": "Database Server",
        "location": "Data Center A",
        "ip": "10.0.1.20",
        "status": "healthy",
        "uptime_days": 120,
        "last_check": datetime.now().isoformat()
    },
    "file-server-01": {
        "name": "file-server-01",
        "type": "File Server",
        "location": "Data Center B",
        "ip": "10.0.2.10",
        "status": "warning",
        "uptime_days": 15,
        "last_check": datetime.now().isoformat(),
        "warnings": ["Disk usage at 85%", "Memory usage at 78%"]
    },
    "vpn-gateway-01": {
        "name": "vpn-gateway-01",
        "type": "VPN Gateway",
        "location": "Data Center A",
        "ip": "10.0.1.5",
        "status": "healthy",
        "uptime_days": 60,
        "last_check": datetime.now().isoformat()
    },
    "email-server-01": {
        "name": "email-server-01",
        "type": "Email Server",
        "location": "Data Center B",
        "ip": "10.0.2.15",
        "status": "critical",
        "uptime_days": 0,
        "last_check": datetime.now().isoformat(),
        "errors": ["Service stopped responding", "High CPU usage 95%"]
    }
}

# Create MCP server instance
app = Server("system-monitoring")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available system monitoring tools."""
    return [
        Tool(
            name="check_system_health",
            description="Check the health status of a specific system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "Name of the system to check (e.g., web-server-01)"
                    }
                },
                "required": ["system_name"]
            }
        ),
        Tool(
            name="list_all_systems",
            description="List all monitored systems with their current status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["healthy", "warning", "critical", "unknown"]
                    },
                    "location": {
                        "type": "string",
                        "description": "Filter by location",
                        "enum": ["Data Center A", "Data Center B"]
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_system_metrics",
            description="Get detailed performance metrics for a system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "Name of the system"
                    },
                    "metric_type": {
                        "type": "string",
                        "description": "Type of metrics to retrieve",
                        "enum": ["cpu", "memory", "disk", "network", "all"]
                    }
                },
                "required": ["system_name"]
            }
        ),
        Tool(
            name="ping_system",
            description="Ping a system to check network connectivity",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "Name of the system to ping"
                    }
                },
                "required": ["system_name"]
            }
        ),
        Tool(
            name="get_system_logs",
            description="Retrieve recent system logs for troubleshooting",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "Name of the system"
                    },
                    "log_level": {
                        "type": "string",
                        "description": "Filter logs by level",
                        "enum": ["error", "warning", "info", "all"],
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of log entries to return",
                        "default": 10
                    }
                },
                "required": ["system_name"]
            }
        ),
        Tool(
            name="get_alerts",
            description="Get current active alerts across all systems",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity",
                        "enum": ["critical", "warning", "info"]
                    }
                },
                "required": []
            }
        )
    ]


def generate_metrics(system_name: str, metric_type: str = "all") -> dict:
    """Generate simulated metrics for a system."""
    system = SYSTEMS.get(system_name)

    if not system:
        return {"error": f"System {system_name} not found"}

    # Generate realistic-looking metrics based on system status
    if system["status"] == "healthy":
        cpu_usage = random.randint(20, 50)
        memory_usage = random.randint(40, 65)
        disk_usage = random.randint(30, 60)
    elif system["status"] == "warning":
        cpu_usage = random.randint(60, 80)
        memory_usage = random.randint(70, 85)
        disk_usage = random.randint(75, 90)
    else:  # critical
        cpu_usage = random.randint(85, 99)
        memory_usage = random.randint(90, 98)
        disk_usage = random.randint(90, 99)

    all_metrics = {
        "cpu": {
            "usage_percent": cpu_usage,
            "cores": 8,
            "load_average": round(cpu_usage / 12.5, 2)
        },
        "memory": {
            "usage_percent": memory_usage,
            "total_gb": 32,
            "used_gb": round(32 * memory_usage / 100, 1),
            "available_gb": round(32 * (100 - memory_usage) / 100, 1)
        },
        "disk": {
            "usage_percent": disk_usage,
            "total_gb": 500,
            "used_gb": round(500 * disk_usage / 100, 1),
            "available_gb": round(500 * (100 - disk_usage) / 100, 1)
        },
        "network": {
            "packets_sent": random.randint(10000, 100000),
            "packets_received": random.randint(10000, 100000),
            "bandwidth_usage_mbps": random.randint(10, 100),
            "errors": random.randint(0, 5)
        }
    }

    if metric_type == "all":
        return all_metrics
    elif metric_type in all_metrics:
        return {metric_type: all_metrics[metric_type]}
    else:
        return {"error": f"Unknown metric type: {metric_type}"}


def generate_logs(system_name: str, log_level: str = "all", limit: int = 10) -> list:
    """Generate simulated log entries."""
    system = SYSTEMS.get(system_name)

    if not system:
        return []

    # Generate sample logs based on system status
    sample_logs = []

    if system["status"] == "critical":
        sample_logs.extend([
            {"level": "error", "message": "Service stopped responding", "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()},
            {"level": "error", "message": "CPU usage exceeded 95%", "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat()},
            {"level": "warning", "message": "Memory usage high", "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()},
        ])
    elif system["status"] == "warning":
        sample_logs.extend([
            {"level": "warning", "message": "Disk usage at 85%", "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()},
            {"level": "warning", "message": "Memory usage elevated", "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()},
        ])

    # Always add some info logs
    sample_logs.extend([
        {"level": "info", "message": "Health check completed successfully", "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()},
        {"level": "info", "message": "Backup completed", "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()},
        {"level": "info", "message": "System maintenance scheduled", "timestamp": (datetime.now() - timedelta(days=1)).isoformat()},
    ])

    # Filter by log level
    if log_level != "all":
        sample_logs = [log for log in sample_logs if log["level"] == log_level]

    # Limit results
    return sample_logs[:limit]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for system monitoring operations."""

    if name == "check_system_health":
        system_name = arguments.get("system_name")
        system = SYSTEMS.get(system_name)

        if system:
            # Update last check time
            system["last_check"] = datetime.now().isoformat()

            return [TextContent(
                type="text",
                text=json.dumps(system, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"System {system_name} not found"})
            )]

    elif name == "list_all_systems":
        status_filter = arguments.get("status_filter")
        location = arguments.get("location")

        systems = list(SYSTEMS.values())

        # Apply filters
        if status_filter:
            systems = [s for s in systems if s["status"] == status_filter]

        if location:
            systems = [s for s in systems if s["location"] == location]

        # Return summary
        system_list = [
            {
                "name": s["name"],
                "type": s["type"],
                "location": s["location"],
                "status": s["status"],
                "uptime_days": s["uptime_days"]
            }
            for s in systems
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "count": len(system_list),
                "systems": system_list
            }, indent=2)
        )]

    elif name == "get_system_metrics":
        system_name = arguments.get("system_name")
        metric_type = arguments.get("metric_type", "all")

        metrics = generate_metrics(system_name, metric_type)

        return [TextContent(
            type="text",
            text=json.dumps({
                "system": system_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            }, indent=2)
        )]

    elif name == "ping_system":
        system_name = arguments.get("system_name")
        system = SYSTEMS.get(system_name)

        if not system:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"System {system_name} not found"})
            )]

        # Simulate ping
        if system["status"] == "critical":
            success = False
            response_time = None
        else:
            success = True
            response_time = random.randint(1, 50)  # ms

        return [TextContent(
            type="text",
            text=json.dumps({
                "system": system_name,
                "ip": system["ip"],
                "reachable": success,
                "response_time_ms": response_time,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        )]

    elif name == "get_system_logs":
        system_name = arguments.get("system_name")
        log_level = arguments.get("log_level", "all")
        limit = arguments.get("limit", 10)

        logs = generate_logs(system_name, log_level, limit)

        return [TextContent(
            type="text",
            text=json.dumps({
                "system": system_name,
                "log_level": log_level,
                "count": len(logs),
                "logs": logs
            }, indent=2)
        )]

    elif name == "get_alerts":
        severity = arguments.get("severity")

        alerts = []

        # Generate alerts from system status
        for system in SYSTEMS.values():
            if system["status"] == "critical":
                alerts.append({
                    "system": system["name"],
                    "severity": "critical",
                    "message": system.get("errors", ["Critical system failure"])[0],
                    "timestamp": system["last_check"]
                })
            elif system["status"] == "warning":
                alerts.append({
                    "system": system["name"],
                    "severity": "warning",
                    "message": system.get("warnings", ["System warning"])[0],
                    "timestamp": system["last_check"]
                })

        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        return [TextContent(
            type="text",
            text=json.dumps({
                "count": len(alerts),
                "alerts": alerts
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
