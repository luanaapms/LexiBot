# agents/spaced_repetition_agent.py
import sqlite3
from typing import Dict, Any
from datetime import datetime, timedelta

class SpacedRepetitionAgent:
    def __init__(self, storage_path: str, algorithm: str = "SM2"):
        self.conn = sqlite3.connect(storage_path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY,
                front TEXT,
                back TEXT,
                next_review DATE
            )
        """)
        self.conn.commit()

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # inputs pode conter items a adicionar ou sinalização de revisão
        if "add" in inputs:
            for item in inputs["add"]:
                self._add_card(item["front"], item["back"])
            return {"status": "added"}
        if inputs.get("review"):
            today = datetime.utcnow().date()
            c = self.conn.cursor()
            c.execute("SELECT id, front, back FROM flashcards WHERE next_review <= ?", (today,))
            cards = [{"id": r[0], "front": r[1], "back": r[2]} for r in c.fetchall()]
            return {"flashcards": cards}
        return {}

    def _add_card(self, front: str, back: str):
        next_review = datetime.utcnow().date() + timedelta(days=1)
        c = self.conn.cursor()
        c.execute("INSERT INTO flashcards (front, back, next_review) VALUES (?, ?, ?)",
                  (front, back, next_review))
        self.conn.commit()
