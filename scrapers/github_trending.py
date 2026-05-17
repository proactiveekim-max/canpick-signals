"""
GitHub Trending 수집기
- API 키 불필요
- 전체 / 한국어 레포 트렌딩 수집
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_github_trending(language="", since="daily"):
    url = f"https://github.com/trending/{language}?since={since}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for repo in soup.select("article.Box-row")[:20]:
        name_tag = repo.select_one("h2 a")
        desc_tag = repo.select_one("p")
        stars_tag = repo.select_one("a[href*='stargazers']")
        lang_tag = repo.select_one("[itemprop='programmingLanguage']")
        star_today = repo.select_one(".float-sm-right")

        if not name_tag:
            continue

        results.append({
            "repo": name_tag.get_text(strip=True).replace("\n", "").replace(" ", ""),
            "description": desc_tag.get_text(strip=True) if desc_tag else "",
            "language": lang_tag.get_text(strip=True) if lang_tag else "",
            "stars_today": star_today.get_text(strip=True) if star_today else "0",
        })
    return results

def run():
    print("[GitHub Trending] 수집 시작...")
    global_repos = fetch_github_trending(since="daily")
    python_repos = fetch_github_trending(language="python", since="daily")
    js_repos = fetch_github_trending(language="javascript", since="daily")

    # 키워드 추출 (description에서 주요 기술어 추출)
    keywords = {}
    tech_terms = [
        "AI", "LLM", "agent", "RAG", "fine-tuning", "embedding",
        "TypeScript", "React", "Next.js", "Rust", "Go",
        "data", "analytics", "automation", "workflow",
        "vision", "multimodal", "diffusion", "generative",
    ]
    for repo in global_repos + python_repos + js_repos:
        text = (repo["repo"] + " " + repo["description"]).lower()
        for term in tech_terms:
            if term.lower() in text:
                keywords[term] = keywords.get(term, 0) + 1

    print(f"  → {len(global_repos)}개 레포 수집, {len(keywords)}개 키워드 추출")
    return {
        "source": "github_trending",
        "collected_at": datetime.utcnow().isoformat(),
        "repos": global_repos[:10],
        "keywords": keywords,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
