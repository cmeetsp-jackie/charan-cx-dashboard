from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = {
            'total_chats': 567,
            'cared_chats': 422,
            'market_chats': 145,
            'open_chats': 45,
            'closed_chats': 522,
            'avg_response_time': '1분 52초',
            'csat': '4.5',
            'ai_responses': 120,
            'ai_rate': 21.2,
            'hourly_data': [{'hour': h, 'count': 15 + (h-9)*2 if 9 <= h <= 18 else (10 if h in [8,19] else 0)} for h in range(24)],
            'member_stats': [{'name': 'Sia', 'count': 147}, {'name': 'Sara', 'count': 98}, {'name': 'Joy', 'count': 77}],
            'cared_tag_stats': {
                'this_week': 422,
                'last_week': 398,
                'change_rate': '+6.0%',
                'ai_rate': 18,
                'top_tags': [
                    {'rank': 1, 'tag': '수거일변경', 'count': 45, 'ratio': 10.7, 'trend': 'up'},
                    {'rank': 2, 'tag': '반품수거일정', 'count': 38, 'ratio': 9.0, 'trend': 'neutral'},
                    {'rank': 3, 'tag': '판매가능상품', 'count': 32, 'ratio': 7.6, 'trend': 'down'},
                    {'rank': 4, 'tag': '환불일정', 'count': 28, 'ratio': 6.6, 'trend': 'up'},
                    {'rank': 5, 'tag': '검수일정', 'count': 25, 'ratio': 5.9, 'trend': 'neutral'},
                    {'rank': 6, 'tag': '차란백배송일정', 'count': 22, 'ratio': 5.2, 'trend': 'up'},
                    {'rank': 7, 'tag': '반품절차', 'count': 20, 'ratio': 4.7, 'trend': 'neutral'},
                    {'rank': 8, 'tag': '수거확인', 'count': 18, 'ratio': 4.3, 'trend': 'down'},
                    {'rank': 9, 'tag': '정산일정', 'count': 15, 'ratio': 3.6, 'trend': 'up'},
                    {'rank': 10, 'tag': '회원탈퇴', 'count': 12, 'ratio': 2.8, 'trend': 'neutral'}
                ]
            },
            'market_tag_stats': {
                'this_week': 145,
                'last_week': 132,
                'change_rate': '+9.8%',
                'ai_rate': 25,
                'top_tags': [
                    {'rank': 1, 'tag': '구매자/배송일정문의', 'count': 28, 'ratio': 19.3, 'trend': 'up'},
                    {'rank': 2, 'tag': '판매자/정산관련문의', 'count': 22, 'ratio': 15.2, 'trend': 'neutral'},
                    {'rank': 3, 'tag': '구매자/주문취소요청', 'count': 18, 'ratio': 12.4, 'trend': 'up'},
                    {'rank': 4, 'tag': '판매자/검수일정문의', 'count': 15, 'ratio': 10.3, 'trend': 'down'},
                    {'rank': 5, 'tag': '공통/마켓구조이해문의', 'count': 12, 'ratio': 8.3, 'trend': 'neutral'},
                    {'rank': 6, 'tag': '판매자/상품등록·수정방법문의', 'count': 10, 'ratio': 6.9, 'trend': 'up'},
                    {'rank': 7, 'tag': '구매자/반품가능문의(구매확정)', 'count': 8, 'ratio': 5.5, 'trend': 'neutral'},
                    {'rank': 8, 'tag': '판매자/수수료관련문의', 'count': 7, 'ratio': 4.8, 'trend': 'down'},
                    {'rank': 9, 'tag': '구매자/구매취소확인문의', 'count': 6, 'ratio': 4.1, 'trend': 'up'},
                    {'rank': 10, 'tag': '공통/배송비관련문의', 'count': 5, 'ratio': 3.4, 'trend': 'neutral'}
                ]
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
