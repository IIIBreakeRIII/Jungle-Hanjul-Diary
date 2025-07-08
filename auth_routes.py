from flask import request, jsonify, render_template, url_for, render_template_string
from db import db

from flask_jwt_extended import (
  JWTManager,
  create_access_token,
  set_access_cookies,
  unset_jwt_cookies,
  jwt_required,
  get_jwt_identity,
  verify_jwt_in_request
)


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
    data = request.get_json()
    user_id = data.get("userId")
    user_password = data.get("userPw")

    # users 컬렉션에 해당 유저가 존재하는지 확인하기
    user = db.users.find_one({"user_id": user_id})

    # 입력한 정보에 해당하는 유저가 없다면, 사용자에게 안내 메시지 보내기
    if not user or user["password"] != user_password:
      return jsonify({"message": "아이디 또는 비밀번호가 틀렸습니다."}), 401

    # 입력한 정보에 해당하는 유저가 있다면 JWT 토큰을 발급하기
    access_token = create_access_token(identity=user_id)

    # 리다이렉션 URL 설정
    redirect_url = url_for('signup')

    # 응답 객체 생성
    response = jsonify({
      "message": "로그인에 성공하였습니다.",
      "redirect": redirect_url,
    })

    # 토큰을 쿠키에 저장하기
    set_access_cookies(response, access_token)

    # CORS 관련 헤더 추가
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response, 200

