import os
from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db, init_db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flasgger import Swagger

from routes.kakao_auth import kakao_auth
from routes.posts import posts
from routes.google_auth import google_auth
from routes.comments import comments
from routes.naver_auth import naver_auth

# ✅ 환경 변수 로드
load_dotenv()

# ✅ Flask 앱 설정
app = Flask(__name__)
CORS(app, supports_credentials=True)  

swagger_template = {
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT 토큰을 입력하세요. 예: Bearer {token}"
        }
    },
    "security": [
        {"Bearer": []}
    ]
}

swagger = Swagger(app, template=swagger_template)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")

# ✅ Supabase PostgreSQL 데이터베이스 설정
#app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SUPABASE_DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SUPABASE_DB_URL").replace("5432", "6543")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,  # 🛠 DB 연결이 끊겼는지 확인 후 자동으로 다시 연결
    "pool_recycle": 1800,   # ⏳ 30분마다 연결을 새로고침
}


# ✅ DB 및 JWT 초기화
db = SQLAlchemy()
jwt = JWTManager(app)

# ✅ 모델 import 후 초기화
from models import db, User, Post, init_db
init_db(app)

# ✅ Flask 컨텍스트에서 DB 생성
with app.app_context():
    print("🚀 데이터베이스 테이블 생성 시작...")
    try:
        db.create_all()
        print("✅ 데이터베이스 테이블 생성 완료!")
    except Exception as e:
        print("❌ 데이터베이스 생성 실패:", str(e))



# ✅ 라우트 등록
app.register_blueprint(kakao_auth)
app.register_blueprint(posts)
app.register_blueprint(google_auth)
app.register_blueprint(comments)
app.register_blueprint(naver_auth)

# ✅ 사용자 정보 확인 (JWT 필요)
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    현재 로그인된 사용자 정보 반환
    ---
    tags:
      - User
    security:
      - Bearer: []
    responses:
      200:
        description: 사용자 정보 조회 성공
        schema:
          type: object
          properties:
            message:
              type: string
            user_info:
              type: string
      401:
        description: 인증 실패
    """
    current_user = get_jwt_identity()
    return jsonify({
        "message": "사용자 정보 조회 성공",
        "user_info": current_user
    })

# ✅ 로그아웃 (JWT 기반이라 별도 로그아웃 불필요)
@app.route("/logout")
@jwt_required()
def logout():
    """
    로그아웃 엔드포인트
    클라이언트에서 JWT를 삭제하면 로그아웃 처리됩니다.
    ---
    tags:
      - User
    security:
      - Bearer: []
    responses:
      200:
        description: 로그아웃 성공 메시지 반환
        schema:
          type: object
          properties:
            message:
              type: string
      401:
        description: 인증 실패
    """
    return jsonify({"message": "로그아웃 성공, JWT 기반이므로 클라이언트에서 토큰을 삭제하세요."})

@app.route("/health")
def health_check():
    return "OK", 200


# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
