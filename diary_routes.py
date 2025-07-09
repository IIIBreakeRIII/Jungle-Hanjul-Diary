from flask import request, jsonify, render_template, redirect, url_for
from db import db
from bson import ObjectId
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import datetime, UTC
from auth_routes import handle_token_validation


# 일기 관련 코드 작성
def register_diary_routes(app):
  # 메인 페이지
  @app.route('/diary/main', methods=['GET'])
  @handle_token_validation
  def show_main_page():
      return render_template('menu-main.html')
  
  # 일기 작성 페이지
  @app.route('/diary/write', methods=['GET'])
  @handle_token_validation
  def show_write_page():
      return render_template('menu-writeDiary.html')
    
  # 일기 저장 API
  @app.route('/api/diary/create', methods=['POST'])
  @handle_token_validation
  def create_diary():
    try:
      data = request.json
      content = data.get("content")
      is_private = data.get("isPrivate")
      user_id = get_jwt_identity()
      created_at = datetime.now(UTC)

      diary = {
          "content": content,
          "is_private": is_private,
          "user_id": user_id,
          "created_at": created_at
      }

      db.diaries.insert_one(diary)

      return jsonify({'message': '일기가 저장되었습니다.'})
    except Exception as e:
      return jsonify({'message': '일기 저장 중 오류가 발생했습니다.'})


  @app.route('/diary/<diary_id>', methods=['GET'])
  @handle_token_validation
  def show_diary(diary_id):
    try:
      user_id = get_jwt_identity()  # 로그인한 사용자
      diary = db.diaries.find_one({'_id': ObjectId(diary_id)})
      diary['_id'] = str(diary['_id'])
      comments = list(db.comments.find({'diary_id': diary['_id']}))

      if not comments:
        return render_template('menu-viewDiary.html', diary=diary, comments=[])

      for comment in comments:
        comment['_id'] = str(comment['_id'])
        if comment['user_id'] == user_id:
            comment['is_mine'] = True
        else:
            comment['is_mine'] = False

      return render_template('menu-viewDiary.html', diary=diary, comments=comments)

    except Exception as e:
        return render_template('menu-viewDiary.html', diary=None, comments=[])

  # 랜덤 일기 보기 조회
  @app.route('/diary/random', methods=['GET'])
  @handle_token_validation
  def get_random_diary():
    try:
      user_id = get_jwt_identity() # 로그인한 사용자

      random_diaries = list(db.diaries.aggregate([
          {"$match": {"is_private": False}},
          { '$sample': { 'size': 1 } }
          ]))

      if not random_diaries:
          return render_template('menu-randomDiary.html', diary=None, message="공개된 일기가 없습니다.")

      diary = random_diaries[0]
      diary['_id'] = str(diary['_id'])

      comments = list(db.comments.find({'diary_id': diary['_id']}))

      # comments 안의 각 comment 마다 user_id 와 작성자 id 가 동일한지 체크하기
      if not comments:
          return render_template('menu-randomDiary.html', diary=diary, comments=[])

      for comment in comments:
        comment['_id'] = str(comment['_id'])
        if comment['user_id'] == user_id:
            comment['is_mine'] = True
        else:
            comment['is_mine'] = False

      return render_template('menu-randomDiary.html', diary=diary, comments=comments)
    except Exception as e:
      return render_template('menu-randomDiary.html', diary=None, comments=[])

  # 일기 좋아요 기능 구현
  @app.route('/api/diary/<diary_id>/like', methods=['POST'])
  @handle_token_validation
  def like_diary(diary_id):
    try:
      user_id = get_jwt_identity()
      diary = db.diaries.find_one({'_id': ObjectId(diary_id)})
      if not diary:
          return jsonify({'message': '일기를 찾을 수 없습니다.'}), 404

      liked_users = diary.get('liked_users', [])
      if user_id in liked_users:
        return jsonify({'message': '이미 좋아요를 누르셨습니다.', 'like_count': diary.get('like_count', 0)}), 400

      # 좋아요 반영
      new_like_count = diary.get('like_count', 0) + 1
      db.diaries.update_one(
          {'_id': ObjectId(diary_id)},
          {
              '$set': {'like_count': new_like_count},
              '$push': {'liked_users': user_id}
          }
      )
      return jsonify({'message': '좋아요가 반영되었습니다.', 'like_count': new_like_count})
    except Exception as e:
      return jsonify({'message': '좋아요 처리 중 오류가 발생했습니다.'}), 500
    

  @app.route('/diary/accountinfo', methods=['GET'])
  @handle_token_validation
  def show_account_info():
    user_id = get_jwt_identity()
    user = db.users.find_one({'user_id': user_id})

    return render_template('menu-account.html', user=user)
