import os
import json
import requests
from flask import Blueprint, redirect, request, jsonify, session
from flask_jwt_extended import create_access_token
from models import db, User
from flask_cors import cross_origin
import urllib.parse

naver_auth = Blueprint("naver_auth", __name__)

# ✅ 환경변수에서 네이버 OAuth 정보 불러오기
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

NAVER_AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USER_URL = "https://openapi.naver.com/v1/nid/me"

FRONT_PAGE_URL= os.getenv("FRONT_PAGE_URL", "https://banana-project01.github.io/baNaNa-frontend/")


# ✅ 네이버 로그인 페이지로 이동
@naver_auth.route("/login/naver")
@cross_origin()
def login_naver():
    """
    네이버 로그인 페이지로 이동
    ---
    tags:
      - Authentication
    responses:
      302:
        description: 네이버 로그인 페이지로 리다이렉트 합니다.
    """
    state = os.urandom(16).hex()  # CSRF 방지용 상태값
    session["naver_state"] = state  # 세션에 저장

    encoded_redirect_uri = urllib.parse.quote(NAVER_REDIRECT_URI, safe='')
    naver_login_url = (
        f"{NAVER_AUTH_URL}?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&state={state}"
    )
    print("네이버 로그인 URL: ", naver_login_url)
    return redirect(naver_login_url)


# ✅ 네이버 로그인 콜백
@naver_auth.route("/login/naver/callback")
@cross_origin()
def naver_callback():
    """
    네이버 로그인 후 JWT 발급
    ---
    tags:
      - Authentication
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: 네이버로부터 전달받은 인증 코드
      - name: state
        in: query
        type: string
        required: true
        description: CSRF 방지를 위한 상태 값 (세션에 저장된 값과 일치해야 함)
    responses:
      302:
        description: JWT 발급 후 HttpOnly 쿠키에 JWT를 저장하고 프론트엔드로 리다이렉트 합니다.
      400:
        description: CSRF 검증 실패, 네이버 로그인 실패 또는 사용자 정보 조회 실패
    """
    code = request.args.get("code")
    state = request.args.get("state")

    # CSRF 방지용 state 값 확인
    if state != session.get("naver_state"):
        return "CSRF 방지 실패", 400

    # ✅ access_token 요청
    token_data = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    response = requests.post(NAVER_TOKEN_URL, data=token_data)
    token_json = response.json()

    if "access_token" not in token_json:
        return "네이버 로그인 실패", 400

    access_token = token_json["access_token"]

    # ✅ access_token을 사용하여 사용자 정보 요청
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(NAVER_USER_URL, headers=headers)
    user_info = user_response.json().get("response", {})

    if not user_info:
        return "네이버 사용자 정보 조회 실패", 400

    print("🔹 네이버 사용자 정보:", user_info)

    # ✅ DB에 사용자 저장 또는 조회
    with db.session.begin():
        user = User.query.filter_by(social_id=user_info["id"], provider="naver").first()
        if not user:
            user = User(
                provider="naver",
                social_id=user_info["id"],
                name=user_info["name"],
                email=user_info.get("email", "No Email"),
            )
            db.session.add(user)

    # ✅ JWT 발급
    jwt_token = create_access_token(identity=str(user.id))

    # ✅ HttpOnly 쿠키 대신, URL 파라미터로 `token` 포함해서 프론트엔드 리다이렉트
    redirect_url = f"{FRONT_PAGE_URL}?token={jwt_token}"
    return redirect(redirect_url)
