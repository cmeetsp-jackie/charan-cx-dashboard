"""
CX 대시보드 Flask 서버
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
from channeltalk_api import ChannelTalkAPI

app = Flask(__name__)
CORS(app)

# 채널톡 API 초기화
CHANNELTALK_TOKEN = os.environ.get("CHANNELTALK_TOKEN")
if not CHANNELTALK_TOKEN:
    print("⚠️ CHANNELTALK_TOKEN 환경변수가 없습니다")
    api = None
else:
    api = ChannelTalkAPI(CHANNELTALK_TOKEN)

@app.route('/')
def index():
    """대시보드 메인 페이지"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """통계 데이터 API"""
    if not api:
        # API 토큰 없으면 데모 데이터 생성
        demo_api = ChannelTalkAPI(None)
        stats = demo_api._generate_demo_data()
        return jsonify(stats)
    
    stats = api.get_dashboard_stats()
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 CX 대시보드 서버 시작...")
    print("📊 브라우저에서 http://localhost:3000 접속하세요")
    app.run(host='127.0.0.1', port=3000, debug=False)
