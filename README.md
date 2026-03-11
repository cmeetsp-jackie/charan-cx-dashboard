# 📊 차란 CX 실시간 대시보드

**웹 브라우저 기반 고객 응대 현황 대시보드**

---

## 🚀 빠른 시작

### 1. 채널톡 API 토큰 설정

```bash
export CHANNELTALK_TOKEN="your_token_here"
```

### 2. 서버 실행

```bash
cd /Users/pc/.openclaw/workspace-edison/cx-dashboard
source venv/bin/activate
python3 server.py
```

### 3. 브라우저 접속

```
http://localhost:8080
```

---

## 📊 기능

### KPI 카드
- **오늘 총 대화**: 오늘 00:00부터 현재까지 대화 수
- **진행 중**: 아직 완료되지 않은 대화
- **완료**: 해결된 대화
- **평균 응답 시간**: 평균 첫 응답 시간

### 시간대별 차트
- 24시간 막대 그래프
- 어느 시간대에 문의가 많은지 시각화

### 자동 새로고침
- **30초마다** 자동으로 최신 데이터 업데이트
- 마지막 업데이트 시간 표시

---

## 🎨 UI/UX 특징

- ✅ **깔끔한 카드 레이아웃** (Zendesk 스타일)
- ✅ **색상 구분** (파랑/노랑/초록)
- ✅ **반응형 디자인** (모니터 크기에 맞춰 자동 조정)
- ✅ **부드러운 애니메이션**
- ✅ **Chart.js** 기반 인터랙티브 차트

---

## 📁 파일 구조

```
cx-dashboard/
├── server.py              # Flask 서버
├── channeltalk_api.py     # 채널톡 API 연동
├── templates/
│   └── dashboard.html     # 대시보드 프론트엔드
├── requirements.txt       # Python 패키지
└── README.md
```

---

## 🔧 다음 단계

### 추가 가능한 기능:
1. **팀별 성과 비교** (에이전트별 응답 속도)
2. **고객 만족도(CSAT)** 차트
3. **알림 기능** (응답 시간 초과 시 알림)
4. **주간/월간 리포트** 자동 생성
5. **모바일 앱 연동**

---

**개발 시간:** 약 30분 (2026-03-11)
**개발자:** Thomas Edison ⚡
