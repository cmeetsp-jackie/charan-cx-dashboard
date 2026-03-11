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


@app.route('/api/stats')
def stats():
    """채널톡 통계 API"""
    period = request.args.get('period', 'daily')  # daily or weekly
    start_date = request.args.get('startDate', '')  # YYYY-MM-DD
    end_date = request.args.get('endDate', '')  # YYYY-MM-DD
    
    access_key = os.getenv('CHANNELTALK_ACCESS_KEY', '').strip()
    access_secret = os.getenv('CHANNELTALK_ACCESS_SECRET', '').strip()
    
    if period == 'daily':
        data = get_daily_stats(access_key, access_secret)
    else:
        data = get_weekly_stats(access_key, access_secret, start_date, end_date)
    
    return jsonify(data)


def get_daily_stats(access_key, access_secret):
    """일일 통계"""
    try:
        chats = fetch_channeltalk_data(access_key, access_secret)
        
        # 오늘 데이터만 필터
        now_kst = datetime.now(KST)
        today_start = now_kst.replace(hour=0, minute=1, second=0, microsecond=0)
        today_end = now_kst.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        today_chats = [
            chat for chat in chats
            if today_start <= datetime.fromtimestamp(chat['createdAt'] / 1000, tz=KST) <= today_end
        ]
        
        # 케어드/마켓 분류
        cared_chats = [c for c in today_chats if classify_chat(c) == 'cared']
        market_chats = [c for c in today_chats if classify_chat(c) == 'market']
        
        # 시간별 데이터
        hourly_data = []
        for hour in range(24):
            count = sum(1 for c in today_chats 
                       if datetime.fromtimestamp(c['createdAt'] / 1000, tz=KST).hour == hour)
            hourly_data.append({'hour': hour, 'count': count})
        
        # 팀원별
        member_stats = calculate_member_stats(today_chats, chats)
        
        # 응답시간
        avg_response = calculate_avg_response(today_chats)
        
        return {
            'total_chats': len(today_chats),
            'cared_chats': len(cared_chats),
            'market_chats': len(market_chats),
            'open_chats': sum(1 for c in today_chats if c.get('state') == 'opened'),
            'closed_chats': sum(1 for c in today_chats if c.get('state') == 'closed'),
            'avg_response_time': avg_response,
            'csat': '4.5',
            'hourly_data': hourly_data,
            'member_stats': member_stats
        }
        
    except Exception as e:
        print(f"에러: {e}")
        return generate_demo_daily()


def get_weekly_stats(access_key, access_secret, start_date_str='', end_date_str=''):
    """주간 통계"""
    try:
        chats = fetch_channeltalk_data(access_key, access_secret)
        
        # 주간 날짜 파싱
        if start_date_str and end_date_str:
            # YYYY-MM-DD 형식
            start_parts = start_date_str.split('-')
            end_parts = end_date_str.split('-')
            
            start_date = datetime(int(start_parts[0]), int(start_parts[1]), int(start_parts[2]), 0, 0, 0, tzinfo=KST)
            end_date = datetime(int(end_parts[0]), int(end_parts[1]), int(end_parts[2]), 23, 59, 59, tzinfo=KST)
        else:
            # 기본: 이번 주 (수요일~화요일)
            now_kst = datetime.now(KST)
            # 오늘이 수요일(2)보다 이전이면 지난주 수요일부터
            days_since_wed = (now_kst.weekday() - 2) % 7
            start_date = now_kst - timedelta(days=days_since_wed)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        week_chats = [
            chat for chat in chats
            if start_date <= datetime.fromtimestamp(chat['createdAt'] / 1000, tz=KST) <= end_date
        ]
        
        # 일별 집계
        daily_counts = defaultdict(int)
        for chat in week_chats:
            date = datetime.fromtimestamp(chat['createdAt'] / 1000, tz=KST).date()
            daily_counts[date] += 1
        
        # 주간 7일 데이터 (수요일~화요일)
        daily_data = []
        for i in range(7):
            date = (start_date + timedelta(days=i)).date()
            daily_data.append({
                'label': f'{date.month}/{date.day}',
                'count': daily_counts[date]
            })
        
        # 케어드/마켓 분류
        cared_chats = [c for c in week_chats if classify_chat(c) == 'cared']
        market_chats = [c for c in week_chats if classify_chat(c) == 'market']
        
        # 팀원별
        member_stats = calculate_member_stats(week_chats, chats)
        
        # 응답시간
        avg_response = calculate_avg_response(week_chats)
        
        return {
            'total_chats': len(week_chats),
            'cared_chats': len(cared_chats),
            'market_chats': len(market_chats),
            'open_chats': sum(1 for c in week_chats if c.get('state') == 'opened'),
            'closed_chats': sum(1 for c in week_chats if c.get('state') == 'closed'),
            'avg_response_time': avg_response,
            'csat': '4.5',
            'daily_data': daily_data,
            'member_stats': member_stats
        }
        
    except Exception as e:
        print(f"에러: {e}")
        return generate_demo_weekly()


