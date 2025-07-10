from flask import request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from db import db
from bson import ObjectId
from datetime import datetime, UTC

from auth_routes import handle_token_validation


def register_comments_routes(app):
  # 댓글 작성
  @app.route('/diary/<diary_id>/comments', methods=['POST'])
  @handle_token_validation
  def create_comment(diary_id):
    try:
      # TODO : try~except 로 수정할 것
      data = request.json
      new_comment = data.get("comment")
      user_id = get_jwt_identity()
      created_at = datetime.now(UTC)

      comment = {
        "diary_id": diary_id,
        "user_id": user_id,
        "comment": new_comment,
        "created_at": created_at
      }

      db.comments.insert_one(comment)

      return jsonify({
        "message": "댓글 작성에 성공했습니다.",
        "redirect": url_for('show_diary', diary_id=diary_id)
      })
    except Exception as e:
      return jsonify({
        "message": "댓글 작성 중 오류가 발생했습니다."
      }), 500

  # 댓글 수정
  @app.route('/diary/<diary_id>/comments/<comment_id>', methods=['PUT'])
  @handle_token_validation
  def update_diary_comment(diary_id, comment_id):
    data = request.json
    comment_to_update = data.get('comment')

    result = db.comments.update_one(
      {'_id': ObjectId(comment_id)},
      {'$set': {'comment': comment_to_update}}
    )

    if result.matched_count == 0:
      return jsonify({"message": "해당 댓글을 찾을 수 없습니다."}), 404
    elif result.modified_count == 0:
      return jsonify({
        "message": "댓글 수정이 완료되었습니다. (내용이 이전과 동일합니다.)",
        "redirect": url_for('show_diary', diary_id=diary_id)
      })
    else:
      return jsonify({
        "message": "댓글 수정이 완료되었습니다.",
        "redirect": url_for('show_diary', diary_id=diary_id)
      })

  # 댓글 삭제
  @app.route('/diary/<diary_id>/comments/<comment_id>', methods=['DELETE'])
  @handle_token_validation
  def delete_diary_comment(diary_id, comment_id):
    result = db.comments.delete_one({'_id': ObjectId(comment_id)})
    return jsonify({
      "message": "댓글 삭제에 성공했습니다.",
      "redirect": url_for('show_diary', diary_id=diary_id)
    })

  # [내가 쓴 일기] 의 댓글 수정
  @app.route('/diary/me/<diary_id>/comments/<comment_id>', methods=['PUT'])
  @handle_token_validation
  def update_my_diary_comment(diary_id, comment_id):
    data = request.json
    comment_to_update = data.get('comment')

    result = db.comments.update_one(
      {'_id': ObjectId(comment_id)},
      {'$set': {'comment': comment_to_update}}
    )

    if result.matched_count == 0:
      return jsonify({"message": "해당 댓글을 찾을 수 없습니다."}), 404
    elif result.modified_count == 0:
      return jsonify({
        "message": "댓글 수정이 완료되었습니다. (내용이 이전과 동일합니다.)",
        "redirect": url_for('edit_diary', diary_id=diary_id)
      })
    else:
      return jsonify({
        "message": "댓글 수정이 완료되었습니다.",
        "redirect": url_for('edit_diary', diary_id=diary_id)
      })

  # [내가 쓴 일기] 의 댓글 삭제
  @app.route('/diary/me/<diary_id>/comments/<comment_id>', methods=['DELETE'])
  @handle_token_validation
  def delete_my_diary_comment(diary_id, comment_id):
    result = db.comments.delete_one({'_id': ObjectId(comment_id)})
    return jsonify({
      "message": "댓글 삭제에 성공했습니다.",
      "redirect": url_for('edit_diary', diary_id=diary_id)
    })