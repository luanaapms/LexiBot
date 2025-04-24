# agents/__init__.py
from typing import Dict, Any

class BaseAgent:
    def __init__(self, model_id: str, prompt: str, **kwargs):
        self.model_id = model_id
        self.prompt_template = prompt
        # aqui você pode inicializar clientes de API, HF endpoints, etc.

    def call_model(self, prompt: str) -> str:
        # ex.: usar HuggingFace Inference API ou seu client preferido
        # return client.text_generation(model_id=self.model_id, prompt=prompt, ...)
        raise NotImplementedError

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