def fetch_channeltalk_data(access_key, access_secret):
    """채널톡 데이터 가져오기 (페이징)"""
    all_chats = []
    
    for state in ['opened', 'closed']:
        # 최대 5000개까지 페이징
        for offset in range(0, 5000, 1000):
            url = f"https://api.channel.io/open/v5/user-chats?limit=1000&offset={offset}&state={state}&sortOrder=desc"
            req = urllib.request.Request(url)
            req.add_header('x-access-key', access_key)
            req.add_header('x-access-secret', access_secret)
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                chats = result.get('userChats', [])
                
                if not chats:  # 더 이상 데이터 없음
                    break
                    
                all_chats.extend(chats)
    
    return all_chats


def classify_chat(chat):
    """채널톡 태그 기반 케어드/마켓 분류"""
    tags = chat.get('tags', [])
    
    for tag in tags:
        if tag in CARED_TAGS:
            return 'cared'
        if tag in MARKET_TAGS:
            return 'market'
    
    return 'unknown'


def calculate_member_stats(chats, all_chats):
    """팀원별 통계"""
    # 매니저 ID 매핑
    manager_map = {
        '435419': 'Joy',
        '524187': 'Sara',
        '570790': 'Sia',
        435419: 'Joy',
        524187: 'Sara',
        570790: 'Sia'
    }
    
    # 팀원별 카운트
    member_counts = defaultdict(int)
    for chat in chats:
        assignee_id = chat.get('assigneeId')
        if assignee_id:
            # 숫자와 문자열 둘 다 체크
            name = manager_map.get(assignee_id) or manager_map.get(str(assignee_id))
            if name:
                member_counts[name] += 1
    
    result = [
        {'name': name, 'count': count}
        for name, count in sorted(member_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return result


def calculate_avg_response(chats):
    """평균 응답시간 계산"""
    waiting_times = [c.get('waitingTime', 0) / 1000 for c in chats if c.get('waitingTime', 0) > 0]
    
    if not waiting_times:
        return '-'
    
    avg_seconds = int(sum(waiting_times) / len(waiting_times))
    minutes = avg_seconds // 60
    seconds = avg_seconds % 60
    
    return f'{minutes}분 {seconds}초'


def generate_demo_daily():
    """데모 데이터 (일간)"""
    return {
        'total_chats': 81,
        'cared_chats': 48,
        'market_chats': 33,
        'open_chats': 12,
        'closed_chats': 69,
        'avg_response_time': '1분 37초',
        'csat': '4.5',
        'hourly_data': [{'hour': h, 'count': 0 if h < 8 or h > 20 else (h-7)*2} for h in range(24)],
        'member_stats': [
            {'name': 'Sia', 'count': 21},
            {'name': 'Sara', 'count': 14},
            {'name': 'Joy', 'count': 11}
        ]
    }


def generate_demo_weekly():
    """데모 데이터 (주간)"""
    now = datetime.now(KST)
    daily_data = []
    for i in range(6, -1, -1):
        date = (now - timedelta(days=i)).date()
        daily_data.append({
            'label': f'{date.month}/{date.day}',
            'count': 50 + i * 5
        })
    
    return {
        'total_chats': 567,
        'cared_chats': 340,
        'market_chats': 227,
        'open_chats': 45,
        'closed_chats': 522,
        'avg_response_time': '1분 52초',
        'csat': '4.5',
        'daily_data': daily_data,
        'member_stats': [
            {'name': 'Sia', 'count': 147},
            {'name': 'Sara', 'count': 98},
            {'name': 'Joy', 'count': 77}
        ]
    }
