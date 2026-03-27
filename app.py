from flask import Flask, request, jsonify
import jwt
import json
import datetime
from functools import wraps
import uuid
import db

app = Flask(__name__)
app.config['SECRET_KEY'] = '$2b$12$exqNYe66fu9nLoU9HXMC8Ota5TjOuImz1e/lLqqunaRY0NBhFR0mi'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password or username=="" or password=="":
        return jsonify({'error': 'Missing username or password'}), 400
    hashed_password = db.hash_password(password)  # Реализуйте в db
    user_id = str(uuid.uuid4())

    success = db.create_user(user_id, username, hashed_password)
    if not success:
        return jsonify({'error': 'User already exists'}), 400
    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password or username=="" or password=="":
        return jsonify({'error': 'Missing username or password'}), 400
    user = db.get_user_by_username(username)
    if user and db.verify_password(password, user[2]):
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/games/new', methods=['POST'])
@token_required
def create_game(current_user_id):
    data = request.json
    game_id = str(uuid.uuid4())
    title = data.get('title')
    description = data.get('description')
    if title=="" or description=="":
        return jsonify({'error': 'Method Not Allowed'}), 405
    success = db.create_game(game_id, title, description, current_user_id)
    if success:
        return jsonify({'message': 'Game created', 'game_id': game_id})
    return jsonify({'error': 'Failed to create game'}), 400

@app.route('/games', methods=['GET'])
def get_games():
    games = db.get_all_games()
    return jsonify(games)

@app.route('/games/<game_id>', methods=['GET'])
def get_game_info(game_id):
    game = db.get_game_by_id(game_id)
    if game:
        return jsonify(game)
    return jsonify({'error': 'Game not found'}), 404

@app.route('/myprofile', methods=['GET'])
@token_required
def my_profile(current_user_id):
    user = db.get_user_by_id(current_user_id)
    return jsonify(user[1])

@app.route('/games/<game_id>/delete', methods=['POST'])
@token_required
def delete_game(current_user_id, game_id):
    success = db.delete_game(game_id, current_user_id)
    if success:
        return jsonify({'message': 'Game deleted'})
    return jsonify({'error': 'Failed to delete game'}), 400

@app.route('/games/<game_id>/comment/add', methods=['POST'])
@token_required
def add_comment(current_user_id, game_id):
    data = request.json
    content = data.get('content')
    comment_id = str(uuid.uuid4())
    success = db.add_comment(game_id, comment_id, current_user_id, content)
    if success:
        return jsonify({'message': 'Comment added'})
    return jsonify({'error': 'Failed to add comment'}), 400

@app.route('/games/<game_id>/comments', methods=['GET'])
def get_comments(game_id):
    comments = db.get_comments_for_game(game_id)
    if comments:
        return jsonify(comments)
    return jsonify({'error': 'Комментарии не найдены'}), 404

@app.route('/games/<game_id>/comment/delete', methods=['POST'])
@token_required
def delete_comment(current_user_id, game_id):
    data = request.json
    comment_id = data.get('comment_id')
    success = db.delete_comment(comment_id, current_user_id)
    if success:
        return jsonify({'message': 'Comment deleted'})
    return jsonify({'error': 'Failed to delete comment'}), 400

@app.route('/games/<game_id>/download', methods=['GET'])
@token_required
def download_game(current_user_id, game_id):
    game = db.get_game_by_id(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify({'message': 'Download started', 'url': game[4]})

@app.route('/myprofile/favorites', methods=['GET'])
@token_required
def get_favorites(current_user_id):
    favorites = db.get_user_favorites(current_user_id)
    return jsonify(favorites)

@app.route('/games/<game_id>/report', methods=['POST'])
@token_required
def report_game(current_user_id, game_id):
    data = request.json
    reason = data.get('reason')
    success = db.report_game(game_id, current_user_id, reason)
    if success:
        return jsonify({'message': 'Report submitted'})
    return jsonify({'error': 'Failed to report'}), 400

@app.route('/games/<game_id>/like', methods=['POST'])
@token_required
def like_game(current_user_id, game_id):
    success = db.like_game(game_id, current_user_id)
    if success:
        return jsonify({'message': 'Game liked'})
    return jsonify({'error': 'Failed to like'}), 400

@app.route('/games/<game_id>/unlike', methods=['POST'])
@token_required
def unlike_game(current_user_id, game_id):
    success = db.unlike_game(game_id, current_user_id)
    if success:
        return jsonify({'message': 'Game unliked'})
    return jsonify({'error': 'Failed to unlike'}), 400

@app.route('/games/<game_id>/favorite', methods=['POST'])
@token_required
def add_favorite(current_user_id, game_id):
    success = db.add_favorite(game_id, current_user_id)
    if success:
        return jsonify({'message': 'Game added to favorites'})
    return jsonify({'error': 'Failed to add favorite'}), 400

@app.route('/games/<game_id>/unfavorite', methods=['POST'])
@token_required
def remove_favorite(current_user_id, game_id):
    success = db.remove_favorite(game_id, current_user_id)
    if success:
        return jsonify({'message': 'Game removed from favorites'})
    return jsonify({'error': 'Failed to remove favorite'}), 400

@app.route('/user/<user_id>/games', methods=['GET'])
def user_games(user_id):
    games = db.get_games_by_user(user_id)
    return jsonify(games)

@app.route('/games/<game_id>/upload', methods=['POST'])
@token_required
def upload_game(current_user_id, game_id):
    data = request.json
    download_url = data.get('download_url')
    success = db.upload_game(game_id, download_url)
    if success:
        return jsonify({'message': 'Game uploaded', 'game_id': game_id, 'download_url': download_url})
    return jsonify({'error': 'Failed to create game'}), 400

@app.route('/game/<game_id>/report', methods=['POST'])
@token_required
def report_individual_game(current_user_id, game_id):
    data = request.json
    reason = data.get('reason')
    report_id = str(uuid.uuid4())
    success = db.report_game(report_id, game_id, current_user_id, reason)
    if success:
        return jsonify({'message': 'Reported'})
    return jsonify({'error': 'Failed to report'}), 400

@app.route('/game/<game_id>/comment/report', methods=['POST'])
@token_required
def report_comment(current_user_id, game_id):
    data = request.json
    comment_id = data.get('comment_id')
    reason = data.get('reason')
    report_id = str(uuid.uuid4())
    success = db.report_comment(report_id, game_id, comment_id, current_user_id, reason)
    if success:
        return jsonify({'message': 'Comment reported'})
    return jsonify({'error': 'Failed to report comment'}), 400

@app.route('/openapi.json', methods=['GET'])
def openapi():
    file = open("openapi.json")
    openapi = json.load(file)
    return openapi


if __name__ == '__main__':
    app.run(debug=True)