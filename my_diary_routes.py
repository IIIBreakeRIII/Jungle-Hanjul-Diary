import re

from flask import request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from db import db
from bson import ObjectId
from datetime import datetime, UTC, timezone, timedelta

from auth_routes import handle_token_validation

def register_my_diary_routes(app):

  # 내가 작성한 일기 리스트 조회
  @app.route('/diaries/me', methods=['GET'])
  @handle_token_validation
  def show_my_diaries_page():
    # 현재 로그인한 사용자 정보를 쿠키의 토큰에서 가져오기
    user_id = get_jwt_identity()

    # 로그인한 유저가 작성한 일기만 조회
    my_diaries = list(db.diaries.find({"user_id": user_id}))

    for diary in my_diaries:
      diary['_id'] = str(diary['_id'])
      if isinstance(diary['created_at'], str):
        diary['created_at'] = datetime.fromisoformat(diary['created_at'].replace('Z', '+00:00'))
        kr_time = diary['created_at'].astimezone(timezone(timedelta(hours=9)))
        diary['created_at'] = kr_time.strftime('%Y-%m-%d %H:%M:%S')
      else:
        diary['created_at'] = diary['created_at'].replace(tzinfo=UTC).astimezone(
          timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('menu-myDiary.html', my_diaries=my_diaries)

  # 내가 작성한 일기 검색
  @app.route('/api/diary/search', methods=['GET'])
  @handle_token_validation
  def search_diary():
    user_id = get_jwt_identity()
    keyword = request.args.get('keyword', '')

    if not keyword:
      return redirect(url_for('show_my_diaries_page'))

    try:
      # 특수문자를 이스케이프 처리
      escaped_keyword = re.escape(keyword)

      diaries = list(db.diaries.find({
        "user_id": user_id,
        "content": {"$regex": escaped_keyword, "$options": "i"}
      }))

      for diary in diaries:
        diary['_id'] = str(diary['_id'])

      return render_template('menu-myDiary.html', my_diaries=diaries)

    except Exception as e:
      # 검색 실패 시 ,빈 결과로 페이지 렌더링
      return render_template('menu-myDiary.html', my_diaries=[])

  # 내가 작성한 일기 상세 조회
  @app.route('/diary/me/<diary_id>', methods=['GET'])
  @handle_token_validation
  def edit_diary(diary_id):
    user_id = get_jwt_identity()
    diary = db.diaries.find_one({'_id': ObjectId(diary_id)})
    diary['_id'] = str(diary['_id'])

    # 일기에 달린 댓글도 조회
    comments = list(db.comments.find({'diary_id': diary['_id']}))

    # comments 안의 각 comment 마다 user_id 와 작성자 id 가 동일한지 체크하기
    if not comments:
      return render_template('myDiary-edit.html', diary=diary, comments=[])

    for comment in comments:
      comment['_id'] = str(comment['_id'])
      comment['created_at'] = comment['created_at'].replace(tzinfo=UTC).astimezone(
        timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')
      if comment['user_id'] == user_id:
        comment['is_mine'] = True
      else:
        comment['is_mine'] = False

    return render_template('myDiary-edit.html', diary=diary, comments=comments)

  # 내 일기 수정 API
  @app.route('/api/diary/<diary_id>/update', methods=['PUT'])
  @handle_token_validation
  def update_diary(diary_id):
    data = request.json
    content_to_update = data.get('content')
    is_private = data.get('is_private')

    try:
      result = db.diaries.update_one(
        {'_id': ObjectId(diary_id)},
        {'$set': {
          'content': content_to_update,
          'is_private': is_private
        }}
      )

      if result.matched_count == 0:
        return jsonify({"message": "해당 일기를 찾을 수 없습니다."}), 404
      elif result.modified_count == 0:
        return jsonify({"message": "일기가 수정되었습니다. (내용이 이전과 동일합니다.)",})
      else:
        return jsonify({"message": "일기가 수정되었습니다."})

    except Exception as e:
      return jsonify({"message": "일기 수정 요청 중 오류가 발생했습니다."}), 500

  # 내가 작성한 일기 삭제 API
  @app.route('/api/diary/<diary_id>/delete', methods=['DELETE'])  # 기존 DELETE를 사용했으나 교체
  @handle_token_validation
  def delete_diary(diary_id):
    result = db.diaries.delete_one({'_id': ObjectId(diary_id)})

    return jsonify({"message": "일기가 삭제되었습니다."})