"""
YouTube 커리어 키워드 수집기
- Invidious 공개 API 사용 (API 키 불필요)
- 트렌딩 피드 대신 커리어 키워드 직접 검색 → 조회수 기반 점수 산정
"""
import requests
from datetime import datetime

INVIDIOUS_INSTANCES = [
    "https://y.com.sb",
    "https://invidious.nerdvpn.de",
    "https://inv.nadeko.net",
    "https://invidious.lunar.icu",
    "https://vid.puffyan.us",
]

# 검색할 커리어 쿼리 → (키워드, 쿼리문자열)
CAREER_QUERIES = [
    ("AI", "AI 개발 강의"),
    ("LLM", "LLM 활용"),
    ("RAG", "RAG 구현"),
    ("에이전트", "AI 에이전트"),
    ("파이썬", "파이썬 독학"),
    ("데이터 분석", "데이터 분석 입문"),
    ("SQL", "SQL 강의"),
    ("ChatGPT", "ChatGPT 활용법"),
    ("프롬프트", "프롬프트 엔지니어링"),
    ("노코드", "노코드 자동화"),
    ("UX", "UX 디자인 포트폴리오"),
    ("취업", "개발자 취업"),
    ("이직", "이직 준비"),
    ("포트폴리오", "포트폴리오 만들기"),
    ("자격증", "IT 자격증"),
    ("사이드프로젝트", "사이드프로젝트 아이디어"),
    ("스타트업", "스타트업 창업"),
    ("마케팅", "디지털 마케팅"),
    ("재테크", "재테크 입문"),
    ("자동화", "업무 자동화"),
]


def get_working_instance():
    """작동하는 Invidious 인스턴스 반환"""
    for base in INVIDIOUS_INSTANCES:
        try:
            res = requests.get(
                f"{base}/api/v1/stats",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=8,
            )
            if res.status_code == 200:
                print(f"  → Invidious 인스턴스: {base}")
                return base
        except Exception:
            continue
    return None


def search_videos(base, query, max_results=5):
    """Invidious 검색 API로 영상 조회수 합계 반환"""
    try:
        url = f"{base}/api/v1/search"
        params = {
            "q": query,
            "sort_by": "relevance",
            "type": "video",
            "region": "KR",
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, params=params, headers=headers, timeout=10)
        if res.status_code != 200:
            return 0
        videos = res.json()
        if not isinstance(videos, list):
            return 0
        total_views = sum(v.get("viewCount", 0) for v in videos[:max_results])
        return total_views
    except Exception:
        return 0


def views_to_score(views):
    """조회수 합계를 0~50 점수로 변환"""
    if views >= 5_000_000:
        return 50
    elif views >= 1_000_000:
        return 30
    elif views >= 500_000:
        return 20
    elif views >= 100_000:
        return 10
    elif views >= 10_000:
        return 5
    return 0


def run():
    print("[YouTube] 수집 시작...")
    base = get_working_instance()
    if not base:
        print("  [경고] 작동하는 Invidious 인스턴스 없음")
        return {
            "source": "youtube",
            "collected_at": datetime.utcnow().isoformat(),
            "keywords": {},
        }

    keywords = {}
    for keyword, query in CAREER_QUERIES:
        views = search_videos(base, query)
        score = views_to_score(views)
        if score > 0:
            keywords[keyword] = score
        print(f"    {keyword}: {views:,} views → {score}점")

    # 점수 내림차순 정렬
    keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True))

    print(f"  → 키워드 {len(keywords)}개 추출")
    if keywords:
        top3 = list(keywords.items())[:3]
        print(f"  → TOP3: {top3}")

    return {
        "source": "youtube",
        "collected_at": datetime.utcnow().isoformat(),
        "keywords": keywords,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
