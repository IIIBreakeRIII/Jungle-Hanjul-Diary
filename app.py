from flask import Flask, render_template, jsonify
from auth_routes import register_auth_routes
from diary_routes import register_diary_routes

import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from datetime import timedelta

load_dotenv()

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# JWT 토큰을 어디서 가져올 것인가? -> 쿠키에서만 읽겠다
app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# JWT 쿠키를 HTTPS(보안 연결)일 때만 전송할 것인가? -> 아니오
app.config['JWT_COOKIE_SECURE'] = False

# JWT 쿠키 사용 시, CSRF 토큰도 함께 검증할 것인가? -> 아니오
# CSRF (Cross Site Request Forgery) 공격
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# JWT 액세스 토큰의 유효시간 설정 : 테스트를 위해 짧게 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=300)

# 확장 모듈 초기화
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# ✅ JWT 예외 처리 핸들러들을 JSON 응답으로 수정
@jwt.unauthorized_loader
def handle_missing_token(reason):
    return jsonify({"msg": "로그인이 필요합니다."}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "토큰이 만료되었습니다."}), 401

@jwt.invalid_token_loader
def handle_invalid_token(reason):
    return jsonify({"msg": "토큰이 유효하지 않습니다."}), 401

# 각각 라우트 등록
register_auth_routes(app)
register_diary_routes(app)


@app.route("/")
def home():
    return render_template('index.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)