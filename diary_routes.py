from flask import request, jsonify, render_template, redirect
from db import db
from bson import ObjectId
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import datetime

# 일기 관련 코드 작성 


def register_diary_routes(app):

    # 메인 페이지
    @app.route('/diary/main', methods=['GET'])
    def show_main_page():
        return render_template('menu-main.html')
    

############################################################

    #글쓰기 페이지
    @app.route('/diary/write', methods=['GET'])
    def show_write_page():
        return render_template('menu-writeDiary.html')
    
    # 일기 작성
    @app.route('/diary', methods=['POST'])
    def create_diary():
        data = request.json
        content = data.get("content")
        diary_id = data.get("diary_id")
        name = data.get("name")
        is_public = data.get("is_public", False)

        diary = {
            "diary_id": diary_id, # 일기 작성자 user ID
            "name": name,
            "content": content,
            "is_public": is_public
        }
        db.diaries.insert_one(diary)
        #return jsonify({"message": "일기 저장 완료"})
        return render_template('menu-main.html', message="일기 저장 완료")
    
############################################################
    
    # 랜덤 일기 보기 페이지(랜덤 일기 조회)
    @app.route('/diary/random', methods=['GET'])
    def get_random_diary():
        random_diaries = list(db.diaries.aggregate([
            {"$match": {"is_public": True}},
            { '$sample': { 'size': 1 } }
            ]))
        if not random_diaries:
            return render_template('menu-randomDiary.html', diary=None, message="공개된 일기가 없습니다.")
        diary = random_diaries[0]
        for diary in random_diaries:
            diary['_id'] = str(diary['_id'])
        return render_template('menu-randomDiary.html', diary=diary)
    
    # 댓글 작성(상대방의 일기에 댓글 작성)
    @app.route('/diary/<post_id>/comments', methods=['POST'])
    def create_comment(post_id): #post_id는 일기 "_id"
        data = request.json
        name = data.get("name")  
        new_comment = data.get("comment")
        diary_id = data.get("diary_id")  # 댓글 작성자 ID
        comment = {
            "post_id": post_id,  # 일기 "_id"
            "diary_id": diary_id,
            "name": name,
            "comment": new_comment
        }
        db.comments.insert_one(comment)
        #return jsonify({"message": "댓글 작성 완료"})
        return render_template('menu-randomDiary.html', message="댓글 작성 완료")

    # 댓글 목록 조회(3개만)
    @app.route('/diary/<post_id>/comments/random', methods=['GET'])
    def get_comments(post_id):
        diary = db.diaries.find_one({'_id': ObjectId(post_id)})
        if not diary:
            return render_template('menu-randomDiary.html', diary=None, message="일기를 찾을 수 없습니다.")
        diary['_id'] = str(diary['_id'])

        comments = list(db.comments.aggregate([
            {"$match": {"post_id": post_id}},
            { "$sample": { "size": 3 }}
            ]))
        for comment in comments:
            comment['_id'] = str(comment['_id'])

            
        return render_template('menu-randomDiary.html', diary=diary, comments=comments)

    # # 댓글 목록 조회(전체)
    # @app.route('/diary/<post_id>/comments', methods=['GET'])
    # def get_comments(post_id):
    #     comments = list(db.comments.aggregate([ {"$match": {"post_id": post_id}} ]))
    #     for comment in comments:
    #         comment['_id'] = str(comment['_id'])
    #     return jsonify({'comments': comments})
    
    
    



############################################################

    # 내가 쓴 글 페이지
    @app.route('/diary/my', methods=['GET'])
    def show_my_diaries_page():
        return render_template('menu-myDiary.html')

    # 내가 쓴 글 페이지(내가 작성한 일기 목록 조회)
    @app.route('/diary', methods=['GET'])
    def get_my_diaries():
        diary_id = request.args.get('diary_id') 
        diaries = list(db.diaries.find({"diary_id": diary_id}))
        for diary in diaries:
            diary['_id'] = str(diary['_id'])
        #return jsonify({"data": diaries})
        return render_template('menu-myDiary.html', diaries=diaries)
    
    # 내가 작성한 일기 검색
    @app.route('/diary/search', methods=['GET'])
    def search_diary():
        diary_id = request.args.get('diary_id')
        keyword = request.args.get('keyword')

        diaries = list(db.diaries.find({
            "diary_id": diary_id,
            "content": { "$regex": keyword, "$options": "i"}
        }))
        for diary in diaries:
            diary['_id'] = str(diary['_id'])
        #return jsonify({"data": diaries})
        return render_template('menu-myDiary.html', diaries=diaries)
    
############################################################

    # 내가 쓴 글 페이지(내가 작성한 일기 상세 조회)
    @app.route('/diary/<diary_id>', methods=['GET'])
    def edit_diary(diary_id):
        diary = db.diaries.find_one({'_id': ObjectId(diary_id)})
        diary['_id'] = str(diary['_id'])
        return render_template('myDiary-edit.html', diary=diary)
    
    # 내가 작성한 일기 수정(내가 작성한 것만 나온다.)
    #@app.route('/diary/<diary_id>', methods=['PUT'])
    @app.route('/diary/<diary_id>/update', methods=['POST']) # 기존 PUT을 POST로 교체 
    #@jwt_required()
    def update_diary(diary_id):
        #user_id = get_jwt_identity()
        data = request.json
        content_receive = data.get('content')
        result = db.diaries.update_one(
            {'_id': ObjectId(diary_id)},
            {'$set': {'content': content_receive}}
        )
        # if result.modified_count == 1:
        #     return jsonify({"message": "수정 완료"})
        # else:
        #     return jsonify({"message": "수정 실패"})
        return render_template('myDiary-edit.html', message="일기 수정 완료")
        
    # 내가 작성한 일기 삭제
    #@app.route('/diary/<diary_id>', methods=['DELETE'])
    @app.route('/diary/<diary_id/delete>', methods=['POST']) # 기존 DELETE를 사용했으나 교체
    def delete_diary(diary_id):
        result = db.diaries.delete_one({'_id': ObjectId(diary_id)})
        # return jsonify({"message": "일기 삭제 완료"})
        return render_template('myDiary-edit.html', message="일기 삭제 완료")
    
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
    
#     # 일기 좋아요
#     @app.route('/memo/like', methods=['POST'])
#     def like_memo():
#         id_receive = request.form['id_give']
#         memo = db.memos.find_one({'_id': ObjectId(id_receive)})
#         new_likes = memo['likes'] + 1
#         result = db.memos.update_one({'_id': ObjectId(id_receive)}, {'$set': {'likes': new_likes}})
#         if result.modified_count == 1:
#             return jsonify({'result': 'success'})
#         else:
#             return jsonify({'result': 'failure'})
        
#     #일기 좋아요 취소
#     @app.route('/memo/unlike', methods=['POST'])
