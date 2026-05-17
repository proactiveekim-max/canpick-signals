"""
CANPICK 키워드 시그널 수집 메인 스크립트
매일 GitHub Actions에서 자동 실행됨

실행: python collect.py
출력: data/keywords.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 이전 데이터 로드 (변화율 계산용)
DATA_PATH = Path("data/keywords.json")

def load_previous():
    if DATA_PATH.exists():
        with open(DATA_PATH) as f:
            return json.load(f)
    return {}

def calculate_temperature(score, prev_score, source_count):
    """
    온도 계산 로직
    - score: 현재 점수 (0~100)
    - prev_score: 지난 주 점수
    - source_count: 몇 개 소스에서 잡혔는지
    반환: emerging / rising / hot / verified
    """
    change_rate = 0
    if prev_score and prev_score > 0:
        change_rate = (score - prev_score) / prev_score * 100

    if source_count >= 3 and score >= 60:
        return "hot"
    elif source_count >= 3 or (source_count >= 2 and change_rate > 30):
        return "rising"
    elif source_count >= 2 or change_rate > 50:
        return "emerging"
    else:
        return "emerging"

def merge_signals(*signal_dicts):
    """여러 소스의 키워드 점수를 하나로 합산"""
    merged = {}
    for signals in signal_dicts:
        for kw, score in signals.items():
            if kw not in merged:
                merged[kw] = {"total_score": 0, "source_count": 0, "sources": []}
            merged[kw]["total_score"] += score
            merged[kw]["source_count"] += 1
    return merged

def run():
    print("=" * 50)
    print("CANPICK 키워드 수집 시작")
    print(f"실행 시각: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 50)

    prev_data = load_previous()
    all_signals = {}

    # ── 1. GitHub Trending ──
    try:
        from scrapers.github_trending import run as github_run
        github = github_run()
        for kw, count in github["keywords"].items():
            all_signals[kw] = all_signals.get(kw, {})
            all_signals[kw]["github"] = count * 10  # 스케일 조정
    except Exception as e:
        print(f"[오류] GitHub: {e}")

    # ── 2. Google Trends ──
    try:
        from scrapers.google_trends import run as google_run
        google = google_run()
        for kw, score in google["career_scores"].items():
            all_signals[kw] = all_signals.get(kw, {})
            all_signals[kw]["google"] = score
    except Exception as e:
        print(f"[오류] Google Trends: {e}")

    # ── 3. YouTube ──
    try:
        from scrapers.youtube_trending import run as youtube_run
        youtube = youtube_run()
        for kw, count in youtube["keywords"].items():
            all_signals[kw] = all_signals.get(kw, {})
            all_signals[kw]["youtube"] = count * 15
    except Exception as e:
        print(f"[오류] YouTube: {e}")

    # ── 4. 채용공고 ──
    try:
        from scrapers.naver_jobs import run as jobs_run
        jobs = jobs_run()
        for kw, count in jobs["wanted_skills"].items():
            all_signals[kw] = all_signals.get(kw, {})
            all_signals[kw]["jobs"] = min(count * 5, 100)
    except Exception as e:
        print(f"[오류] Jobs: {e}")

    # ── 온도 계산 및 결과 생성 ──
    keywords = []
    prev_keywords = {k["keyword"]: k for k in prev_data.get("keywords", [])}

    for kw, sources in all_signals.items():
        total = sum(sources.values())
        source_count = len(sources)
        prev = prev_keywords.get(kw, {})
        prev_score = prev.get("score", 0)

        temp = calculate_temperature(total, prev_score, source_count)

        keywords.append({
            "keyword": kw,
            "score": round(total),
            "prev_score": prev_score,
            "change": round(total - prev_score),
            "temperature": temp,
            "source_count": source_count,
            "sources": list(sources.keys()),
        })

    # 점수 높은 순 정렬
    keywords.sort(key=lambda x: x["score"], reverse=True)

    result = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_keywords": len(keywords),
        "keywords": keywords[:30],  # 상위 30개만 저장
    }

    # 저장
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"✅ 완료! {len(keywords)}개 키워드 → data/keywords.json 저장")
    print("상위 10개:")
    for k in keywords[:10]:
        print(f"  [{k['temperature'].upper():8}] {k['keyword']:20} 점수:{k['score']:4}")
    print("=" * 50)

if __name__ == "__main__":
    run()
