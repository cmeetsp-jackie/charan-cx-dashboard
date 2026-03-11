"""
Vercel Serverless Function - 채널톡 통계 API
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from datetime import datetime
import random


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS 헤더
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # 채널톡 API 토큰 확인
        channeltalk_token = os.environ.get('CHANNELTALK_TOKEN')
        
        if channeltalk_token:
            # 실제 채널톡 API 호출
            stats = self.get_real_stats(channeltalk_token)
        else:
            # 데모 데이터
            stats = self.generate_demo_data()
        
        # JSON 응답
        self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_real_stats(self, access_token):
        """실제 채널톡 API 호출"""
        base_url = "https://api.channel.io/open/v5"
        headers = {
            "x-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        # 오늘 00:00부터
        today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        
        try:
            # 최근 대화 가져오기
            response = requests.get(
                f"{base_url}/user-chats",
                headers=headers,
                params={
                    "since": today_start,
                    "limit": 1000,
                    "sortOrder": "desc"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return self.generate_demo_data()
            
            data = response.json()
            user_chats = data.get('userChats', [])
            
            # 통계 계산
            total_today = len(user_chats)
            open_count = sum(1 for chat in user_chats if chat.get('state') == 'opened')
            closed_count = sum(1 for chat in user_chats if chat.get('state') == 'closed')
            
            # 시간대별 데이터
            hourly_data = [0] * 24
            for chat in user_chats:
                created_at = chat.get('createdAt', 0)
                hour = datetime.fromtimestamp(created_at / 1000).hour
                hourly_data[hour] += 1
            
            # 응답 시간 계산 (간단 버전)
            response_times = []
            for chat in user_chats[:50]:  # 최근 50개만
                messages = chat.get('messages', [])
                if len(messages) >= 2:
                    first_user_msg = next((m for m in messages if m.get('personType') == 'User'), None)
                    first_manager_msg = next((m for m in messages if m.get('personType') == 'Manager'), None)
                    
                    if first_user_msg and first_manager_msg:
                        diff = (first_manager_msg.get('createdAt', 0) - first_user_msg.get('createdAt', 0)) / 1000
                        if 0 < diff < 3600:  # 1시간 이내만
                            response_times.append(diff)
            
            avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0
            
            return {
                "total_today": total_today,
                "open": open_count,
                "closed": closed_count,
                "avg_response_time": avg_response_time,
                "hourly_data": hourly_data,
                "team_performance": self.get_team_performance(user_chats),
                "csat_score": 4.5  # TODO: 실제 CSAT API 호출
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return self.generate_demo_data()
    
    def get_team_performance(self, chats):
        """팀원별 성과 (간단 버전)"""
        managers = {}
        
        for chat in chats:
            assignee = chat.get('assignee')
            if assignee:
                name = assignee.get('name', '미지정')
                if name not in managers:
                    managers[name] = {"handled": 0, "total_time": 0, "count": 0}
                managers[name]["handled"] += 1
        
        team_list = []
        for name, data in list(managers.items())[:4]:  # 상위 4명
            team_list.append({
                "name": name,
                "handled": data["handled"],
                "avg_time": random.randint(180, 420)  # TODO: 실제 계산
            })
        
        return team_list if team_list else [
            {"name": "매니저1", "handled": 0, "avg_time": 0}
        ]
    
    def generate_demo_data(self):
        """데모 데이터 생성"""
        current_hour = datetime.now().hour
        
        hourly_pattern = [
            2, 1, 0, 0, 1, 2,
            5, 8, 12, 18, 22, 25,
            28, 30, 26, 24, 20, 18,
            15, 12, 8, 6, 4, 3
        ]
        
        hourly_data = []
        for i in range(24):
            if i <= current_hour:
                base = hourly_pattern[i]
                variation = random.randint(-2, 3)
                hourly_data.append(max(0, base + variation))
            else:
                hourly_data.append(0)
        
        total_today = sum(hourly_data)
        open_count = random.randint(5, 15)
        closed_count = total_today - open_count
        avg_response_time = random.randint(180, 420)
        
        return {
            "total_today": total_today,
            "open": open_count,
            "closed": closed_count,
            "avg_response_time": avg_response_time,
            "hourly_data": hourly_data,
            "team_performance": [
                {"name": "김민지", "handled": 45, "avg_time": 245},
                {"name": "이서연", "handled": 38, "avg_time": 312},
                {"name": "박지훈", "handled": 42, "avg_time": 278},
                {"name": "최유진", "handled": 35, "avg_time": 290}
            ],
            "csat_score": round(random.uniform(4.2, 4.8), 1)
        }
