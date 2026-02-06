import sqlite3
import msgspec
from result import Result, Ok, Err
from pathlib import Path


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


class LocalEpisode(msgspec.Struct):
    id: int
    show_id: int
    episode: int
    torrent_id: int | None
    watched: bool
    downloaded: bool


class AnimeDB:
    def __init__(self, db_path: str = "ani.db"):
        self.db_path = db_path
        self._run_migrations()

    def _run_migrations(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            con.commit()

            cur = con.execute("SELECT filename FROM _migrations")
            applied = {row[0] for row in cur.fetchall()}

            migration_dir = Path("migrations")
            for sql_file in sorted(migration_dir.glob("*.sql")):
                if sql_file.name in applied:
                    continue

                print(f"Applying migration from {sql_file.name}...")
                try:
                    con.execute("BEGIN")
                    con.executescript(sql_file.read_text())
                    con.execute("""
                                INSERT INTO _migrations (filename)
                                VALUES (?)
                    """, (sql_file.name,))
                    con.commit()
                    print("  -> Success")
                except Exception as e:
                    con.rollback()
                    print(f"  -> Failed: {e}")
                    break

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

    def get_show(self, sid: str) -> Result[LocalShow, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                print(sid)
                cur = con.execute(
                        "SELECT * FROM shows WHERE sid = ? LIMIT 1",
                        (sid,))
                r = cur.fetchone()

                show = LocalShow(
                        id=r['id'],
                        sid=r['sid'],
                        anilist_id=r['anilist_id'],
                        title_romaji=r['title_romaji'],
                        title_english=r['title_english'],
                        title_japanese=r['title_japanese'],
                        episode=r['last_episode'],
                        tracking=bool(r['tracking']),
                        current=bool(r['current']))

                return Ok(show)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def create_episode(self, show_id: int, episode: int) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("""
                    INSERT OR IGNORE INTO episodes (show_id, episode)
                    VALUES (?, ?)
                """, (show_id, episode))
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def get_episode(self, show_id: str, episode: int
                    ) -> Result[LocalEpisode, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                cur = con.execute(
                        """
                        SELECT *
                        FROM episodes
                        WHERE show_id = ?
                        AND episode = ?
                        LIMIT 1
                        """,
                        (show_id, episode))
                r = cur.fetchone()

                show = LocalEpisode(
                        id=r['id'],
                        show_id=r['show_id'],
                        episode=r['episode'],
                        torrent_id=r['episode'],
                        watched=bool(r['watched']),
                        downloaded=bool(r['downloaded']),
                )
                return Ok(show)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")
