import os
import dotenv
import requests
from smolagents import CodeAgent, DuckDuckGoSearchTool, load_tool, tool
from tools.visit_webpage import VisitWebpageTool
from tools.final_answer import final_answer_tool
from agents.correction_agent import LanguageCorrectionAgent
from agents.explanation_agent import ExplanationAgent
from agents.exercise_agent import ExerciseGenerationAgent
from Gradio_UI import GradioUI

dotenv.load_dotenv()

# Modelos a tentar
MODELS_TO_TRY = [
    "Qwen/Qwen2.5-Coder-3B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
]

# Prompts embutidos diretamente no código
prompts = {
    "correction": "Corrija os erros gramaticais do seguinte texto e retorne uma lista estruturada com os erros identificados e as correções sugeridas.",
    "explanation": "Com base na lista de erros corrigidos, explique cada um deles de forma clara e educativa.",
    "exercise": "Gere um exercício para cada explicação fornecida, focando em reforçar o aprendizado do ponto gramatical.",
    "system": "Você é um assistente especializado em língua portuguesa.",
    "user": "Corrija e explique o seguinte texto: {text}",

    # Requisitos do CodeAgent
    "system_prompt": "Você é um agente útil e confiável que resolve tarefas com ferramentas.",
    
    # Planejamento
    "planning": {
        "initial_plan": "Descreva as etapas iniciais para resolver a tarefa, considerando as informações fornecidas e os recursos disponíveis.",
        "update_plan_pre_messages": "Antes de atualizar o plano, revise as mensagens ou tarefas anteriores que precisam ser reavaliadas ou ajustadas.",
        "update_plan_post_messages": "Depois de atualizar o plano, comunique os próximos passos e qualquer ajuste necessário com base nas mensagens anteriores.",
        "final_plan": "Este é o plano final para resolver a tarefa.",
        "feedback_messages": "Forneça um resumo ou feedback sobre o progresso feito até o momento."
    },

    # A chave `managed_agent` agora inclui os campos `task` e `report`
    "managed_agent": {
        "task": "Agora execute cada passo do plano, usando ferramentas quando necessário.",
        "report": "Forneça um relatório detalhado sobre o progresso e os resultados obtidos durante a execução da tarefa."
    },

    # Final Answer
    "final_answer": {
        "pre_messages": "Antes de fornecer a resposta final, revise todas as etapas anteriores e os dados coletados até agora.",
        "response": "Com base nas informações obtidas, forneça a melhor resposta final para o usuário.",
        "post_messages": "Após fornecer a resposta final, resuma qualquer informação adicional ou feedback necessário sobre o processo."
    }
}

# Função com fallback de modelo
def create_model_with_fallback():
    last_exception = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"Tentando carregar modelo: {model_name}")
            url = f"https://api-inference.huggingface.co/models/{model_name}"
            headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
            response = requests.post(url, headers=headers, json={"inputs": "Olá"})

            if response.status_code == 200:
                print(f"✅ Modelo {model_name} carregado com sucesso!")
                return model_name
            else:
                raise Exception(f"Erro ao chamar o modelo: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"⚠️ Erro com {model_name}: {e}")
            last_exception = e
    raise RuntimeError("Nenhum modelo disponível!") from last_exception

try:
    model_id = create_model_with_fallback()

    # Inicialização dos agentes
    correction_agent = LanguageCorrectionAgent(
        model_id=model_id,
        prompt=prompts["correction"]
    )
    explanation_agent = ExplanationAgent(
        model_id=model_id,
        prompt=prompts["explanation"]
    )
    exercise_agent = ExerciseGenerationAgent(
        model_id=model_id,
        prompt=prompts["exercise"]
    )

    @tool
    def gerar_explicacoes(texto: str) -> dict:
        """
        Corrige o texto fornecido, gera explicações gramaticais e cria exercícios.

        Args:
            texto (str): O texto a ser corrigido e analisado. O texto deve conter possíveis erros gramaticais a serem corrigidos.

        Returns:
            dict: Um dicionário contendo:
                - 'correction': Lista de erros corrigidos.
                - 'explanation': Explicações gramaticais.
                - 'exercise': Exercícios gerados.
        """
        corr = correction_agent.run({"text": texto})
        expl = explanation_agent.run({"errors": corr["errors"]})
        exer = exercise_agent.run({"explanations": expl["explanations"]})
        return {
            "correction": corr["errors"],
            "explanation": expl["explanations"],
            "exercise": exer.get("exercises", [])
        }


    @tool
    def FinalAnswerTool(inputs: dict) -> str:
        """
        Combina as correções, explicações e exercícios para gerar uma resposta final formatada.

        Args:
            inputs (dict): Um dicionário contendo as chaves 'correction', 'explanation' e 'exercise'.
                        - 'correction' é uma lista de erros corrigidos.
                        - 'explanation' é uma lista de explicações para os erros corrigidos.
                        - 'exercise' é uma lista de exercícios gerados.

        Returns:
            str: Uma string formatada contendo os erros corrigidos, as explicações e os exercícios gerados.
        """
        correction = inputs.get("correction", [])
        explanation = inputs.get("explanation", [])
        exercise = inputs.get("exercise", [])

        resposta_final = f"""🔍 **Erros Corrigidos**:
        {correction if correction else "Nenhum erro identificado."}

        💬 **Explicações**:
        {explanation if explanation else "Nenhuma explicação gerada."}

        📝 **Exercícios**:
        """
        for i, ex in enumerate(exercise, 1):
            resposta_final += f"\n{i}. {ex}"
        return resposta_final



    # Define o agente principal
    agent = CodeAgent(
        model=model_id,
        tools=[
            DuckDuckGoSearchTool(),  # Ferramenta de busca
            # VisitWebpageTool(url="https://www.bbc.co.uk/learningenglish/"),  # Ferramenta de visita a páginas
            gerar_explicacoes,  # Instância da ferramenta de correção, explicação e exercícios
            FinalAnswerTool,  # Instância da ferramenta final_answer_tool corrigida
        ],
        max_steps=6,
        verbosity_level=1,
        prompt_templates=prompts  # Modelos de prompt definidos
    )

    # Inicia a interface Gradio
    GradioUI(agent).launch()

except Exception as e:
    print(f"Erro durante a inicialização do sistema: {str(e)}")
    raise
