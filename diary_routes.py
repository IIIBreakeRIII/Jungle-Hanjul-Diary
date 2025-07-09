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
    
    # 일기 작성 API
    @app.route('/api/diary/create', methods=['POST'])
    @handle_token_validation
    def create_diary():
        try:
            data = request.json
            content = data.get("content")
            is_private = data.get("isPrivate")
            user_id = get_jwt_identity()
            created_at = datetime.now(UTC)

            print(content, is_private, user_id)

            diary = {
                "content": content,
                "is_private": is_private,
                "user_id": user_id,
                "created_at": created_at
            }

            db.diaries.insert_one(diary)

            return jsonify({
                'message': '일기가 저장되었습니다.'
            });

        except Exception as e:
            return jsonify({
                'message': '일기 저장 중 오류가 발생했습니다.',
            })
    
    # 랜덤 일기 보기 페이지(랜덤 일기 조회)
    @app.route('/diary/random', methods=['GET'])
    @handle_token_validation
    def get_random_diary():
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
        for comment in comments:
            if comment['user_id'] == user_id:
                comment['is_mine'] = True

        print(comments)

        return render_template('menu-randomDiary.html', diary=diary, comments=comments)
    
    # 댓글 작성(상대방의 일기에 댓글 작성)
    @app.route('/diary/<diary_id>/comments', methods=['POST'])
    @handle_token_validation
    def create_comment(diary_id):
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

        print(comment)

        db.comments.insert_one(comment)

        return jsonify({"message": "댓글 작성에 성공했습니다."})


############################################################

    # 내가 쓴 글 페이지
    @app.route('/diaries/me', methods=['GET'])
    @handle_token_validation
    def show_my_diaries_page():
        # 현재 로그인한 사용자 정보를 쿠키의 토큰에서 가져오기
        user_id = get_jwt_identity()

        # 로그인한 유저가 작성한 일기만 조회
        my_diaries = list(db.diaries.find({"user_id": user_id}))

        for diary in my_diaries:
            diary['_id'] = str(diary['_id'])

        return render_template('menu-myDiary.html',my_diaries=my_diaries)
    
    # 내가 작성한 일기 검색
    @app.route('/api/diary/search', methods=['GET'])
    @handle_token_validation
    def search_diary():
        user_id = get_jwt_identity()
        keyword = request.args.get('keyword', '')

        print(user_id, keyword)

        if not keyword:
            return redirect(url_for('show_my_diaries_page'))

        diaries = list(db.diaries.find({
            "user_id": user_id,
            "content": {"$regex": keyword, "$options": "i"}
        }))

        for diary in diaries:
            diary['_id'] = str(diary['_id'])

        return render_template('menu-myDiary.html', my_diaries=diaries)


    # 내가 쓴 글 페이지 (내가 작성한 일기 상세 조회)
    @app.route('/diary/<diary_id>', methods=['GET'])
    def edit_diary(diary_id):
        diary = db.diaries.find_one({'_id': ObjectId(diary_id)})
        diary['_id'] = str(diary['_id'])

        return render_template('myDiary-edit.html', diary=diary)

    # 내 일기 수정 API
    @app.route('/api/diary/<diary_id>/update', methods=['PUT'])
    @handle_token_validation
    def update_diary(diary_id):
        user_id = get_jwt_identity()
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

            if result.modified_count == 1:
                return jsonify({"message": "일기가 수정되었습니다."})
            else:
                return jsonify({"message": "일기 수정에 실패했습니다."})

        except Exception as e:
            return jsonify({"message": "오류가 발생했습니다."}), 500

    # 내가 작성한 일기 삭제
    @app.route('/api/diary/<diary_id>/delete', methods=['DELETE']) # 기존 DELETE를 사용했으나 교체
    @handle_token_validation
    def delete_diary(diary_id):
        result = db.diaries.delete_one({'_id': ObjectId(diary_id)})

        return jsonify({
            "message": "일기가 삭제되었습니다."
        })
        # return render_template('myDiary-edit.html', message="일기 삭제 완료")
    
############################################################    
    



#    # 랜덤 일기에 대해 내가 작성한 댓글 수정
#     @app.route('/diary/<post_id>/comments', methods=['PUT'])
#     def update_diary(post_id):
#         data = request.json
#         comments_receive = data.get('comments')
#         result = db.diaries.update_one(
#             {'_id': ObjectId(diary_id)},
#             {'$set': {'content': comments_receive}}
#         )
#         if result.modified_count == 1:
#             return jsonify({"message": "수정 완료"})
#         else:
#             return jsonify({"message": "수정 실패"})
        
#     # 댓글 삭제
#     @app.route('/diary/<diary_id>', methods=['DELETE'])
#     def delete_diary(diary_id):
#         result = db.diaries.delete_one({'_id': ObjectId(diary_id)})
#         return jsonify({"message": "일기 삭제 완료"})
    
# 일기 좋아요


#일기 좋아요 취소

