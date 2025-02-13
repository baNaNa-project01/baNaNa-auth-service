import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, Post, User

comments = Blueprint("comments", __name__)

# ✅ 1️⃣ 댓글 작성 API
@comments.route("/post/<int:post_id>/comment", methods=["POST"])
@jwt_required()
def create_comment(post_id):
    """특정 게시물에 댓글 작성"""
    user_id = int(get_jwt_identity())
    content = request.json.get("content")

    if not content:
        return jsonify({"error": "댓글 내용을 입력하세요."}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    new_comment = Comment(post_id=post_id, user_id=user_id, content=content)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "댓글이 추가되었습니다!"})

# ✅ 2️⃣ 특정 게시물의 댓글 목록 조회 API
@comments.route("/post/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    """특정 게시물의 댓글 조회"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([
        {
            "id": c.id,
            "content": c.content,
            "author": c.user.name,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for c in comments
    ])

# ✅ 3️⃣ 댓글 삭제 API (본인만 가능)
@comments.route("/comment/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    """댓글 삭제"""
    user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"error": "댓글을 찾을 수 없습니다."}), 404

    if comment.user_id != user_id:
        return jsonify({"error": "댓글 삭제 권한이 없습니다."}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "댓글이 삭제되었습니다!"})
