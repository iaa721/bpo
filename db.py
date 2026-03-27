import sqlite3
import bcrypt

conn = sqlite3.connect('dionys.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    try:
        with open('init.sql', 'r', encoding='utf-8') as file:
            init_sql = file.read()
        cursor.executescript(init_sql)
        conn.commit()
        print("Успешная инициализация базы данных.")
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")

init_db()

def hash_password(plain_password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(user_id, username, password):
    try:
        cursor.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)',
                       (user_id, username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_username(username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def get_user_by_id(user_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()


#Функции для игр
def create_game(game_id, title, description, owner_id):
    try:
        default_url = f"/download/{game_id}"
        cursor.execute('INSERT INTO games (id, title, description, owner_id, download_url) VALUES (?, ?, ?, ?, ?)',
                       (game_id, title, description, owner_id, default_url))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def upload_game(game_id, download_url):
    try:
        cursor.execute('UPDATE games SET download_url = ? WHERE id = ?', (download_url, game_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_games():
    cursor.execute('SELECT * FROM games')
    return cursor.fetchall()

def get_game_by_id(game_id):
    cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
    return cursor.fetchone()

def delete_game(game_id, owner_id):
    # Можно добавить проверку, что текущий пользователь — владелец
    cursor.execute('DELETE FROM games WHERE id = ? AND owner_id = ?', (game_id, owner_id))
    conn.commit()
    return cursor.rowcount > 0

def get_games_by_user(user_id):
    cursor.execute('SELECT * FROM games WHERE owner_id = ?', (user_id,))
    return cursor.fetchall()


#Комментарии
def add_comment(game_id, comment_id, user_id, content):
    try:
        cursor.execute('INSERT INTO comments (id, game_id, user_id, content) VALUES (?, ?, ?, ?)',
                       (comment_id, game_id, user_id, content))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_comment(comment_id, user_id):
    # Можно добавить проверку, что комментарий принадлежит пользователю
    cursor.execute('DELETE FROM comments WHERE id = ? AND user_id = ?', (comment_id, user_id))
    conn.commit()
    return cursor.rowcount > 0

def get_user_favorites(user_id):
    cursor.execute('''
        SELECT games.* FROM games
        JOIN favorites ON games.id = favorites.game_id
        WHERE favorites.user_id = ?
    ''', (user_id,))
    return cursor.fetchall()

def get_comments_for_game(game_id):
    cursor.execute('SELECT * FROM comments WHERE game_id = ?', (game_id,))
    return cursor.fetchall()


def add_favorite(game_id, user_id):
    try:
        cursor.execute('INSERT INTO favorites (user_id, game_id) VALUES (?, ?)', (user_id, game_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_favorite(game_id, user_id):
    cursor.execute('DELETE FROM favorites WHERE user_id = ? AND game_id = ?', (user_id, game_id))
    conn.commit()
    return cursor.rowcount > 0

#Жалобы
def report_game(report_id, game_id, user_id, reason):
    cursor.execute('INSERT INTO reports (id, game_id, user_id, reason, report_type) VALUES (?, ?, ?, ?, ?)',
                   (report_id, game_id, user_id, reason, 'game'))
    conn.commit()
    return True

def report_comment(report_id, game_id, current_user_id, comment_id, reason):
    cursor.execute('INSERT INTO reports (id, game_id, user_id, comment_id, reason, report_type) VALUES (?, ?, ?, ?, ?, ?)',
                   (report_id, game_id, current_user_id, comment_id, reason, 'comment'))
    conn.commit()
    return True

#Лайки / Удаление лайков

# Для закрытия соединения
def close_connection():
    conn.close()

# Не забудьте вызвать close_connection() при завершении работы приложения
