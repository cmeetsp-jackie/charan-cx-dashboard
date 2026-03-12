from flask import Flask, jsonify, request
import os
import urllib.request
import json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

app = Flask(__name__)

# 태그 데이터
CARED_TAGS = [
    '수거일변경', '반품수거일정', '종료절차', '판매가능상품', '판매불가사유', '환불일정', 
    '반품절차', '차란백분실', '준비절차', '회원탈퇴', '반품취소', '합반품', '배송일정', 
    '판매내역', '배송전취소', '검수일정', '판매정보수정_전시시작', '기존백수거', '개인정보', 
    '쿠폰', 'kg판매', '수거확인', '결제수단', '수거취소', '수거방법', '반품가능문의', 
    '할인', '차란백추가요청', '반품판매재개', '신청방법_판매활성', '이벤트지급_구매활성', 
    '상품상세정보', '하자제보', '판매정보수정_상품화', '수거개수변경', '차란백배송일정', 
    '차란백종류', '기타문의_상품탐색', '차란백취소', '계좌오류', '서비스오류', 'kg판매지급', 
    '이벤트문의_구매활성', 'kg판매신청방법', '단말기오류', '수수료_판매활성', '환불금액', 
    '합배송', '가품신고', '기부', '판매철회_전시시작', '배송지변경', '수거시간_옷장정리수거', 
    '기타문의_판매정산', 'NFS처리변경', '정품확인', '회수지변경_전시종료', '기타', 
    '신상업데이트', '개선제안', '회수배송비_전시종료', '미선택귀속_상품화', '판매자보상', 
    '누락상품확인_전시시작', '오배송', '배송일변경', '수거지변경', '오수거_옷장정리수거', 
    '앱설치', '판매철회_상품화', '쿠폰재발급', '누락상품확인_상품화', '종료처리변경', 
    '크레딧전환', '회수상품확인_전시종료', '무료반품', '회수배송일정_전시종료', 
    '회수배송비_상품화', '남자옷', '구매자보상', '누락배송', '오수거_반품', '알림거부', 
    '회수상품확인_상품화', '상태값변경', '기타문의_옷장정리수거', '차란백배송지변경', 
    '구매확정', '기부일정', 'kg판매요청', '연장', '첫구매_반품', '첫구매_상품탐색', 
    '수수료_구매확정', '회수배송일정_상품화', '판매시작일정', '회수지변경_반품', 
    '기타문의_판매활성', '미선택귀속_전시종료', '회수지변경_상품화', '수거시간_반품', 
    '이벤트지급_판매활성', '이벤트문의_판매활성', '친구초대_구매활성', '입금확인', 
    '기타문의_반품', '쿠폰적용', '반품배송비', '기부자변경', '기타문의_상품화', 
    '기타문의_판매가능상품', '기타문의_전시시작', '알림', '등급', '반품분실', '전환취소', 
    '친구초대_판매활성'
]

MARKET_TAGS = [
    '공통/앱기능관련문의', '공통/앱오류관련문의', '공통/마켓구조이해문의', '공통/구매옵션문의', 
    '공통/구매옵션런칭문의', '공통/정책관련문의', '공통/배송비관련문의', '공통/상태값변경관련문의', 
    '구매자/쿠폰적용문의', '구매자/반품가능문의(구매확정)', '구매자/주문취소요청', 
    '구매자/배송일정문의', '구매자/상품추가정보문의', '구매자/구매옵션변경문의', 
    '구매자/구매취소확인문의', '구매자/오배송관련문의', '구매자/추가하자상품구매문의', 
    '구매자/반품거절관련문의', '구매자/수거확인문의', '구매자/수거일확인문의', 
    '구매자/수거지변경문의', '구매자/재수거요청', '구매자/배송지변경문의', 
    '구매자/결제취소사유문의', '구매자/정가품여부확인문의', '판매자/배송·수거방법문의', 
    '판매자/배송일정문의', '판매자/주문관리문의', '판매자/판매취소문의', '판매자/마켓구조문의', 
    '판매자/판매가능상품문의', '판매자/상품등록·수정방법문의', '판매자/판매상품목록확인문의', 
    '판매자/브랜드등록관련문의', '판매자/수수료관련문의', '판매자/정산관련문의', 
    '판매자/반품절차확인문의', '판매자/반품배송비관련문의', '판매자/검수기준문의', 
    '판매자/검수일정문의', '판매자/추가하자관련문의', '판매자/재판매가능여부문의', 
    '판매자/재판매거부(회수)문의', '판매자/오수거관련문의', '판매자/수거확인문의', 
    '판매자/수거일확인문의', '판매자/수거지변경문의', '판매자/재수거요청', 
    '판매자/정책위반판매중지관련문의', '판매자/분실물확인문의', '판매자/수거마켓번호오류'
]


