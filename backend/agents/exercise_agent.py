from agents import BaseAgent
from typing import Dict, Any, List
import json

class ExerciseGenerationAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        explanations: List[str] = inputs["explanations"]
        prompt = self.prompt_template.replace("{{explanations}}", json.dumps(explanations))
        raw = self.call_model(prompt)

        try:
            parsed = json.loads(raw)
            return {"exercises": parsed.get("fill_in_the_blank", []) + parsed.get("reformulation", [])}
        except json.JSONDecodeError:
            return {"exercises": raw.strip().split("\n")}
