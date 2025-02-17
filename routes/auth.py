from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User

auth = Blueprint("auth", __name__)

@auth.route("/auth/me", methods=["GET"])
@jwt_required()  # ✅ JWT 인증 추가 (토큰 검증)
def get_current_user():
    """
    현재 로그인한 사용자 정보 반환

    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: 로그인한 사용자의 정보 반환
        schema:
          type: object
          properties:
            id:
              type: integer
              description: 사용자 ID
            name:
              type: string
              description: 사용자 이름
            email:
              type: string
              description: 사용자 이메일 (없는 경우 "No Email" 반환)
      401:
        description: 인증 실패 (유효하지 않은 JWT 토큰)
        schema:
          type: object
          properties:
            error:
              type: string
              description: "토큰 검증 실패"
      404:
        description: 사용자를 찾을 수 없음
        schema:
          type: object
          properties:
            error:
              type: string
              description: "사용자를 찾을 수 없습니다."
    """

    try:
        user_id = get_jwt_identity()  # ✅ JWT에서 사용자 ID 추출
        print("✅ [DEBUG] 인증된 사용자 ID:", user_id)

        # ✅ 사용자 정보 조회
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
        
        # ✅ 사용자 정보 반환
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }), 200

    except Exception as e:
        print("🚨 [DEBUG] JWT 인증 실패:", str(e))
        return jsonify({"error": f"토큰 검증 실패: {str(e)}"}), 401
