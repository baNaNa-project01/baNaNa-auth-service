from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

auth = Blueprint("auth", __name__)

@auth.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """현재 로그인한 사용자 정보 반환"""

    print(f"🔹 Request Headers: {request.headers}")  # 요청 헤더 확인
    print(f"🔹 Request Cookies: {request.cookies}")  # 쿠키 확인
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "provider": user.provider
    })
