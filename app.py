from flask import Flask, render_template
from auth_routes import register_auth_routes
from diary_routes import register_diary_routes

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

# 각각 라우트 등록
register_auth_routes(app)
register_diary_routes(app)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5001, debug=True)