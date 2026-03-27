_U='Failed to report'
_T='Missing comment_id'
_S='comment_id'
_R='Game not found'
_Q='game_id'
_P='Password'
_O='Username'
_N='password'
_M='user_id'
_L='Reason'
_K='reason'
_J='download_url'
_I='username'
_H=None
_G='SECRET_KEY'
_F='GET'
_E='Invalid JSON'
_D='POST'
_C='message'
_B='Internal server error'
_A='error'
import os,json,datetime,uuid,logging
from functools import wraps
from flask import Flask,request,jsonify,g
import jwt,bcrypt,db
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)
app=Flask(__name__)
app.config[_G]=os.environ.get(_G,'$2b$12$exqNYe66fu9nLoU9HXMC8Ota5TjOuImz1e/lLqqunaRY0NBhFR0mi')
MIN_USERNAME_LENGTH=3
MAX_USERNAME_LENGTH=50
MIN_PASSWORD_LENGTH=6
MAX_PASSWORD_LENGTH=128
MIN_TITLE_LENGTH=1
MAX_TITLE_LENGTH=200
MIN_DESCRIPTION_LENGTH=1
MAX_DESCRIPTION_LENGTH=2000
MAX_COMMENT_LENGTH=1000
MAX_REASON_LENGTH=500
@app.teardown_appcontext
def close_db(exception):'Close database connection at end of request.';db.close_connection()
@app.before_request
def log_request():'Log incoming requests.';logger.info(f"{request.method} {request.path} from {request.remote_addr}")
def token_required(f):
	'Decorator to require valid JWT token for route.'
	@wraps(f)
	def A(*D,**E):
		C='Authorization';A=_H
		if C in request.headers:
			F=request.headers[C];B=F.split()
			if len(B)==2 and B[0]=='Bearer':A=B[1]
		if not A:return jsonify({_A:'Token is missing'}),401
		try:G=jwt.decode(A,app.config[_G],algorithms=['HS256']);H=G[_M]
		except jwt.ExpiredSignatureError:return jsonify({_A:'Token has expired'}),401
		except jwt.InvalidTokenError:return jsonify({_A:'Invalid token'}),401
		return f(H,*D,**E)
	return A
def validate_string(value,min_len,max_len,field_name):
	'Validate string length and type.';E=max_len;D=min_len;C=False;B=field_name;A=value
	if A is _H:return C,f"Missing {B}"
	if not isinstance(A,str):return C,f"{B} must be a string"
	if len(A)<D or len(A)>E:return C,f"{B} must be between {D} and {E} characters"
	return True,_H
@app.route('/register',methods=[_D])
def register():
	'Register a new user.'
	try:
		A=request.get_json()
		if not A:return jsonify({_A:_E}),400
		B=A.get(_I);E=A.get(_N);C,D=validate_string(B,MIN_USERNAME_LENGTH,MAX_USERNAME_LENGTH,_O)
		if not C:return jsonify({_A:D}),400
		C,D=validate_string(E,MIN_PASSWORD_LENGTH,MAX_PASSWORD_LENGTH,_P)
		if not C:return jsonify({_A:D}),400
		F=db.hash_password(E);G=str(uuid.uuid4());H=db.create_user(G,B,F)
		if not H:return jsonify({_A:'User already exists'}),400
		logger.info(f"User registered: {B}");return jsonify({_C:'Registration successful'}),201
	except Exception as I:logger.error(f"Registration error: {I}");return jsonify({_A:_B}),500
