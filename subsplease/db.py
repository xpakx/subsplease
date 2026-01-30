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
    current: bool


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
                    title_japanese TEXT,
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

    def get_airing_shows(self) -> Result[list[LocalShow], str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                cur = con.execute("SELECT * FROM shows WHERE current = 1")
                rows = cur.fetchall()

                shows = [
                    LocalShow(
                        id=r['id'],
                        sid=r['sid'],
                        anilist_id=r['anilist_id'],
                        title_romaji=r['title_romaji'],
                        title_english=r['title_english'],
                        title_japanese=r['title_japanese'],
                        episode=r['last_episode'],
                        tracking=bool(r['tracking']),
                        current=bool(r['current']),
                    ) for r in rows
                ]
                return Ok(shows)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def update_show(self, show: LocalShow) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                cursor = con.execute("""
                    UPDATE shows
                    SET anilist_id = ?,
                        title_romaji = ?,
                        title_english = ?,
                        title_japanese = ?,
                        last_episode = ?,
                        tracking = ?,
                        current = ?
                    WHERE sid = ?
                """, (
                    show.anilist_id,
                    show.title_romaji,
                    show.title_english,
                    show.title_japanese,
                    show.episode,
                    show.tracking,
                    show.current,
                    show.sid
                ))
                if cursor.rowcount == 0:
                    return Err(f"Show with sid '{show.sid}' not found in DB.")
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def toggle_tracking(self, sid: str,
                        status: bool) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("""
                            UPDATE shows
                            SET tracking = ?
                            WHERE sid = ?
                """, (status, sid))
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def toggle_current(self, sid: str,
                       status: bool) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("""
                            UPDATE shows
                            SET current = ?
                            WHERE sid = ?
                """, (status, sid))
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")
