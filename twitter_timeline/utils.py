import hashlib
import string
import random
from datetime import datetime
from functools import wraps
from bson.objectid import ObjectId


from flask import request, g, abort

JSON_MIME_TYPE = 'application/json'


def md5(token):
    new_token = token
    if str != bytes:
        new_token = token.encode('utf-8')
    return hashlib.md5(new_token)


def generate_random_token(size=15):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def sqlite_date_to_python(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def python_date_to_json_str(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def auth_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        auth = g.db.auth.find_one(
            {'access_token': request.headers['Authorization']})
        if not auth:
            abort(401)
        kwargs['user_id'] = str(auth['user_id'])
        return f(*args, **kwargs)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != JSON_MIME_TYPE:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function

def get_user_name(user_id):
    user = g.db.users.find_one({'_id': ObjectId(user_id)})
    return user['username'] if user else None