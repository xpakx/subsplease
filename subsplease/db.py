import sqlite3
import msgspec
from result import Result, Ok, Err


class LocalShow(msgspec.Struct):
    id: int
    sid: str   # subsplease link
    anilist_id: int | None
    title_romaji: str
    title_english: str | None
    title_japanese: str | None
    episode: int
    tracking: bool


class AnimeDB:
    def __init__(self, db_path: str = "ani.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS shows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sid TEXT UNIQUE NOT NULL,
                    anilist_id INTEGER,
                    title_romaji TEXT NOT NULL,
                    title_english TEXT,
                    last_episode INTEGER DEFAULT 0,
                    tracking BOOLEAN DEFAULT 0,
                    current BOOLEAN DEFAULT 0
                )
            """)

    def create_entry(self, sid: str, romaji: str) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("""
                    INSERT OR IGNORE INTO shows (sid, title_romaji, current)
                    VALUES (?, ?, 1)
                """, (sid, romaji))
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")
