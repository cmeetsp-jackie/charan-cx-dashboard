export default async function handler(req, res) {
  const CARED_TAGS = ['수거일변경', '반품수거일정', '종료절차', '판매가능상품', '판매불가사유', '환불일정', '반품절차', '차란백분실', '준비절차', '회원탈퇴', '반품취소', '합반품', '배송일정', '판매내역', '배송전취소', '검수일정', '판매정보수정_전시시작', '기존백수거', '개인정보', '쿠폰', 'kg판매', '수거확인', '결제수단', '수거취소', '수거방법', '반품가능문의', '할인', '차란백추가요청', '반품판매재개', '신청방법_판매활성', '이벤트지급_구매활성', '상품상세정보', '하자제보', '판매정보수정_상품화', '수거개수변경', '차란백배송일정', '차란백종류', '기타문의_상품탐색', '차란백취소', '계좌오류', '서비스오류', 'kg판매지급', '이벤트문의_구매활성', 'kg판매신청방법', '단말기오류', '수수료_판매활성', '환불금액', '합배송', '가품신고', '기부', '판매철회_전시시작', '배송지변경', '수거시간_옷장정리수거', '기타문의_판매정산', 'NFS처리변경', '정품확인', '회수지변경_전시종료', '기타', '신상업데이트', '개선제안', '회수배송비_전시종료', '미선택귀속_상품화', '판매자보상', '누락상품확인_전시시작', '오배송', '배송일변경', '수거지변경', '오수거_옷장정리수거', '앱설치', '판매철회_상품화', '쿠폰재발급', '누락상품확인_상품화', '종료처리변경', '크레딧전환', '회수상품확인_전시종료', '무료반품', '회수배송일정_전시종료', '회수배송비_상품화', '남자옷', '구매자보상', '누락배송', '오수거_반품', '알림거부', '회수상품확인_상품화', '상태값변경', '기타문의_옷장정리수거', '차란백배송지변경', '구매확정', '기부일정', 'kg판매요청', '연장', '첫구매_반품', '첫구매_상품탐색', '수수료_구매확정', '회수배송일정_상품화', '판매시작일정', '회수지변경_반품', '기타문의_판매활성', '미선택귀속_전시종료', '회수지변경_상품화', '수거시간_반품', '이벤트지급_판매활성', '이벤트문의_판매활성', '친구초대_구매활성', '입금확인', '기타문의_반품', '쿠폰적용', '반품배송비', '기부자변경', '기타문의_상품화', '기타문의_판매가능상품', '기타문의_전시시작', '알림', '등급', '반품분실', '전환취소', '친구초대_판매활성'];

  const MARKET_TAGS = ['공통/앱기능관련문의', '공통/앱오류관련문의', '공통/마켓구조이해문의', '공통/구매옵션문의', '공통/구매옵션런칭문의', '공통/정책관련문의', '공통/배송비관련문의', '공통/상태값변경관련문의', '구매자/쿠폰적용문의', '구매자/반품가능문의(구매확정)', '구매자/주문취소요청', '구매자/배송일정문의', '구매자/상품추가정보문의', '구매자/구매옵션변경문의', '구매자/구매취소확인문의', '구매자/오배송관련문의', '구매자/추가하자상품구매문의', '구매자/반품거절관련문의', '구매자/수거확인문의', '구매자/수거일확인문의', '구매자/수거지변경문의', '구매자/재수거요청', '구매자/배송지변경문의', '구매자/결제취소사유문의', '구매자/정가품여부확인문의', '판매자/배송·수거방법문의', '판매자/배송일정문의', '판매자/주문관리문의', '판매자/판매취소문의', '판매자/마켓구조문의', '판매자/판매가능상품문의', '판매자/상품등록·수정방법문의', '판매자/판매상품목록확인문의', '판매자/브랜드등록관련문의', '판매자/수수료관련문의', '판매자/정산관련문의', '판매자/반품절차확인문의', '판매자/반품배송비관련문의', '판매자/검수기준문의', '판매자/검수일정문의', '판매자/추가하자관련문의', '판매자/재판매가능여부문의', '판매자/재판매거부(회수)문의', '판매자/오수거관련문의', '판매자/수거확인문의', '판매자/수거일확인문의', '판매자/수거지변경문의', '판매자/재수거요청', '판매자/정책위반판매중지관련문의', '판매자/분실물확인문의', '판매자/수거마켓번호오류'];

  const accessKey = process.env.CHANNELTALK_ACCESS_KEY;
  const accessSecret = process.env.CHANNELTALK_ACCESS_SECRET;

  try {
    // 채널톡 데이터 가져오기
    let allChats = [];
    
    for (const state of ['opened', 'closed']) {
      const limit = state === 'opened' ? 2000 : 10000;
      for (let offset = 0; offset < limit; offset += 1000) {
        const url = `https://api.channel.io/open/v5/user-chats?limit=1000&offset=${offset}&state=${state}`;
        const response = await fetch(url, {
          headers: {
            'x-access-key': accessKey,
            'x-access-secret': accessSecret
          }
        });
        const data = await response.json();
        const chats = data.userChats || [];
        if (chats.length === 0) break;
        allChats = allChats.concat(chats);
      }
    }

    // 중복 제거
    const seen = new Set();
    const uniqueChats = allChats.filter(c => {
      if (seen.has(c.id)) return false;
      seen.add(c.id);
      return true;
    });

    // 오늘/어제 필터링
    const now = new Date();
    const kst = now.getTime() + (9 * 60 * 60 * 1000);
    const today = new Date(kst);
    today.setHours(0, 1, 0, 0);
    const todayEnd = new Date(kst);
    todayEnd.setHours(23, 59, 59, 999);
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayEnd = new Date(yesterday);
    yesterdayEnd.setHours(23, 59, 59, 999);

    const todayChats = uniqueChats.filter(c => {
      const t = new Date(c.createdAt);
      return t >= today && t <= todayEnd;
    });

    const yesterdayChats = uniqueChats.filter(c => {
      const t = new Date(c.createdAt);
      return t >= yesterday && t <= yesterdayEnd;
    });

    // 케어드/마켓 분류
    const classify = (chat) => {
      const tags = (chat.tags || []).map(t => t.name);
      if (tags.some(t => CARED_TAGS.includes(t))) return 'cared';
      if (tags.some(t => MARKET_TAGS.includes(t))) return 'market';
      return 'unknown';
    };

    const caredToday = todayChats.filter(c => classify(c) === 'cared');
    const marketToday = todayChats.filter(c => classify(c) === 'market');
    const caredYesterday = yesterdayChats.filter(c => classify(c) === 'cared');
    const marketYesterday = yesterdayChats.filter(c => classify(c) === 'market');

    // 태그 통계
    const calcTagStats = (today, yesterday, tagList) => {
      const todayCounts = {};
      const yesterdayCounts = {};
      
      today.forEach(c => {
        (c.tags || []).forEach(t => {
          if (tagList.includes(t.name)) {
            todayCounts[t.name] = (todayCounts[t.name] || 0) + 1;
          }
        });
      });
      
      yesterday.forEach(c => {
        (c.tags || []).forEach(t => {
          if (tagList.includes(t.name)) {
            yesterdayCounts[t.name] = (yesterdayCounts[t.name] || 0) + 1;
          }
        });
      });

      const sorted = Object.entries(todayCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);
      const topTags = sorted.map(([tag, count], i) => {
        const ycount = yesterdayCounts[tag] || 0;
        let trend = 'neutral';
        if (ycount > 0) {
          const change = ((count - ycount) / ycount) * 100;
          if (change > 10) trend = 'up';
          else if (change < -10) trend = 'down';
        } else if (count > 0) {
          trend = 'up';
        }
        const ratio = today.length > 0 ? ((count / today.length) * 100).toFixed(1) : 0;
        return { rank: i + 1, tag, count, ratio: parseFloat(ratio), trend };
      });

      const changeRate = yesterday.length > 0 
        ? `${((today.length - yesterday.length) / yesterday.length * 100).toFixed(1)}%`
        : '0%';

      return {
        this_week: today.length,
        last_week: yesterday.length,
        change_rate: (today.length >= yesterday.length ? '+' : '') + changeRate,
        ai_rate: 0,
        top_tags: topTags
      };
    };

    // 시간별
    const hourly = Array.from({ length: 24 }, (_, h) => ({
      hour: h,
      count: todayChats.filter(c => new Date(c.createdAt).getHours() === h).length
    }));

    // 팀원별
    const memberMap = { 435419: 'Joy', 524187: 'Sara', 570790: 'Sia' };
    const memberCounts = {};
    todayChats.forEach(c => {
      const name = memberMap[c.assigneeId];
      if (name) memberCounts[name] = (memberCounts[name] || 0) + 1;
    });
    const members = Object.entries(memberCounts).map(([name, count]) => ({ name, count }));

    // AI 응답
    const aiChats = todayChats.filter(c => c.state === 'closed' && !c.assigneeId);
    const aiRate = todayChats.length > 0 ? ((aiChats.length / todayChats.length) * 100).toFixed(1) : 0;

    res.status(200).json({
      total_chats: todayChats.length,
      cared_chats: caredToday.length,
      market_chats: marketToday.length,
      open_chats: todayChats.filter(c => c.state === 'opened').length,
      closed_chats: todayChats.filter(c => c.state === 'closed').length,
      avg_response_time: '1분 52초',
      csat: '4.5',
      ai_responses: aiChats.length,
      ai_rate: parseFloat(aiRate),
      hourly_data: hourly,
      member_stats: members,
      cared_tag_stats: calcTagStats(caredToday, caredYesterday, CARED_TAGS),
      market_tag_stats: calcTagStats(marketToday, marketYesterday, MARKET_TAGS)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
