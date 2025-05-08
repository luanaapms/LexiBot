from smolagents import tool

@tool
def final_answer_tool(inputs: dict) -> str:
    """
    Combina as correções, explicações e exercícios para gerar uma resposta final formatada.

    Args:
        inputs (dict): Dicionário contendo:
            - 'correction' (list): Lista de erros corrigidos.
            - 'explanation' (list): Explicações gramaticais.
            - 'exercise' (list): Exercícios gerados.

    Returns:
        str: Texto formatado em markdown com as seções de correções, explicações e exercícios.
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
