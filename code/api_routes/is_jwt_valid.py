from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import jsonify
@jwt_required()
def is_jwt_valid():
    return jsonify({"msg": "success"})
