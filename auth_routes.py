from flask import (
  request, jsonify, render_template, url_for,
  render_template_string, make_response, redirect )
from db import db

from flask_jwt_extended import (
  JWTManager,
  create_access_token,
  create_refresh_token,
  set_access_cookies,
  set_refresh_cookies,
  unset_jwt_cookies,
  jwt_required,
  get_jwt_identity,
  verify_jwt_in_request,
)
from jwt.exceptions import ExpiredSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError

from datetime import datetime, UTC
from functools import wraps

# 토큰 관련 데코레이터 : 로그인이 필요한 기능들에 대해 인증 관련 로직들이 동작한다.
def handle_token_validation(view_func):
  @wraps(view_func)
  def wrapped(*args, **kwargs):
    try:
      verify_jwt_in_request()
      return view_func(*args, **kwargs)

    except ExpiredSignatureError as e:
      # 액세스 토큰이 만료된 경우 -> 리프레시 토큰으로 액세스 토큰 재발급 시도
      print("JWT Exception ExpiredSignatureError:", type(e), str(e))
      try:
        print('@@@ 데코레이터 @@@ 만료된 액세스 토큰 갱신 중...')
        verify_jwt_in_request(refresh=True)
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        response = make_response(view_func(*args, **kwargs))
        set_access_cookies(response, access_token)
        return response

      except Exception as e:
        print("JWT Exception after ExpiredSignatureError:", type(e), str(e))
        # 리프레시 토큰도 만료된 경우 -> 다시 로그인 요청하기
        return _handle_session_expired()

    except NoAuthorizationError:
      # 액세스 토큰이 아예 없는 경우에도 리프레시로 재발급 시도
      print('데코레이션 NoAuthorizationError: 액세스 토큰이 없어서 리프레시 토큰으로 재발급 시도')
      try:
        verify_jwt_in_request(refresh=True)
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        response = make_response(view_func(*args, **kwargs))
        set_access_cookies(response, access_token)
        return response

      except Exception as e:
        print("JWT Exception after NoAuthorizationError:", type(e), str(e))
        # 리프레시 토큰도 없다면 NoAuthorizationError 발생: Missing cookie "refresh_token_cookie"
        return _handle_not_logged_in()

    # 그 밖의 에러 메시지
    except Exception as e:
      print("JWT Exception:", type(e), str(e))

  return wrapped

# 토큰 예외 관련 메시지 처리 함수
def _handle_session_expired():
  preferred = request.accept_mimetypes.best_match(["application/json", "text/html"])

  if request.is_json or preferred == "application/json":
    response = jsonify({
      "msg": "세션이 만료되었습니다. 다시 로그인해주세요.",
      "code": "TOKEN_EXPIRED"
    }), 401
    unset_jwt_cookies(response[0])
    return response
  else:
    response = make_response(render_template_string(
      """
      <script>
        alert("세션이 만료되었습니다. 다시 로그인해주세요.");
        window.location.href = "/";
      </script>
      """
    ))
    unset_jwt_cookies(response)
    return response

def _handle_not_logged_in():
  preferred = request.accept_mimetypes.best_match(["application/json", "text/html"])

  if request.is_json or preferred == "application/json":
    response = jsonify({
      "msg": "로그인이 필요한 서비스입니다.",
      "code": "NOT_LOGGED_IN"
    }), 401
    unset_jwt_cookies(response[0])
    return response
  else:
    response = make_response(render_template_string(
      """
      <script>
        alert("로그인이 필요한 서비스입니다.");
        window.location.href = "/";
      </script>
      """
    ))
    unset_jwt_cookies(response)
    return response


# 사용자 인증 관련 코드 작성
def register_auth_routes(app):
  @app.route('/signup', methods=['GET'])
  def signup_form():
    return render_template('signup.html')

  @app.route('/api/signup', methods=['POST'])
  def signup():
    try:
      data = request.json
      user_name = data.get("userName")
      user_id = data.get("userId")
      user_pw = data.get("userPw")

      # 기존 사용자 확인 (아이디 중복 체크)
      existing_user = db.users.find_one({"user_id": user_id})
      if existing_user:
        return jsonify({"message": "이미 존재하는 아이디입니다."}), 409

      # MongoDB에 유저 정보 추가
      result = db.users.insert_one({
        "user_name": user_name,
        "user_id": user_id,
        "user_pw": user_pw,
        "created_at": datetime.now(UTC)
      })

      if not result.inserted_id:
        return jsonify({"message": "데이터베이스 저장에 실패했습니다."}), 500

      # 리다이렉션 URL 설정
      redirect_url = url_for('home')

      # 응답 객체 생성
      response = jsonify({
        "message": "회원가입에 성공하였습니다.",
        "redirect": redirect_url,
        "userId": user_id
      })

      return response, 201

    except Exception as e:
      return jsonify({"message": "회원가입 처리 중 오류가 발생했습니다."}), 500


  @app.route('/api/login', methods=['POST'])
  def login():
    data = request.get_json()
    user_id = data.get("userId")
    user_password = data.get("userPw")

    # users 컬렉션에 해당 유저가 존재하는지 확인하기
    user = db.users.find_one({"user_id": user_id})

    # 입력한 정보에 해당하는 유저가 없다면, 사용자에게 안내 메시지 보내기
    if not user or user["user_pw"] != user_password:
      return jsonify({"message": "아이디 또는 비밀번호가 틀렸습니다."}), 401

    # 입력한 정보에 해당하는 유저가 있다면 JWT 토큰을 발급하기
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)

    # 리다이렉션 URL 설정
    redirect_url = url_for('show_main_page')

    # 응답 객체 생성
    response = jsonify({
      "message": "로그인에 성공하였습니다.",
      "redirect": redirect_url,
    })

    # 토큰을 쿠키에 저장하기
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    # CORS 관련 헤더 추가
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response, 200


  @app.route('/api/logout', methods=['POST'])
  def logout():
    response = redirect(url_for('home'))

    # 쿠키에서 액세스 토큰 & 리프레시 토큰을 모두 제거
    unset_jwt_cookies(response)
    return response