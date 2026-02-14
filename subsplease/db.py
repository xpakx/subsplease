import sqlite3
import msgspec
from subsplease.result import Result, Ok, Err
from pathlib import Path


class LocalShow(msgspec.Struct):
    id: int
    sid: str   # subsplease link
    anilist_id: int | None
    subsplease_id: int | None
    title_romaji: str
    title_english: str | None
    title_japanese: str | None
    last_episode: int
    dir_name: str | None
    tracking: bool
    current: bool


class LocalEpisode(msgspec.Struct):
    id: int
    show_id: int
    episode: int
    torrent_hash: str | None
    watched: bool
    downloaded: bool
    started: bool


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
                    self.db_to_object(LocalShow, r) for r in rows
                ]
                return Ok(shows)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def db_to_object(self, obj_type, data):
        fields = msgspec.structs.fields(obj_type)
        obj = {}
        for field in fields:
            value = data[field.name]
            if field.type == bool:
                value = bool(value)
            obj[field.name] = value
        return msgspec.convert(obj, obj_type)

    def update_show(self, show: LocalShow) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                cursor = con.execute("""
                    UPDATE shows
                    SET anilist_id = ?,
                        subsplease_id = ?,
                        title_romaji = ?,
                        title_english = ?,
                        title_japanese = ?,
                        dir_name = ?,
                        last_episode = ?,
                        tracking = ?,
                        current = ?
                    WHERE sid = ?
                """, (
                    show.anilist_id,
                    show.subsplease_id,
                    show.title_romaji,
                    show.title_english,
                    show.title_japanese,
                    show.dir_name,
                    show.last_episode,
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
                cur = con.execute(
                        "SELECT * FROM shows WHERE sid = ? LIMIT 1",
                        (sid,))
                r = cur.fetchone()

                show = self.db_to_object(LocalShow, r)
                return Ok(show)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def get_show_by_id(self, id: int) -> Result[LocalShow, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                cur = con.execute(
                        "SELECT * FROM shows WHERE id = ? LIMIT 1",
                        (id,))
                r = cur.fetchone()

                show = self.db_to_object(LocalShow, r)
                return Ok(show)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def create_episode(
            self, show_id: int, episode: int,
            hash: str
    ) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                con.execute("""
                    INSERT OR IGNORE
                    INTO episodes (show_id, episode, torrent_hash, started)
                    VALUES (?, ?, ?, ?)
                """, (show_id, episode, hash, True))
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
                if r is None:
                    return Err('')

                show = LocalEpisode(
                        id=r['id'],
                        show_id=r['show_id'],
                        episode=r['episode'],
                        torrent_hash=r['torrent_hash'],
                        watched=bool(r['watched']),
                        downloaded=bool(r['downloaded']),
                        started=bool(r['started']),
                )
                return Ok(show)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def get_unfinished_downloads(self):
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                cur = con.execute("""
                                  SELECT *
                                  FROM episodes
                                  WHERE downloaded = 0
                                  AND started = 1
                                  AND torrent_hash IS NOT NULL
                                  """)
                rows = cur.fetchall()

                shows = [
                    self.db_to_object(LocalEpisode, r) for r in rows
                ]
                return Ok(shows)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def get_all_eps(self):
        try:
            with sqlite3.connect(self.db_path) as con:
                con.row_factory = sqlite3.Row
                cur = con.execute("""
                                  SELECT *
                                  FROM episodes
                                  """)
                rows = cur.fetchall()

                shows = [
                    self.db_to_object(LocalEpisode, r) for r in rows
                ]
                return Ok(shows)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")

    def update_episode(self, episode: LocalEpisode) -> Result[bool, str]:
        try:
            with sqlite3.connect(self.db_path) as con:
                cursor = con.execute("""
                    UPDATE episodes
                    SET show_id = ?,
                        episode = ?,
                        torrent_hash = ?,
                        watched = ?,
                        downloaded = ?,
                        started = ?
                    WHERE id = ?
                """, (
                    episode.show_id,
                    episode.episode,
                    episode.torrent_hash,
                    episode.watched,
                    episode.downloaded,
                    episode.started,
                    episode.id
                ))
                if cursor.rowcount == 0:
                    return Err(f"Episode '{episode.id}' not found in DB.")
            return Ok(True)
        except sqlite3.Error as e:
            return Err(f"DB Error: {e}")
