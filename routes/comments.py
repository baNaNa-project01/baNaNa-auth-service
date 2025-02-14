import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, Post, User

comments = Blueprint("comments", __name__)

# ✅ 1️⃣ 댓글 작성 API
@comments.route("/post/<int:post_id>/comment", methods=["POST"])
@jwt_required()
def create_comment(post_id):
    """
    특정 게시물에 댓글 작성
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
        description: 댓글을 작성할 게시물의 ID
      - in: body
        name: body
        required: true
        description: 댓글 작성에 필요한 데이터
        schema:
          type: object
          required:
            - content
          properties:
            content:
              type: string
              description: 댓글 내용
    responses:
      200:
        description: 댓글 작성 성공
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: 댓글 내용이 누락된 경우
      404:
        description: 게시글을 찾을 수 없음
    """
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
    """
    특정 게시물의 댓글 조회
    ---
    tags:
      - Comments
    parameters:
      - in: path
        name: post_id
        type: integer
        required: true
        description: 조회할 게시물의 ID
    responses:
      200:
        description: 댓글 목록 조회 성공
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              content:
                type: string
              author:
                type: string
              created_at:
                type: string
                description: 댓글 작성 시간 (YYYY-MM-DD HH:MM:SS)
      404:
        description: 게시글을 찾을 수 없음
    """
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
    """
    댓글 삭제 (본인만 가능)
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: comment_id
        type: integer
        required: true
        description: 삭제할 댓글의 ID
    responses:
      200:
        description: 댓글 삭제 성공
        schema:
          type: object
          properties:
            message:
              type: string
      403:
        description: 댓글 삭제 권한이 없음
      404:
        description: 댓글을 찾을 수 없음
    """
    user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"error": "댓글을 찾을 수 없습니다."}), 404

    if comment.user_id != user_id:
        return jsonify({"error": "댓글 삭제 권한이 없습니다."}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "댓글이 삭제되었습니다!"})
