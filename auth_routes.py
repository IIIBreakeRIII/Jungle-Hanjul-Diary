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
  

  """
  아래의 코드는 FE 마이그레이션용 임시 코드입니다!
  BE 개발을 진행할 시에 삭제하여 사용하면 됩니다.

  함수 이름의 시작이 temp_ 인 경우, FE에서 만든 임시 코드입니다.
  """

  @app.route('/menu-main', methods=['GET'])
  def temp_menu_main_render():
    return render_template('menu-main.html')

  @app.route('/menu-writeDiary', methods=['GET'])
  def temp_menu_writeDiary():
    return render_template('menu-writeDiary.html')
