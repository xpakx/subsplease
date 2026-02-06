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
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    show_id INTEGER NOT NULL,
    torrent_id INTEGER,
    downloaded BOOLEAN DEFAULT 0,
    watched BOOLEAN DEFAULT 0
);

