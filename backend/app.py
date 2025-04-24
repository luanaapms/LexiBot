from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from agents.correction_agent import LanguageCorrectionAgent
from agents.explanation_agent import ExplanationAgent
from agents.exercise_agent import ExerciseGenerationAgent

import yaml

# 1. Carrega templates de prompt 
with open("prompts/prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

# 2. Instancia cada smolAgent
correction_agent = LanguageCorrectionAgent(
    model_id="", 
    prompt=prompts["correction"]
)
explanation_agent = ExplanationAgent(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct", 
    prompt=prompts["explanation"]
)
exercise_agent = ExerciseGenerationAgent(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct", 
    prompt=prompts["exercise"]
)

# 3. Cria FastAPI e configura CORS
app = FastAPI(title="LexiBot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        ],
    allow_credentials=True,   
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Define esquema de request/response
class TextRequest(BaseModel):
    text: str

class MentorResponse(BaseModel):
    errors: list
    explanations: list
    exercises: list

# 5. Endpoint principal
@app.post("/mentor", response_model=MentorResponse)
def mentor_endpoint(req: TextRequest):
    try:
        # 5.1 Correção
        corr_out = correction_agent.run({"text": req.text})
        # 5.2 Explicação
        expl_out = explanation_agent.run({"errors": corr_out["errors"]})
        # 5.3 Exercícios
        exer_out = exercise_agent.run({"explanations": expl_out["explanations"]})

        return MentorResponse(
            errors=corr_out["errors"],
            explanations=expl_out["explanations"],
            exercises=exer_out.get("exercises", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. Raiz
@app.get("/")
def root():
    return {"message": "Welcome to LexiBot API"}

