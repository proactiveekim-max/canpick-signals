"""
YouTube 트렌딩 수집기 (API 키 불필요 — 공개 페이지 스크래핑)
- 학습/커리어 관련 급상승 영상 키워드 추출
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

CAREER_TAGS = [
    "AI", "인공지능", "ChatGPT", "프롬프트", "파이썬", "코딩",
    "데이터", "공모전", "스타트업", "취업", "이직", "포트폴리오",
    "디자인", "UX", "노코드", "자동화", "사이드프로젝트", "부업",
    "자격증", "영어", "재테크", "투자",
]

def fetch_youtube_trending():
    """유튜브 트렌딩 페이지에서 영상 제목 수집"""
    url = "https://www.youtube.com/feed/trending?gl=KR&hl=ko"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        # YouTube는 JS 렌더링이라 제목 직접 파싱이 어려움
        # ytInitialData에서 제목 추출
        matches = re.findall(r'"title":\{"runs":\[{"text":"([^"]+)"', res.text)
        titles = list(dict.fromkeys(matches))[:30]  # 중복 제거
        return titles
    except Exception as e:
        print(f"  [경고] YouTube 수집 실패: {e}")
        return []

def extract_keywords(titles):
    """제목에서 커리어 관련 키워드 빈도 계산"""
    keyword_count = {}
    for title in titles:
        for tag in CAREER_TAGS:
            if tag.lower() in title.lower():
                keyword_count[tag] = keyword_count.get(tag, 0) + 1
    return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))

def run():
    print("[YouTube Trending] 수집 시작...")
    titles = fetch_youtube_trending()
    keywords = extract_keywords(titles)

    print(f"  → 영상 {len(titles)}개, 키워드 {len(keywords)}개 추출")
    return {
        "source": "youtube_trending",
        "collected_at": datetime.utcnow().isoformat(),
        "video_titles": titles[:15],
        "keywords": keywords,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
