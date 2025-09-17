import os
import sqlite3
import asyncio
from typing import List, Dict, Set
from datetime import datetime

DB_PATH = os.path.join("data", "app.db")

_connection = None

# Fallback for Python < 3.9 where asyncio.to_thread is unavailable
try:
    _to_thread = asyncio.to_thread  # type: ignore[attr-defined]
except AttributeError:
    async def _to_thread(func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def _get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        os.makedirs("data", exist_ok=True)
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.execute("PRAGMA journal_mode=WAL;")
        _connection.execute("PRAGMA synchronous=NORMAL;")
    return _connection


def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table});")
    return any(row[1] == column for row in cur.fetchall())


def init_db() -> None:
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            link TEXT PRIMARY KEY,
            joined_at TEXT,
            account_phone TEXT
        );
        """
    )

    # Migration: ensure account_phone column exists
    if not _column_exists(cur, "groups", "account_phone"):
        cur.execute("ALTER TABLE groups ADD COLUMN account_phone TEXT;")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER,
            group_link TEXT,
            date TEXT,
            sender_id INTEGER,
            text TEXT,
            PRIMARY KEY (id, group_link),
            FOREIGN KEY (group_link) REFERENCES groups(link)
        );
        """
    )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_link);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_groups_joined_at ON groups(substr(joined_at,1,10));")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_groups_phone ON groups(account_phone);")

    conn.commit()


def _record_group_join_sync(link: str, joined_at: str, account_phone: str) -> None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO groups (link, joined_at, account_phone)
        VALUES (?, ?, ?)
        ON CONFLICT(link) DO UPDATE SET joined_at=excluded.joined_at, account_phone=excluded.account_phone;
        """,
        (link, joined_at, account_phone),
    )
    conn.commit()


async def record_group_join(link: str, joined_at: str, account_phone: str) -> None:
    await _to_thread(_record_group_join_sync, link, joined_at, account_phone)


def _record_messages_sync(group_link: str, messages: List[Dict]) -> None:
    if not messages:
        return
    conn = _get_connection()
    cur = conn.cursor()
    rows = [
        (
            int(m.get("id")),
            group_link,
            str(m.get("date")),
            None if m.get("sender_id") is None else int(m.get("sender_id")),
            (m.get("text") or ""),
        )
        for m in messages
    ]
    cur.executemany(
        """
        INSERT OR IGNORE INTO messages (id, group_link, date, sender_id, text)
        VALUES (?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()


async def record_messages(group_link: str, messages: List[Dict]) -> None:
    await _to_thread(_record_messages_sync, group_link, messages)


def _today_total_joins_sync(date_str: str) -> int:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM groups WHERE substr(joined_at,1,10)=?;",
        (date_str,),
    )
    return int(cur.fetchone()[0])


def _today_joins_for_phone_sync(date_str: str, phone: str) -> int:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM groups WHERE substr(joined_at,1,10)=? AND account_phone=?;",
        (date_str, phone),
    )
    return int(cur.fetchone()[0])


async def today_total_joins(date_str: str) -> int:
    return await _to_thread(_today_total_joins_sync, date_str)


async def today_joins_for_phone(date_str: str, phone: str) -> int:
    return await _to_thread(_today_joins_for_phone_sync, date_str, phone)


def _all_joined_links_sync() -> Set[str]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT link FROM groups;")
    return {row[0] for row in cur.fetchall()}


async def all_joined_links() -> Set[str]:
    return await _to_thread(_all_joined_links_sync) 