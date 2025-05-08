from smolagents import tool
import requests
from bs4 import BeautifulSoup

@tool
def VisitWebpageTool(url: str) -> str:
    """
    Visita uma página da web e retorna um resumo do conteúdo.

    Args:
        url (str): A URL da página a ser visitada.

    Returns:
        str: Um trecho de até 500 caracteres com o texto extraído da página.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        return page_text[:500]
    except Exception as e:
        return f"Erro ao acessar a página: {str(e)}"