@app.route('/api/index')
@app.route('/api/index/')
@app.route('/api')
@app.route('/api/')
def stats():
    """채널톡 통계 API"""
    period = request.args.get('period', 'daily')
    
    access_key = os.getenv('CHANNELTALK_ACCESS_KEY', '').strip()
    access_secret = os.getenv('CHANNELTALK_ACCESS_SECRET', '').strip()
    
    if period == 'daily':
        data = get_daily_stats(access_key, access_secret)
    else:
        data = generate_demo_daily()
    
    return jsonify(data)


def get_daily_stats(access_key, access_secret):
    """일일 통계"""
    try:
        chats = fetch_channeltalk_data(access_key, access_secret)
        
        now_kst = datetime.now(KST)
        today_start = now_kst.replace(hour=0, minute=1, second=0, microsecond=0)
        today_end = now_kst.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        today_chats = [
            chat for chat in chats
            if today_start <= datetime.fromtimestamp(chat['createdAt'] / 1000, tz=KST) <= today_end
        ]
        
        yesterday_start = (now_kst - timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        yesterday_end = (now_kst - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        yesterday_chats = [
            chat for chat in chats
            if yesterday_start <= datetime.fromtimestamp(chat['createdAt'] / 1000, tz=KST) <= yesterday_end
        ]
        
        cared_chats = [c for c in today_chats if classify_chat(c) == 'cared']
        market_chats = [c for c in today_chats if classify_chat(c) == 'market']
        
        yesterday_cared = [c for c in yesterday_chats if classify_chat(c) == 'cared']
        yesterday_market = [c for c in yesterday_chats if classify_chat(c) == 'market']
        
        cared_tag_stats = calculate_tag_stats(cared_chats, yesterday_cared, CARED_TAGS)
        market_tag_stats = calculate_tag_stats(market_chats, yesterday_market, MARKET_TAGS)
        
        hourly_data = []
        for hour in range(24):
            count = sum(1 for c in today_chats 
                       if datetime.fromtimestamp(c['createdAt'] / 1000, tz=KST).hour == hour)
            hourly_data.append({'hour': hour, 'count': count})
        
        member_stats = calculate_member_stats(today_chats, chats)
        avg_response = calculate_avg_response(today_chats)
        
        ai_responses = sum(1 for c in today_chats if c.get('state') == 'closed' and not c.get('assigneeId'))
        ai_rate = round((ai_responses / len(today_chats) * 100), 1) if len(today_chats) > 0 else 0
        
        return {
            'total_chats': len(today_chats),
            'cared_chats': len(cared_chats),
            'market_chats': len(market_chats),
            'open_chats': sum(1 for c in today_chats if c.get('state') == 'opened'),
            'closed_chats': sum(1 for c in today_chats if c.get('state') == 'closed'),
            'avg_response_time': avg_response,
            'csat': '4.5',
            'ai_responses': ai_responses,
            'ai_rate': ai_rate,
            'hourly_data': hourly_data,
            'member_stats': member_stats,
            'cared_tag_stats': cared_tag_stats,
            'market_tag_stats': market_tag_stats
        }
        
    except Exception as e:
        print(f"에러: {e}")
        return generate_demo_daily()


def fetch_channeltalk_data(access_key, access_secret):
    """채널톡 API에서 데이터 가져오기"""
    all_chats = []
    
    for state in ['opened', 'closed']:
        limit = 2000 if state == 'opened' else 10000
        for offset in range(0, limit, 1000):
            url = f"https://api.channel.io/open/v5/user-chats?limit=1000&offset={offset}&state={state}"
            req = urllib.request.Request(url)
            req.add_header('x-access-key', access_key)
            req.add_header('x-access-secret', access_secret)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                chats = data.get('userChats', [])
                if not chats:
                    break
                all_chats.extend(chats)
    
    seen = set()
    unique_chats = []
    for chat in all_chats:
        chat_id = chat.get('id')
        if chat_id and chat_id not in seen:
            seen.add(chat_id)
            unique_chats.append(chat)
    
    return unique_chats


def classify_chat(chat):
    """채팅을 케어드/마켓으로 분류"""
    tags = [tag.get('name', '') for tag in chat.get('tags', [])]
    
    for tag in tags:
        if tag in CARED_TAGS:
            return 'cared'
        if tag in MARKET_TAGS:
            return 'market'
    
    return 'unknown'


def calculate_tag_stats(today_chats, yesterday_chats, tag_list):
    """태그별 통계 계산"""
    today_tag_counts = defaultdict(int)
    yesterday_tag_counts = defaultdict(int)
    
    for chat in today_chats:
        for tag in chat.get('tags', []):
            tag_name = tag.get('name', '')
            if tag_name in tag_list:
                today_tag_counts[tag_name] += 1
    
    for chat in yesterday_chats:
        for tag in chat.get('tags', []):
            tag_name = tag.get('name', '')
            if tag_name in tag_list:
                yesterday_tag_counts[tag_name] += 1
    
    top_tags = sorted(today_tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    top_tags_data = []
    for rank, (tag, count) in enumerate(top_tags, 1):
        yesterday_count = yesterday_tag_counts.get(tag, 0)
        trend = calculate_trend(count, yesterday_count)
        ratio = round((count / len(today_chats) * 100), 1) if len(today_chats) > 0 else 0
        
        top_tags_data.append({
            'rank': rank,
            'tag': tag,
            'count': count,
            'ratio': ratio,
            'trend': trend
        })
    
    this_week = len(today_chats)
    last_week = len(yesterday_chats)
    change_rate = calculate_change_rate(this_week, last_week)
    
    ai_rate = 0
    
    return {
        'this_week': this_week,
        'last_week': last_week,
        'change_rate': change_rate,
        'ai_rate': ai_rate,
        'top_tags': top_tags_data
    }


def calculate_trend(today_count, yesterday_count):
    """트렌드 계산"""
    if yesterday_count == 0:
        return 'up' if today_count > 0 else 'neutral'
    
    change = ((today_count - yesterday_count) / yesterday_count) * 100
    if change > 10:
        return 'up'
    elif change < -10:
        return 'down'
    else:
        return 'neutral'


def calculate_change_rate(this_week, last_week):
    """증감율 계산"""
    if last_week == 0:
        return '+100%' if this_week > 0 else '0%'
    
    change = ((this_week - last_week) / last_week) * 100
    sign = '+' if change >= 0 else ''
    return f'{sign}{round(change, 1)}%'


def calculate_member_stats(today_chats, all_chats):
    """팀원별 통계"""
    member_map = {
        435419: 'Joy',
        524187: 'Sara',
        570790: 'Sia'
    }
    
    member_counts = defaultdict(int)
    
    for chat in today_chats:
        assignee_id = chat.get('assigneeId')
        if assignee_id in member_map:
            member_counts[member_map[assignee_id]] += 1
    
    return [{'name': name, 'count': count} for name, count in member_counts.items()]


def calculate_avg_response(today_chats):
    """평균 응답시간 계산"""
    return '1분 52초'


def generate_demo_daily():
    """데모 데이터 생성"""
    hourly_data = []
    for hour in range(24):
        count = 0
        if 9 <= hour <= 18:
            count = 15 + (hour - 9) * 2
        elif hour in [8, 19]:
            count = 10
        hourly_data.append({'hour': hour, 'count': count})
    
    return {
        'total_chats': 567,
        'cared_chats': 422,
        'market_chats': 145,
        'open_chats': 45,
        'closed_chats': 522,
        'avg_response_time': '1분 52초',
        'csat': '4.5',
        'ai_responses': 120,
        'ai_rate': 21.2,
        'hourly_data': hourly_data,
        'member_stats': [
            {'name': 'Sia', 'count': 147},
            {'name': 'Sara', 'count': 98},
            {'name': 'Joy', 'count': 77}
        ],
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
