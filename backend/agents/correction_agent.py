# agents/correction_agent.py

import requests
from typing import Dict, Any
from agents import BaseAgent

class LanguageCorrectionAgent(BaseAgent):
    def __init__(self, model_id: str, prompt: str, lang: str = "en-US", **kwargs):
        super().__init__(model_id, prompt, **kwargs)
        self.lang = lang
        self.api_url = "https://api.languagetool.org/v2/check"

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        text = inputs["text"]
        # Chama a API pública do LanguageTool
        resp = requests.post(self.api_url, data={
            "text": text,
            "language": self.lang,
        })
        result = resp.json()
        errors = []
        for m in result.get("matches", []):
            offset = m["offset"]
            length = m["length"]
            errors.append({
                "offset": offset,
                "length": length,
                "original": text[offset:offset+length],
                "correction": m["replacements"][0]["value"] if m["replacements"] else "",
                "ruleId": m["rule"]["id"],
            })
        return {"errors": errors}
