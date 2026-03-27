CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        );

CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            owner_id TEXT,
            download_url TEXT,
            FOREIGN KEY(owner_id) REFERENCES users(id)
        );

CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            user_id TEXT,
            content TEXT,
            FOREIGN KEY(game_id) REFERENCES games(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

CREATE TABLE IF NOT EXISTS favorites (
            user_id TEXT,
            game_id INTEGER,
            PRIMARY KEY(user_id, game_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(game_id) REFERENCES games(id)
        );

CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            game_id INTEGER,
            user_id TEXT,
            reason TEXT,
            report_type TEXT,
            comment_id TEXT,
            FOREIGN KEY(game_id) REFERENCES games(id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(comment_id) REFERENCES comments(id)
        )