import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GCAL_API_KEY = os.getenv("GCAL_API_KEY")
CALENDAR_ID  = os.getenv("CALENDAR_ID", "primary")
BASE_URL     = "https://www.googleapis.com/calendar/v3"

async def handle_list_gcal_events(args: dict) -> str:
    """Fetch real events from Google Calendar"""
    date = args["date"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/calendars/{CALENDAR_ID}/events",
            params={
                "key":          GCAL_API_KEY,
                "timeMin":      f"{date}T00:00:00Z",
                "timeMax":      f"{date}T23:59:59Z",
                "singleEvents": True,
                "orderBy":      "startTime"
            }
        )
        resp.raise_for_status()
        data  = resp.json()
        items = data.get("items", [])

        events = [
            {
                "title": e.get("summary", "Untitled"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end":   e["end"].get("dateTime",   e["end"].get("date"))
            }
            for e in items
        ]
        import json
        return json.dumps(events)

async def handle_create_gcal_event(args: dict) -> str:
    """Create a real event on Google Calendar"""
    from datetime import datetime, timedelta

    start    = args["start"]
    duration = args.get("duration_minutes", 60)
    end_dt   = datetime.fromisoformat(start) + timedelta(minutes=duration)

    event_body = {
        "summary": args["title"],
        "start":   {"dateTime": start,                "timeZone": "Africa/Lagos"},
        "end":     {"dateTime": end_dt.isoformat(),   "timeZone": "Africa/Lagos"}
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/calendars/{CALENDAR_ID}/events",
            params={"key": GCAL_API_KEY},
            json=event_body
        )
        resp.raise_for_status()
        created = resp.json()
        return f"Event '{created['summary']}' created. ID: {created['id']}"