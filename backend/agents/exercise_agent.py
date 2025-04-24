# agents/exercise_agent.py
from agents import BaseAgent
from typing import Dict, Any, List
import json

class ExerciseGenerationAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # inputs["explanations"] é a lista retornada pelo ExplanationAgent
        explanations: List[str] = inputs["explanations"]
        # 1) Junta tudo num único prompt
        prompt = self.prompt_template.replace("{{explanations}}", json.dumps(explanations))
        # 2) Gera via LLM
        raw = self.call_model(prompt)
        # 3) Parse esperto (por exemplo, JSON no raw)
        try:
            exercises = json.loads(raw)
        except json.JSONDecodeError:
            # Se não for JSON, retorne o texto cru
            exercises = raw.strip().split("\n")
        return {"exercises": exercises}
