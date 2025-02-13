import os
import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post, User
from werkzeug.utils import secure_filename
from supabase import create_client, Client


# Flask Blueprint 설정
posts = Blueprint("posts", __name__)

# Supabase 연결
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ 게시글 작성 API (이미지 업로드 포함)
@posts.route("/post", methods=["POST"])
@jwt_required()
def create_post():
    """JWT 기반 인증 후 게시글 작성 (이미지 포함)"""
    user_id = int(get_jwt_identity())  
    title = request.form.get("title")
    content = request.form.get("content")
    image = request.files.get("image") 

    if not title or not content:
        return jsonify({"error": "제목과 내용을 입력해야 합니다."}), 400

    image_url = None
    if image:
        # ✅ 이미지 파일 이름 변환
        filename = secure_filename(image.filename)
        file_path = f"posts/{user_id}_{datetime.datetime.utcnow().timestamp()}_{filename}"

        # ✅ Supabase Storage에 이미지 업로드
        try:
            image_data = image.read()
            supabase.storage.from_(SUPABASE_BUCKET_NAME).upload(file_path, image_data)
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET_NAME}/{file_path}"
        except Exception as e:
            return jsonify({"error": f"이미지 업로드 실패: {str(e)}"}), 500

    # ✅ 게시글 저장
    new_post = Post(title=title, content=content, image_url=image_url, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "게시글이 생성되었습니다!", "image_url": image_url})


# ✅ 게시글 목록 조회 API
@posts.route("/posts", methods=["GET"])
def get_posts():
    """모든 게시글 조회"""
    posts = Post.query.all()
    return jsonify([
        {"id": p.id, "title": p.title, "content": p.content, "image_url": p.image_url, "created_at": p.created_at, "author": p.user.name}
        for p in posts
    ])



# ✅ 특정 게시글 조회
@posts.route("/post/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """특정 게시글 조회"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404
    return jsonify({"id": post.id, "title": post.title, "content": post.content, "author": post.user.name})


# ✅ 게시글 삭제 (JWT 필요)
@posts.route("/post/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    """게시글 삭제 (본인만 가능)"""
    user_id = int(get_jwt_identity())  # JWT에서 사용자 ID 가져오기
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    if post.user_id != user_id:
        return jsonify({"error": "게시글 삭제 권한이 없습니다."}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "게시글이 삭제되었습니다."})
