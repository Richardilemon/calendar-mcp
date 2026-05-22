import asyncpg
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

async def get_db_connection():
    return await asyncpg.connect(DB_URL)

async def handle_query_events(args: dict) -> str:
    
    date  = args.get("date")
    limit = args.get("limit", 10)  # ← stays

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return "Invalid date format. Use YYYY-MM-DD."

    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            """
            SELECT title, start_time, end_time, description
            FROM events
            WHERE DATE(start_time) = $1
            ORDER BY start_time
            LIMIT $2
            """,
            date, limit
        )
        events = [dict(row) for row in rows]
        return json.dumps(events, default=str)
    finally:
        await conn.close()

async def handle_create_db_event(args: dict) -> str:
    """Insert a new event into the database"""
    conn = await get_db_connection()
    try:
        await conn.execute(
            """
            INSERT INTO events (title, start_time, duration_minutes)
            VALUES ($1, $2, $3)
            """,
            args["title"],
            args["start"],
            args.get("duration_minutes", 60)
        )
        return f"Event '{args['title']}' saved to database."
    finally:
        await conn.close()