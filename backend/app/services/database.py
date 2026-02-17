import json
import uuid
from datetime import datetime, timezone

import aiosqlite

DB_PATH = "./chat.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
        await db.commit()


def _now():
    return datetime.now(timezone.utc).isoformat()


async def create_thread(title="New Chat"):
    thread_id = str(uuid.uuid4())
    now = _now()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO threads (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (thread_id, title, now, now),
        )
        await db.commit()
    return {"id": thread_id, "title": title, "created_at": now, "updated_at": now}


async def get_all_threads():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, title, created_at, updated_at FROM threads ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_thread(thread_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, title, created_at, updated_at FROM threads WHERE id = ?",
            (thread_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_thread_messages(thread_id, limit=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT id, thread_id, role, content, sources, created_at FROM messages WHERE thread_id = ? ORDER BY created_at ASC"
        params = [thread_id]
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            msg = dict(row)
            msg["sources"] = json.loads(msg["sources"]) if msg["sources"] else []
            results.append(msg)
        return results


async def get_recent_history(thread_id, limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY created_at DESC LIMIT ?",
            (thread_id, limit),
        )
        rows = await cursor.fetchall()
        return [
            {"role": row["role"], "content": row["content"]} for row in reversed(rows)
        ]


async def add_message(thread_id, role, content, sources=None):
    msg_id = str(uuid.uuid4())
    now = _now()
    sources_json = json.dumps(sources) if sources else None
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (id, thread_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (msg_id, thread_id, role, content, sources_json, now),
        )
        await db.execute(
            "UPDATE threads SET updated_at = ? WHERE id = ?",
            (now, thread_id),
        )
        await db.commit()
    return msg_id


async def update_thread_title(thread_id, title):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE threads SET title = ?, updated_at = ? WHERE id = ?",
            (title, _now(), thread_id),
        )
        await db.commit()


async def delete_thread(thread_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
        await db.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        await db.commit()
