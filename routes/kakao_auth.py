import os
import requests
import datetime
from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

# 🔹 Flask Blueprint 설정
kakao_auth = Blueprint("kakao_auth", __name__)

# ✅ Kakao OAuth 설정
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"


# ✅ 1️⃣ Kakao 로그인 (JWT 발급)
@kakao_auth.route("/login/kakao")
def login_kakao():
    kakao_login_url = (
        f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    )
    return redirect(kakao_login_url)


@kakao_auth.route("/login/kakao/callback")
def kakao_callback():
    """카카오 로그인 후 JWT 발급"""
    code = request.args.get("code")
    token_data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "client_secret": KAKAO_CLIENT_SECRET,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    response = requests.post(KAKAO_TOKEN_URL, data=token_data)
    token_json = response.json()

    if "access_token" not in token_json:
        return "카카오 로그인 실패: " + str(token_json), 400  

    access_token = token_json["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(KAKAO_USER_URL, headers=headers)
    user_info = user_response.json()

    print("🔹 카카오 사용자 정보 응답:", user_info)

    # 🚀 DB에 사용자 저장
    with db.session.begin():
        user = User.query.filter_by(social_id=user_info["id"], provider="kakao").first()
        if not user:
            user = User(
                provider="kakao",
                social_id=user_info["id"],
                name=user_info["kakao_account"]["profile"]["nickname"],
                email=user_info["kakao_account"].get("email", "No Email")
            )
            db.session.add(user)

    # ✅ JWT 발급
    jwt_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=1))

    return jsonify({
        "message": "카카오 로그인 성공",
        "token": jwt_token
    })
