"""
YouTube 트렌딩 수집기
- Invidious 공개 API 사용 (API 키 불필요)
- 한국 트렌딩 영상 제목에서 커리어 키워드 추출
"""
import requests
from datetime import datetime

# 공개 Invidious 인스턴스 (순서대로 시도)
INVIDIOUS_INSTANCES = [
    "https://y.com.sb",
    "https://invidious.nerdvpn.de",
    "https://inv.nadeko.net",
    "https://invidious.lunar.icu",
    "https://vid.puffyan.us",
]

CAREER_TAGS = [
    "AI", "인공지능", "ChatGPT", "GPT", "클로드", "프롬프트",
    "파이썬", "Python", "코딩", "개발", "프로그래밍",
    "데이터", "분석", "SQL", "엑셀",
    "공모전", "스타트업", "창업", "사이드프로젝트", "부업",
    "취업", "이직", "연봉", "포트폴리오", "자기계발",
    "디자인", "UX", "UI", "피그마", "Figma",
    "노코드", "자동화", "워크플로우",
    "영어", "자격증", "강의", "독학",
    "마케팅", "브랜딩", "콘텐츠",
    "투자", "재테크", "ETF",
    "LLM", "RAG", "agent", "에이전트",
]

def fetch_invidious_trending():
    """Invidious API로 한국 트렌딩 영상 수집"""
    for base in INVIDIOUS_INSTANCES:
        try:
            url = f"{base}/api/v1/trending"
            params = {"region": "KR", "type": "Default"}
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, params=params, headers=headers, timeout=10)
            if res.status_code == 200:
                videos = res.json()
                titles = [v.get("title", "") for v in videos[:30]]
                print(f"  → {base} 에서 {len(titles)}개 영상 수집")
                return titles
        except Exception as e:
            print(f"  [경고] {base} 실패: {e}")
            continue
    return []

def extract_keywords(titles):
    """제목에서 커리어 키워드 빈도 계산"""
    keyword_count = {}
    for title in titles:
        title_lower = title.lower()
        for tag in CAREER_TAGS:
            if tag.lower() in title_lower:
                keyword_count[tag] = keyword_count.get(tag, 0) + 1
    return dict(sorted(keyword_count.items(), key=lambda x: x[1], reverse=True))

def run():
    print("[YouTube Trending] 수집 시작...")
    titles = fetch_invidious_trending()
    keywords = extract_keywords(titles)

    print(f"  → 영상 {len(titles)}개, 키워드 {len(keywords)}개 추출")
    if keywords:
        top3 = list(keywords.items())[:3]
        print(f"  → TOP3: {top3}")

    return {
        "source": "youtube_trending",
        "collected_at": datetime.utcnow().isoformat(),
        "video_titles": titles[:15],
        "keywords": keywords,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
