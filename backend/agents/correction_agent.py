import requests
from typing import Dict, Any
from agents import BaseAgent

class LanguageCorrectionAgent(BaseAgent):
    def __init__(self, model_id: str, prompt: str, lang: str = "en-US", **kwargs):
        super().__init__(model_id, prompt, **kwargs)
        self.lang = lang
        self.api_url = "https://api.languagetool.org/v2/check"

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        text = inputs.get("text")
        
        if not text:
            raise ValueError("Text input is required for language correction.")

        try:
            resp = requests.post(self.api_url, data={
                "text": text,
                "language": self.lang,
            })
            resp.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        
        result = resp.json()
        errors = []

        for m in result.get("matches", []):
            offset = m["offset"]
            length = m["length"]
            error_detail = {
                "offset": offset,
                "length": length,
                "original": text[offset:offset + length],
                "correction": m["replacements"][0]["value"] if m["replacements"] else "No suggestion",
                "ruleId": m["rule"]["id"],
            }
            errors.append(error_detail)

        return {"errors": errors}
