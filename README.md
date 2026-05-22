# calendar-mcp

A hands-on learning project built while studying the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — an open standard by Anthropic that defines a universal interface between AI models and external tools.

This repo is the outcome of going through MCP from zero to hero: understanding the protocol, building a server with the Python SDK, testing it with MCP Inspector, and connecting it to Claude Desktop.

> **Note:** This is a learning project, not a production tool. The production-grade version is being built separately — see [Calendar PA](https://github.com/Richardilemon/Calendar-PA).

---

## What's in here

```
calendar-mcp/
├── tools/
│   ├── database.py     # PostgreSQL query tools via asyncpg
│   ├── filesystem.py   # Safe file read/write tools
│   ├── gcal.py         # Google Calendar REST API wrapper
│   └── scraper.py      # Playwright-based web scraping tool
├── server.py           # MCP server — tools, resources, routing
├── requirements.txt    # Dependencies
└── .env.example        # Environment variable template
```

---

## What it covers

- **MCP protocol fundamentals** — JSON-RPC 2.0, the initialize → discover → operate lifecycle, stdio transport
- **Tools** — defining, registering, and routing tool calls with the Python MCP SDK
- **Resources** — exposing data via URIs (`calendar://today`, `system://tool-stats`)
- **Real-world tool patterns** — database queries, REST API wrappers, filesystem access, browser automation
- **Observability** — structured logging and in-memory tool call metrics
- **Claude Desktop integration** — connecting a local MCP server via `claude_desktop_config.json`

---

## Tools exposed

| Tool | Description |
|---|---|
| `create_event` | Create a calendar event (stub — no real API call) |
| `query_events` | Query events from a PostgreSQL database by date |
| `create_db_event` | Insert an event into the database |
| `list_gcal_events` | Fetch events from Google Calendar API |
| `create_gcal_event` | Create a real event on Google Calendar |
| `read_file` | Read a file from an allowed directory |
| `write_file` | Write content to a file |
| `list_files` | List files in the data directory |
| `scrape_page` | Scrape text content from a URL using Playwright |

---

## Resources exposed

| Resource | URI | Description |
|---|---|---|
| Today's schedule | `calendar://today` | Stub schedule data for today |
| Tool statistics | `system://tool-stats` | Live tool call metrics |

---

## Running locally

**Requirements:** Python 3.12+, Node.js (for MCP Inspector)

```bash
# clone the repo
git clone https://github.com/yourusername/calendar-mcp.git
cd calendar-mcp

# create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt
playwright install chromium

# copy environment template
cp .env.example .env
# fill in your credentials in .env

# run the server
python server.py
```

**Test with MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector python server.py
```

**Connect to Claude Desktop** — add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "calendar-mcp": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/calendar-mcp/server.py"]
    }
  }
}
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in your values:

```
DATABASE_URL=postgresql://user:password@localhost:5432/your_db
GCAL_API_KEY=your_google_calendar_api_key
CALENDAR_ID=primary
DATA_DIR=./data
```

---

## What's next

This repo was the learning ground. The production version is **Calendar PA** — a fully OAuth'd, publicly deployable Google Calendar MCP server with:

- Natural language scheduling with conflict detection
- Smart free slot finder
- Complex recurring events
- Reminders
- Telegram bot interface
- Listed on the MCP registry

Follow along: [https://github.com/Richardilemon]

---

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Anthropic](https://anthropic.com)