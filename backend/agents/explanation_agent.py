# agents/explanation_agent.py
from agents import BaseAgent
import json
from typing import Dict, Any, List

class ExplanationAgent(BaseAgent):
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # inputs["errors"] é a lista de objetos gerada pelo CorrectionAgent
        errors: List[Dict[str, Any]] = inputs["errors"]
        explanations = []

        for err in errors:
            # 1) Preenche o prompt com o erro
            prompt = self.prompt_template.replace("{{error}}", json.dumps(err))
            # 2) Chama o LLM
            raw = self.call_model(prompt)
            # 3) Parse de texto livre em string
            explanations.append(raw.strip())

        return {"explanations": explanations}
