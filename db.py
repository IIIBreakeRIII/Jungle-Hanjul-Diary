from pymongo import MongoClient
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 접속 정보 읽기
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

# MongoDB 연결 코드
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

