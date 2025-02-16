from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

auth = Blueprint("auth", __name__)

@auth.route("/auth/me", methods=["GET"])
def get_current_user():
    """ 현재 로그인한 사용자 정보 반환 """

    # ✅ Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "유효하지 않은 토큰"}), 401

    # ✅ "Bearer " 문자열 제거 후 JWT 추출
    jwt_token = auth_header.split(" ")[1]

    # ✅ JWT 해석
    try:
        user_id = get_jwt_identity()  # Flask-JWT-Extended가 자동으로 토큰에서 identity 추출
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
        
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
        })
    except Exception as e:
        return jsonify({"error": f"토큰 검증 실패: {str(e)}"}), 401
