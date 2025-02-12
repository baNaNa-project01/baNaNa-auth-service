## 🚀 구현 내역

- **OAuth 로그인**
  - Kakao OAuth 로그인 및 JWT 발급
- **JWT 인증**
  - JWT를 활용한 사용자 인증
  - 로그인된 사용자만 게시글 작성 가능
- **게시판 기능**
  - 게시글 작성, 조회 기능 제공
- **Supabase 연동 (향후 업데이트 예정)**
  - Supabase를 활용한 데이터 관리 및 인증

```
📂 프로젝트 폴더
│── 📂 routes          # 로그인 및 게시판 관련 API
│   ├── kakao_auth.py  # Kakao 로그인 관련 API
│   ├── google_auth.py # Google 로그인 (추가 예정)
│   ├── posts.py       # 게시판 관련 API
│── 📂 instance        # SQLite 데이터베이스 (Git Ignore)
│── .env               # 환경 변수 설정 (Git Ignore)
│── app.py             # Flask 앱 실행 파일
│── models.py          # DB 모델 정의
│── README.md          # 프로젝트 소개 파일
```
