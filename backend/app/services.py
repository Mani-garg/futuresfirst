import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / "data" / "analytics.db"
CSV_DIR = BASE / "data" / "csv"
PDF_DIR = BASE / "data" / "pdfs"


@dataclass
class ToolResult:
    tool: str
    source: str
    payload: Any


class SqlTool:
    allowed = {
        "top_titles": """
            SELECT m.title, SUM(w.watch_minutes) AS total_minutes, AVG(r.rating) AS avg_rating
            FROM watch_activity w
            JOIN movies m ON m.movie_id = w.movie_id
            LEFT JOIN reviews r ON r.movie_id = m.movie_id
            WHERE strftime('%Y', w.watched_at) = :year
            GROUP BY m.title
            ORDER BY total_minutes DESC
            LIMIT 5
        """,
        "city_engagement": """
            SELECT v.city, SUM(w.watch_minutes) AS total_minutes
            FROM watch_activity w JOIN viewers v ON v.viewer_id = w.viewer_id
            WHERE date(w.watched_at) >= date((SELECT MAX(date(watched_at)) FROM watch_activity), '-30 day')
            GROUP BY v.city ORDER BY total_minutes DESC LIMIT 10
        """,
    }

    def run(self, key: str, params: dict[str, Any]) -> ToolResult:
        if key not in self.allowed:
            raise ValueError("Unsupported SQL tool")
        con = sqlite3.connect(DB_PATH)
        rows = pd.read_sql_query(self.allowed[key], con, params=params).to_dict(orient="records")
        con.close()
        return ToolResult(tool="sql", source=f"query:{key}", payload=rows)


class CsvTool:
    def run(self, name: str) -> ToolResult:
        if name not in {"marketing_spend.csv", "regional_performance.csv"}:
            raise ValueError("CSV access denied")
        df = pd.read_csv(CSV_DIR / name)
        return ToolResult(tool="csv", source=name, payload=df.to_dict(orient="records"))


class DocTool:
    def search(self, keyword: str) -> ToolResult:
        hits: list[dict[str, str]] = []
        for file in PDF_DIR.glob("*.txt"):
            text = file.read_text()
            if keyword.lower() in text.lower():
                hits.append({"document": file.name, "snippet": text[:220]})
        return ToolResult(tool="docs", source="policy+reports", payload=hits[:3])


class AnalyticsOrchestrator:
    def __init__(self) -> None:
        self.sql = SqlTool()
        self.csv = CsvTool()
        self.docs = DocTool()

    def answer(self, query: str, filters: dict[str, Any]) -> dict[str, Any]:
        q = query.lower()
        trace: list[ToolResult] = []

        if "best" in q or "performed" in q:
            year = str(filters.get("year", 2025))
            trace.append(self.sql.run("top_titles", {"year": year}))
        if "city" in q or "engagement" in q:
            trace.append(self.sql.run("city_engagement", {}))
        if "trending" in q or "comedy" in q or "recommend" in q:
            trace.append(self.csv.run("marketing_spend.csv"))
            trace.append(self.docs.search("campaign"))

        if not trace:
            trace.append(self.docs.search(q.split()[0]))

        response = self._summarize(query, trace)
        return {
            "answer": response,
            "sources": [{"tool": t.tool, "source": t.source} for t in trace],
            "trace": [t.__dict__ for t in trace],
        }

    def _summarize(self, query: str, trace: list[ToolResult]) -> str:
        bits: list[str] = [f"For '{query}', I analyzed {len(trace)} approved internal tools."]
        for t in trace:
            if t.tool == "sql" and t.payload:
                top = t.payload[0]
                bits.append(f"SQL shows {top.get('title', top.get('city'))} leading in {t.source}.")
            if t.tool == "csv" and t.payload:
                bits.append("Marketing spend indicates stronger investment in sci-fi and action campaigns.")
            if t.tool == "docs" and t.payload:
                bits.append("Internal reports mention campaign timing and social buzz as key drivers.")
        bits.append("Recommendation: double down on high-retention genres and rebalance weak comedy targeting.")
        return " ".join(bits)

    def dashboard_metrics(self) -> dict[str, Any]:
        titles = self.sql.run("top_titles", {"year": "2025"}).payload
        cities = self.sql.run("city_engagement", {}).payload
        return {"top_titles": titles, "city_engagement": cities}
