"""
Google Trends 수집기 (pytrends 사용, API 키 불필요)
- 한국 급상승 검색어
- 커리어/학습 관련 키워드 트렌드 점수
"""
from pytrends.request import TrendReq
from datetime import datetime
import time

CAREER_KEYWORDS = [
    "프롬프트 엔지니어링", "AI 활용", "데이터 분석",
    "파이썬 독학", "노코드", "사이드프로젝트",
    "포트폴리오", "UX 디자인", "Next.js", "SQL 독학",
    "ChatGPT 활용", "자격증", "공모전", "스타트업",
]

def fetch_realtime_trends():
    """한국 실시간 급상승 검색어"""
    pytrends = TrendReq(hl="ko", tz=540)
    try:
        df = pytrends.trending_searches(pn="south_korea")
        return df[0].tolist()[:20]
    except Exception as e:
        print(f"  [경고] 실시간 트렌드 수집 실패: {e}")
        return []

def fetch_keyword_scores(keywords):
    """키워드별 관심도 점수 (0~100)"""
    pytrends = TrendReq(hl="ko", tz=540)
    scores = {}
    # 한번에 5개씩 (pytrends 제한)
    for i in range(0, len(keywords), 5):
        chunk = keywords[i:i+5]
        try:
            pytrends.build_payload(chunk, geo="KR", timeframe="now 7-d")
            df = pytrends.interest_over_time()
            if not df.empty:
                for kw in chunk:
                    if kw in df.columns:
                        scores[kw] = int(df[kw].mean())
            time.sleep(1)  # rate limit 방지
        except Exception as e:
            print(f"  [경고] {chunk} 점수 수집 실패: {e}")
    return scores

def run():
    print("[Google Trends] 수집 시작...")
    realtime = fetch_realtime_trends()
    scores = fetch_keyword_scores(CAREER_KEYWORDS)

    print(f"  → 실시간 {len(realtime)}개, 키워드 점수 {len(scores)}개 수집")
    return {
        "source": "google_trends",
        "collected_at": datetime.utcnow().isoformat(),
        "realtime_kr": realtime,
        "career_scores": scores,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
