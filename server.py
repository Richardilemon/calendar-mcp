from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict
import time
import mcp.types as types
import uvicorn
import os, json

from tools.database import handle_query_events, handle_create_db_event
from tools.gcal import handle_list_gcal_events, handle_create_gcal_event
from tools.filesystem import handle_read_file, handle_write_file, handle_list_files
from tools.scraper import handle_scrape_page

app = Server("calendar-assistant")
sse = SseServerTransport("/messages/")  # only once
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")

request_counts = defaultdict(list)
RATE_LIMIT     = 100  # requests
RATE_WINDOW    = 60   # seconds
tool_stats = defaultdict(lambda: {"calls": 0, "total_ms": 0, "errors": 0})

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # create_event
        # query_events
        # create_db_event
        # list_gcal_events   ← add this
        # create_gcal_event  ← add this
        # read_file          ← add this
        # write_file         ← add this
        # list_files         ← add this
        # scrape_page        ← add this
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    handlers = {
        "create_event":      handle_create_event,
        "query_events":      handle_query_events,
        "create_db_event":   handle_create_db_event,
        "list_gcal_events":  handle_list_gcal_events,
        "create_gcal_event": handle_create_gcal_event,
        "read_file":         handle_read_file,
        "write_file":        handle_write_file,
        "list_files":        handle_list_files,
        "scrape_page":       handle_scrape_page,
    }

    handler = handlers.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")

    start = time.time()
    try:
        result = await handler(arguments)
        tool_stats[name]["calls"]    += 1
        tool_stats[name]["total_ms"] += (time.time() - start) * 1000
        return result if isinstance(result, list) else [types.TextContent(type="text", text=result)]
    except Exception as e:
        tool_stats[name]["errors"] += 1
        raise

async def handle_create_event(args: dict) -> list[types.TextContent]:
    title    = args["title"]
    start    = args["start"]
    duration = args.get("duration_minutes", 60)
    return [types.TextContent(
        type="text",
        text=f"Event '{title}' scheduled at {start} for {duration} minutes."
    )]

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="calendar://today",
            name="Today's schedule",
            description="All events scheduled for today. Read this before scheduling anything to avoid conflicts.",
            mimeType="application/json"
        ),
        types.Resource(
            uri="system://tool-stats",
            name="Tool call statistics",
            description="Metrics for all tool calls — useful for debugging and optimization.",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    normalized = str(uri).rstrip("/")
    if normalized == "calendar://today":
        return """[
            {"title": "Team standup", "start": "09:00", "end": "09:30"},
            {"title": "Client call",  "start": "14:00", "end": "15:00"}
        ]"""
    
    if normalized == "system://tool-stats":
        return json.dumps(tool_stats)
    
    raise ValueError(f"Unknown resource: {uri}")


def is_rate_limited(client_ip: str) -> bool:
    now     = time.time()
    window  = request_counts[client_ip]
    # remove old requests outside the window
    request_counts[client_ip] = [t for t in window if now - t < RATE_WINDOW]
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return True
    request_counts[client_ip].append(now)
    return False

async def handle_sse(request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        return Response("Rate limit exceeded", status_code=429)
    # verify token on every connection
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {MCP_AUTH_TOKEN}":
        return Response("Unauthorized", status_code=401)

    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(
            streams[0], streams[1],
            app.create_initialization_options()
        )

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)