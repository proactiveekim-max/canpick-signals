"""
원티드 채용공고 + 네이버 API 수집기
- 원티드: 공개 API (인증 불필요)
- 네이버: 검색 API (무료, 환경변수로 키 관리)
"""
import requests
from datetime import datetime
from collections import Counter
import re
import os

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

# 채용공고 포지션명에서 추출할 기술 키워드
SKILL_PATTERNS = [
    "AI", "ML", "LLM", "RAG", "GPT", "Claude", "Gemini",
    "Python", "파이썬", "JavaScript", "TypeScript", "React", "Next.js",
    "Flutter", "Swift", "Kotlin", "Java", "Go", "Rust",
    "SQL", "데이터", "분석", "Analytics", "Tableau", "Power BI",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "DevOps",
    "Figma", "UX", "UI", "디자인", "Design",
    "마케팅", "Marketing", "SEO", "퍼포먼스",
    "PM", "PO", "기획", "프로덕트",
    "노코드", "자동화", "Zapier", "Make",
    "보안", "Security", "블록체인",
]

def fetch_wanted_jobs():
    """원티드 채용공고 포지션명에서 키워드 추출"""
    url = "https://www.wanted.co.kr/api/v4/jobs"
    params = {
        "country": "kr",
        "job_sort": "job.latest_order",
        "limit": 100,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json",
        "Referer": "https://www.wanted.co.kr/",
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        jobs = res.json().get("data", [])

        # 포지션명 추출
        positions = [j.get("position", "") for j in jobs if j.get("position")]

        # 키워드 카운팅
        skill_counter = Counter()
        for pos in positions:
            for skill in SKILL_PATTERNS:
                if skill.lower() in pos.lower():
                    skill_counter[skill] += 1

        print(f"  → 원티드 공고 {len(positions)}개 수집, 스킬 {len(skill_counter)}개 추출")
        return dict(skill_counter.most_common(20))

    except Exception as e:
        print(f"  [경고] 원티드 API 실패: {e}")
        return {}

def fetch_jumpit_jobs():
    """점핏 채용공고 수집 (백업)"""
    url = "https://jumpit.saramin.co.kr/api/positions"
    params = {"sort": "rsp_rate", "page": 1}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        data = res.json()
        positions = data.get("result", {}).get("positions", [])
        tech_stacks = []
        for pos in positions:
            stacks = pos.get("techStacks", [])
            tech_stacks.extend(stacks)
        counter = Counter(tech_stacks)
        print(f"  → 점핏 스택 {len(counter)}개 추출")
        return dict(counter.most_common(15))
    except Exception as e:
        print(f"  [경고] 점핏 실패: {e}")
        return {}

def search_naver_blog(query, display=10):
    """네이버 블로그 검색 (API 키 있을 때만)"""
    if not NAVER_CLIENT_ID:
        return []
    url = "https://openapi.naver.com/v1/search/blog"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "sort": "date"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        items = res.json().get("items", [])
        return [re.sub(r"<[^>]+>", "", item["title"]) for item in items]
    except Exception as e:
        print(f"  [경고] 네이버 블로그 실패: {e}")
        return []

def run():
    print("[Naver/Jobs] 수집 시작...")

    wanted_skills = fetch_wanted_jobs()
    jumpit_skills = fetch_jumpit_jobs()

    # 두 소스 합산
    combined = Counter(wanted_skills) + Counter(jumpit_skills)

    blog_titles = []
    if NAVER_CLIENT_ID:
        for q in ["AI 개발자", "데이터 분석가", "UX 디자이너"]:
            blog_titles += search_naver_blog(q, display=5)

    print(f"  → 최종 스킬 {len(combined)}개, 블로그 {len(blog_titles)}개")
    return {
        "source": "naver_jobs",
        "collected_at": datetime.utcnow().isoformat(),
        "wanted_skills": dict(combined.most_common(20)),
        "jumpit_skills": jumpit_skills,
        "blog_titles": blog_titles[:10],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