@app.route('/login',methods=[_D])
def login():
	'Login and get JWT token.'
	try:
		A=request.get_json()
		if not A:return jsonify({_A:_E}),400
		E=A.get(_I);F=A.get(_N);B,C=validate_string(E,MIN_USERNAME_LENGTH,MAX_USERNAME_LENGTH,_O)
		if not B:return jsonify({_A:C}),400
		B,C=validate_string(F,MIN_PASSWORD_LENGTH,MAX_PASSWORD_LENGTH,_P)
		if not B:return jsonify({_A:C}),400
		D=db.get_user_by_username(E)
		if D and db.verify_password(F,D[2]):G=jwt.encode({_M:D[0],'exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=24)},app.config[_G],algorithm='HS256');return jsonify({'token':G})
		else:return jsonify({_A:'Invalid credentials'}),401
	except Exception as H:logger.error(f"Login error: {H}");return jsonify({_A:_B}),500
@app.route('/games/new',methods=[_D])
@token_required
def create_game(current_user_id):
	'Create a new game.';E=current_user_id
	try:
		A=request.get_json()
		if not A:return jsonify({_A:_E}),400
		F=A.get('title');G=A.get('description');B,C=validate_string(F,MIN_TITLE_LENGTH,MAX_TITLE_LENGTH,'Title')
		if not B:return jsonify({_A:C}),400
		B,C=validate_string(G,MIN_DESCRIPTION_LENGTH,MAX_DESCRIPTION_LENGTH,'Description')
		if not B:return jsonify({_A:C}),400
		D=str(uuid.uuid4());H=db.create_game(D,F,G,E)
		if H:logger.info(f"Game created: {D} by user {E}");return jsonify({_C:'Game created',_Q:D}),201
		return jsonify({_A:'Failed to create game'}),400
	except Exception as I:logger.error(f"Create game error: {I}");return jsonify({_A:_B}),500
@app.route('/games',methods=[_F])
def get_games():
	'Get all games.'
	try:A=db.get_all_games();return jsonify(A)
	except Exception as B:logger.error(f"Get games error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>',methods=[_F])
def get_game_info(game_id):
	'Get game by ID.'
	try:
		A=db.get_game_by_id(game_id)
		if A:return jsonify(A)
		return jsonify({_A:_R}),404
	except Exception as B:logger.error(f"Get game error: {B}");return jsonify({_A:_B}),500
@app.route('/myprofile',methods=[_F])
@token_required
def my_profile(current_user_id):
	'Get current user profile.'
	try:
		A=db.get_user_by_id(current_user_id)
		if A:return jsonify({'id':A[0],_I:A[1]})
		return jsonify({_A:'User not found'}),404
	except Exception as B:logger.error(f"Get profile error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/delete',methods=[_D])
@token_required
def delete_game(current_user_id,game_id):
	'Delete a game.';B=game_id;A=current_user_id
	try:
		C=db.delete_game(B,A)
		if C:logger.info(f"Game deleted: {B} by user {A}");return jsonify({_C:'Game deleted'})
		return jsonify({_A:'Failed to delete game'}),400
	except Exception as D:logger.error(f"Delete game error: {D}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/comment/add',methods=[_D])
@token_required
def add_comment(current_user_id,game_id):
	'Add a comment to a game.';A=game_id
	try:
		B=request.get_json()
		if not B:return jsonify({_A:_E}),400
		C=B.get('content');E,F=validate_string(C,1,MAX_COMMENT_LENGTH,'Content')
		if not E:return jsonify({_A:F}),400
		D=str(uuid.uuid4());G=db.add_comment(A,D,current_user_id,C)
		if G:logger.info(f"Comment added: {D} to game {A}");return jsonify({_C:'Comment added'}),201
		return jsonify({_A:'Failed to add comment'}),400
	except Exception as H:logger.error(f"Add comment error: {H}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/comments',methods=[_F])
def get_comments(game_id):
	'Get all comments for a game.'
	try:
		A=db.get_comments_for_game(game_id)
		if A is not _H:return jsonify(A)
		return jsonify({_A:'Comments not found'}),404
	except Exception as B:logger.error(f"Get comments error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/comment/delete',methods=[_D])
@token_required
def delete_comment(current_user_id,game_id):
	'Delete a comment.'
	try:
		B=request.get_json()
		if not B:return jsonify({_A:_E}),400
		A=B.get(_S)
		if not A:return jsonify({_A:_T}),400
		C=db.delete_comment(A,current_user_id)
		if C:logger.info(f"Comment deleted: {A}");return jsonify({_C:'Comment deleted'})
		return jsonify({_A:'Failed to delete comment'}),400
	except Exception as D:logger.error(f"Delete comment error: {D}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/download',methods=[_F])
@token_required
def download_game(current_user_id,game_id):
	'Get game download URL.'
	try:
		A=db.get_game_by_id(game_id)
		if A:return jsonify({_C:'Download started','url':A.get(_J,'')})
		return jsonify({_A:_R}),404
	except Exception as B:logger.error(f"Download game error: {B}");return jsonify({_A:_B}),500
@app.route('/myprofile/favorites',methods=[_F])
@token_required
def get_favorites(current_user_id):
	"Get current user's favorite games."
	try:A=db.get_user_favorites(current_user_id);return jsonify(A)
	except Exception as B:logger.error(f"Get favorites error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/report',methods=[_D])
@token_required
def report_game(current_user_id,game_id):
	'Report a game.';B=game_id;A=current_user_id
	try:
		C=request.get_json()
		if not C:return jsonify({_A:_E}),400
		D=C.get(_K);E,F=validate_string(D,1,MAX_REASON_LENGTH,_L)
		if not E:return jsonify({_A:F}),400
		G=str(uuid.uuid4());H=db.report_game(G,B,A,D)
		if H:logger.info(f"Game reported: {B} by user {A}");return jsonify({_C:'Report submitted'}),201
		return jsonify({_A:_U}),400
	except Exception as I:logger.error(f"Report game error: {I}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/like',methods=[_D])
@token_required
def like_game(current_user_id,game_id):
	'Like a game.'
	try:
		A=db.like_game(game_id,current_user_id)
		if A:return jsonify({_C:'Game liked'})
		return jsonify({_A:'Failed to like'}),400
	except Exception as B:logger.error(f"Like game error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/unlike',methods=[_D])
@token_required
def unlike_game(current_user_id,game_id):
	'Unlike a game.'
	try:
		A=db.unlike_game(game_id,current_user_id)
		if A:return jsonify({_C:'Game unliked'})
		return jsonify({_A:'Failed to unlike'}),400
	except Exception as B:logger.error(f"Unlike game error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/favorite',methods=[_D])
@token_required
def add_favorite(current_user_id,game_id):
	'Add game to favorites.'
	try:
		A=db.add_favorite(game_id,current_user_id)
		if A:return jsonify({_C:'Game added to favorites'})
		return jsonify({_A:'Failed to add favorite'}),400
	except Exception as B:logger.error(f"Add favorite error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/unfavorite',methods=[_D])
@token_required
def remove_favorite(current_user_id,game_id):
	'Remove game from favorites.'
	try:
		A=db.remove_favorite(game_id,current_user_id)
		if A:return jsonify({_C:'Game removed from favorites'})
		return jsonify({_A:'Failed to remove favorite'}),400
	except Exception as B:logger.error(f"Remove favorite error: {B}");return jsonify({_A:_B}),500
@app.route('/user/<user_id>/games',methods=[_F])
def user_games(user_id):
	'Get games by user ID.'
	try:A=db.get_games_by_user(user_id);return jsonify(A)
	except Exception as B:logger.error(f"Get user games error: {B}");return jsonify({_A:_B}),500
@app.route('/games/<game_id>/upload',methods=[_D])
@token_required
def upload_game(current_user_id,game_id):
	'Upload game with download URL.';A=game_id
	try:
		C=request.get_json()
		if not C:return jsonify({_A:_E}),400
		B=C.get(_J);D,E=validate_string(B,1,500,'Download URL')
		if not D:return jsonify({_A:E}),400
		F=db.upload_game(A,B)
		if F:logger.info(f"Game uploaded: {A}");return jsonify({_C:'Game uploaded',_Q:A,_J:B}),200
		return jsonify({_A:'Failed to upload game'}),400
	except Exception as G:logger.error(f"Upload game error: {G}");return jsonify({_A:_B}),500
@app.route('/game/<game_id>/report',methods=[_D])
@token_required
def report_individual_game(current_user_id,game_id):
	'Report a game (alternative endpoint).';B=game_id;A=current_user_id
	try:
		C=request.get_json()
		if not C:return jsonify({_A:_E}),400
		D=C.get(_K);E,F=validate_string(D,1,MAX_REASON_LENGTH,_L)
		if not E:return jsonify({_A:F}),400
		G=str(uuid.uuid4());H=db.report_game(G,B,A,D)
		if H:logger.info(f"Game reported: {B} by user {A}");return jsonify({_C:'Reported'}),201
		return jsonify({_A:_U}),400
	except Exception as I:logger.error(f"Report game error: {I}");return jsonify({_A:_B}),500
@app.route('/game/<game_id>/comment/report',methods=[_D])
@token_required
def report_comment(current_user_id,game_id):
	'Report a comment.'
	try:
		A=request.get_json()
		if not A:return jsonify({_A:_E}),400
		B=A.get(_S);C=A.get(_K)
		if not B:return jsonify({_A:_T}),400
		D,E=validate_string(C,1,MAX_REASON_LENGTH,_L)
		if not D:return jsonify({_A:E}),400
		F=str(uuid.uuid4());G=db.report_comment(F,game_id,B,current_user_id,C)
		if G:logger.info(f"Comment reported: {B}");return jsonify({_C:'Comment reported'}),201
		return jsonify({_A:'Failed to report comment'}),400
	except Exception as H:logger.error(f"Report comment error: {H}");return jsonify({_A:_B}),500
@app.route('/openapi.json',methods=[_F])
def openapi():
	'Get OpenAPI specification.'
	try:
		with open('openapi.json','r')as A:B=json.load(A)
		return jsonify(B)
	except Exception as C:logger.error(f"Get OpenAPI error: {C}");return jsonify({_A:'Failed to load OpenAPI spec'}),500
if __name__=='__main__':app.run(debug=True)