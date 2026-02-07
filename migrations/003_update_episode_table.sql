ALTER TABLE episodes ADD COLUMN episode INTEGER NOT NULL;
ALTER TABLE episodes ADD COLUMN torrent_hash TEXT;
ALTER TABLE episodes DROP COLUMN torrent_id;
