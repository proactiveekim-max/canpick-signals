"""
네이버 검색 API + 원티드 채용공고 수집기
- 네이버 API: 무료 (하루 25,000건)
- 원티드: 공개 API
"""
import requests
from datetime import datetime
from collections import Counter
import os

# 네이버 API 키 (환경변수로 관리)
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

SEARCH_QUERIES = [
    "AI 개발자 채용", "데이터 분석가 채용", "UX 디자이너 채용",
    "프롬프트 엔지니어", "MLOps", "프로덕트 매니저 채용",
]

SKILL_KEYWORDS = [
    "Python", "SQL", "React", "TypeScript", "Figma", "AWS",
    "LangChain", "RAG", "Fine-tuning", "Tableau", "GA4",
    "Flutter", "SwiftUI", "Kotlin", "Docker", "Kubernetes",
    "ChatGPT", "Claude", "Notion", "Zapier",
]

def search_naver_blog(query, display=10):
    """네이버 블로그 검색"""
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
        return [item["title"].replace("<b>", "").replace("</b>", "") for item in items]
    except Exception as e:
        print(f"  [경고] 네이버 블로그 검색 실패: {e}")
        return []

def fetch_wanted_jobs():
    """원티드 공개 API로 채용공고 스킬 수집"""
    url = "https://www.wanted.co.kr/api/v4/jobs"
    params = {"country": "kr", "job_sort": "job.latest_order", "limit": 50}
    headers = {"User-Agent": "Mozilla/5.0", "wantedsessionid": ""}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        data = res.json()
        jobs = data.get("data", {}).get("jobs", [])
        skill_counter = Counter()
        for job in jobs:
            skills = job.get("skill_tags", [])
            for s in skills:
                name = s.get("title", "")
                if name:
                    skill_counter[name] += 1
        return dict(skill_counter.most_common(20))
    except Exception as e:
        print(f"  [경고] 원티드 API 실패: {e}")
        return {}

def run():
    print("[Naver/Jobs] 수집 시작...")
    wanted_skills = fetch_wanted_jobs()

    # 네이버 API 키가 있을 때만
    blog_titles = []
    if NAVER_CLIENT_ID:
        for q in SEARCH_QUERIES[:3]:
            blog_titles += search_naver_blog(q, display=5)

    print(f"  → 원티드 스킬 {len(wanted_skills)}개, 블로그 {len(blog_titles)}개 수집")
    return {
        "source": "naver_jobs",
        "collected_at": datetime.utcnow().isoformat(),
        "wanted_skills": wanted_skills,
        "blog_titles": blog_titles[:10],
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
