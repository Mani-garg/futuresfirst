import random
import sqlite3
from pathlib import Path
import pandas as pd

base = Path(__file__).resolve().parents[1]
csv_dir = base / "data" / "csv"
pdf_dir = base / "data" / "pdfs"
csv_dir.mkdir(parents=True, exist_ok=True)
pdf_dir.mkdir(parents=True, exist_ok=True)

random.seed(42)
movies = pd.DataFrame([
    (1, "Stellar Run", "Sci-Fi"), (2, "Dark Orbit", "Sci-Fi"), (3, "Last Kingdom", "Drama"),
    (4, "Laugh Storm", "Comedy"), (5, "Neon Heist", "Action")
], columns=["movie_id", "title", "genre"])
viewers = pd.DataFrame([(i, random.choice(["New York", "Austin", "Seattle", "Chicago"]), random.choice(["18-24", "25-34", "35-44"])) for i in range(1, 101)], columns=["viewer_id", "city", "segment"])
watch = pd.DataFrame([(i, random.randint(1, 100), random.randint(1, 5), f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}", random.randint(30, 180)) for i in range(1, 501)], columns=["activity_id", "viewer_id", "movie_id", "watched_at", "watch_minutes"])
reviews = pd.DataFrame([(i, random.randint(1,5), random.randint(2,5), random.choice(["great", "ok", "weak"] )) for i in range(1, 101)], columns=["review_id", "movie_id", "rating", "comment"])
marketing = pd.DataFrame({"genre": ["Sci-Fi", "Drama", "Comedy", "Action"], "spend_usd": [550000, 300000, 180000, 470000], "roi": [2.4, 1.7, 0.9, 2.1]})
regional = pd.DataFrame({"city": ["New York", "Austin", "Seattle", "Chicago"], "engagement_score": [88, 81, 79, 74], "growth_pct": [11, 9, 7, 5]})

for name, df in {
    "movies.csv": movies,
    "viewers.csv": viewers,
    "watch_activity.csv": watch,
    "reviews.csv": reviews,
    "marketing_spend.csv": marketing,
    "regional_performance.csv": regional,
}.items():
    df.to_csv(csv_dir / name, index=False)

for name, text in {
    "quarterly_executive_report.txt": "Q4 campaign results show Stellar Run outperformed due to stronger social engagement and repeat viewing.",
    "campaign_performance_summary.txt": "Campaign timing in urban regions increased conversion. Comedy campaigns under-indexed due to poor message-market fit.",
    "content_roadmap.txt": "Roadmap prioritizes sci-fi sequels and action originals in 2026.",
    "policy_guidelines.txt": "Sensitive data must be masked and access must be role-based.",
    "audience_behavior_report.txt": "25-34 segment has highest completion rates in sci-fi content.",
}.items():
    (pdf_dir / name).write_text(text)

con = sqlite3.connect(base / "data" / "analytics.db")
movies.to_sql("movies", con, if_exists="replace", index=False)
viewers.to_sql("viewers", con, if_exists="replace", index=False)
watch.to_sql("watch_activity", con, if_exists="replace", index=False)
reviews.to_sql("reviews", con, if_exists="replace", index=False)
con.close()
print("Data generated")
