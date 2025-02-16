import os
import requests
import datetime
from flask import Blueprint, redirect, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User
from flask import Response
import json
from flask_cors import cross_origin

google_auth = Blueprint("google_auth", __name__)

# 구글 OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

FRONT_PAGE_URL= os.getenv("FRONT_PAGE_URL", "https://banana-project01.github.io/baNaNa-frontend/")


@google_auth.route("/login/google")
@cross_origin()
def login_google():
    """
    구글 로그인 시작 엔드포인트
    사용자를 구글 로그인 페이지로 리다이렉트합니다.
    ---
    tags:
      - Authentication
    responses:
      302:
        description: 구글 로그인 페이지로 리다이렉트합니다.
    """
    google_login_url = (
        f"{GOOGLE_AUTH_URL}?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code&scope=openid%20email%20profile"
    )
    return redirect(google_login_url)

@google_auth.route("/login/google/callback")
@cross_origin()
def google_callback():
    """
    구글 로그인 콜백 엔드포인트
    구글에서 전달받은 authorization code를 사용하여 JWT를 발급하고,
    HttpOnly 쿠키에 토큰을 저장한 후 프론트엔드 페이지로 리다이렉트합니다.
    ---
    tags:
      - Authentication
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: 구글에서 전달받은 authorization code
    responses:
      302:
        description: 로그인 성공 후 프론트엔드 페이지로 리다이렉트합니다.
      400:
        description: "구글 로그인 실패 (예: access_token 미발급)"
    """
    code = request.args.get("code")
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    token_json = response.json()
    access_token = token_json.get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
    user_info = user_response.json()

    with db.session.begin():
        user = User.query.filter_by(social_id=user_info["id"], provider="google").first()
        if not user:
            user = User(
                provider="google",
                social_id=user_info["id"],
                name=user_info.get("name", "No Name"),
                email=user_info.get("email", "No Email")
            )
            db.session.add(user)
            

    jwt_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=1))

    # ✅ HttpOnly 쿠키에 JWT 토큰 저장
    response = redirect(FRONT_PAGE_URL)
    # max_age는 초 단위이며, secure=True는 HTTPS 사용 시에만 전송됩니다.
    response.set_cookie(
        "access_token", 
        jwt_token, 
        httponly=True, 
        secure=True, 
        samesite="Lax", 
        max_age=3600  # 1시간
    )
    return response 
