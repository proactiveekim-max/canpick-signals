# canpick-signals

CANPICK 키워드 트렌드 자동 수집기

## 구조
```
scrapers/
  github_trending.py  — GitHub 트렌딩 레포 키워드
  google_trends.py    — 구글 트렌드 한국 점수
  youtube_trending.py — 유튜브 급상승 키워드
  naver_jobs.py       — 원티드/네이버 채용공고 스킬
collect.py            — 메인 실행 + 온도 계산
data/keywords.json    — 수집 결과 (매일 자동 업데이트)
```

## 온도 기준
| 온도 | 조건 |
|---|---|
| 🌱 emerging | 1~2개 소스, 초기 신호 |
| 🔥 rising | 2개 이상 소스 OR 30%+ 상승 |
| ⚡ hot | 3개 이상 소스 + 점수 60+ |

## 자동 실행
GitHub Actions로 매일 오전 11시 (KST) 자동 실행
결과: `data/keywords.json`
