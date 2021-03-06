from functools import wraps

from flask import request, Blueprint, jsonify
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from api.errors import *
from api.models import db, User
from helpers import get_signature


api_v1 = Blueprint('v1', __name__)


######################## Authentication ################################

def requires_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            api_key, signature1 = request.headers['Authorization'].split(":")
            try:
                user = db.session.query(User).filter(User.api_key == api_key).first()
            except (NoResultFound, MultipleResultsFound) as e:
                return internal_error(e)

            if signature1 == get_signature(str(user.secret_access_key), request):
                return func(*args, **kwargs)
            else:
                return bad_request('Bad Request')
        return not_authorized()
    return wrapper

############################# Views ####################################


@api_v1.route('/meta', methods=['GET'])
def index():
    data = {
        "name": "My API",
        "version": "1.0",
        "organisation": "Me only",
        "description": "this is version 1.0 of my api!"
    }
    return jsonify(data)
