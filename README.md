# 🍌 배나낭 커뮤니티 - Flask & Supabase 기반 OAuth 로그인 및 게시판 서비스

### Swagger 문서

🔗 [API 문서 바로가기](https://banana-flask-app.onrender.com/apidocs/)

## ✅ 핵심 기능

### 🛡 OAuth 로그인 및 JWT 인증

- **Kakao, Naver, Google OAuth 로그인**
- 로그인 성공 시 JWT 발급 및 로컬 스토리지 저장
- `/auth/me` API를 통해 로그인된 사용자 정보 확인
- 로그인한 사용자만 게시글 작성 가능

### 📝 게시판 기능 (Supabase 연동)

- 게시글 작성, 수정, 삭제, 조회 기능 제공
- **Supabase DB**와 연동하여 데이터 저장
- 댓글 작성 및 삭제 기능 지원

### 🌐 배포 환경

- **백엔드**: Flask, Flask-JWT-Extended, SQLAlchemy
- **데이터베이스**: Supabase (PostgreSQL)
- **프론트엔드**: HTML, CSS, JavaScript (Vanilla JS)
- **배포**: Render(백엔드), GitHub Pages(프론트엔드)

## 🛠 주요 기능 상세

- 🛡 JWT 인증
  - 사용자는 OAuth 로그인 후 JWT를 발급받음
  - JWT는 로컬 스토리지에 저장됨
  - /auth/me API를 호출하여 로그인된 사용자 확인
- 📝 게시판 기능
  - 로그인한 사용자만 게시글 작성 가능
  - 게시글을 수정하거나 삭제할 수 있음
  - Supabase DB 연동하여 게시글을 저장
- 💬 댓글 기능
  - 댓글 작성 및 삭제 기능
  - 특정 게시물에 대한 댓글 목록 조회 가능
  - 댓글 작성자만 삭제 가능

---

```
📂 프로젝트 폴더
│── 📂 routes # 로그인 및 게시판 관련 API
│ ├── auth.py # JWT 인증 API
│ ├── kakao_auth.py # Kakao 로그인 관련 API
│ ├── naver_auth.py # Naver 로그인 관련 API
│ ├── google_auth.py # Google 로그인 관련 API
│ ├── posts.py # 게시판 관련 API
│ ├── comments.py # 댓글 API
│── 📂 instance # SQLite 데이터베이스 (Git Ignore)
│── 📂 test # 테스트 관련 코드
│── .env # 환경 변수 설정 (Git Ignore)
│── app.py # Flask 앱 실행 파일
│── models.py # DB 모델 정의
│── README.md # 프로젝트 소개 파일
│── requirements.txt # Python 패키지 목록
```
