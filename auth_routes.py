from flask import request, jsonify, render_template
from db import db

# 사용자 인증 관련 코드 작성 (예시)
def register_auth_routes(app):
  @app.route('/signup', methods=['POST'])
  def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # MongoDB에 유저 정보 추가
    db.users.insert_one({"email": email, "password": password})
    return jsonify({"message": "회원가입 성공"})
  
  @app.route('/signup', methods=['GET'])
  def signup_form():
    return render_template('signup.html')

  @app.route('/login', methods=['POST'])
  def login():
    # 예시 로그인 로직
    return jsonify({"message": "로그인 성공"})

