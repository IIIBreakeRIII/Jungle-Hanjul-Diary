from flask import request, jsonify
from db import db

# 일기 관련 코드 작성 (예시)
def register_diary_routes(app):
    @app.route('/diary', methods=['POST'])
    def create_diary():
        data = request.json
        content = data.get("content")

        db.diaries.insert_one({"content": content})
        return jsonify({"message": "일기 저장 완료"})

    @app.route('/diary', methods=['GET'])
    def get_diaries():
        # diaries = list(db.diaries.find())
        return jsonify({"data": "다이어리 전체 목록"})
