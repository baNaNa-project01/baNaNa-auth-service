from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Post, User

# 🔹 Flask Blueprint 설정
posts = Blueprint("posts", __name__)

# ✅ 1️⃣ 게시글 작성 (JWT 필요)
@posts.route("/post", methods=["POST"])
@jwt_required()
def create_post():
    """JWT 기반 인증 후 게시글 작성"""
    data = request.json
    user_id = int(get_jwt_identity())  # 🔹 JWT에서 사용자 ID 가져오기

    new_post = Post(title=data["title"], content=data["content"], user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "게시글이 생성되었습니다!"})


# ✅ 2️⃣ 모든 게시글 조회 (로그인 필요 없음)
@posts.route("/posts", methods=["GET"])
def get_posts():
    """모든 게시글 조회"""
    posts = Post.query.all()
    return jsonify([
        {"id": p.id, "title": p.title, "content": p.content, "author": p.user.name}
        for p in posts
    ])


# ✅ 3️⃣ 특정 게시글 조회
@posts.route("/post/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """특정 게시글 조회"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404
    return jsonify({"id": post.id, "title": post.title, "content": post.content, "author": post.user.name})


# ✅ 4️⃣ 게시글 삭제 (JWT 필요)
@posts.route("/post/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    """게시글 삭제 (본인만 가능)"""
    user_id = int(get_jwt_identity())  # 🔹 JWT에서 사용자 ID 가져오기
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    if post.user_id != user_id:
        return jsonify({"error": "게시글 삭제 권한이 없습니다."}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "게시글이 삭제되었습니다."})
