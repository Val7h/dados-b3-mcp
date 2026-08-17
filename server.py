"""Dados B3 — servidor MCP (conector de IA para fundamentos da bolsa brasileira).

Duas formas de usar:

1. REMOTO (recomendado, nada para instalar): adicione o conector
   https://dadosb3.com/mcp/ ao seu cliente de IA (Claude, etc.).

2. LOCAL (este arquivo): um servidor MCP stdio que chama a API pública do
   Dados B3 por HTTP. Útil para embutir em fluxos locais.

As ferramentas expõem dados fundamentalistas das companhias abertas
brasileiras (2010–hoje) com metodologia pública. O universo cresce quando a
CVM publica — por isso nenhuma contagem fica escrita aqui: quem quiser o
número de hoje chama `saude`. A empresa WEGE3 e a
metodologia são gratuitas (degustação); as demais empresas exigem uma chave
(grátis ou Pro) passada no argumento `chave_api`. Detalhes e planos em
https://dadosb3.com.
"""

from __future__ import annotations

import os

import httpx
from mcp.server.fastmcp import FastMCP

API = os.environ.get("DADOS_B3_API", "https://dadosb3.com")
CHAVE = os.environ.get("DADOS_B3_API_KEY", "")

mcp = FastMCP("dados-b3")


def _get(caminho: str, chave_api: str = "") -> dict:
    headers = {}
    k = chave_api or CHAVE
    if k:
        headers["X-API-Key"] = k
    r = httpx.get(f"{API}{caminho}", headers=headers, timeout=30)
    if r.status_code == 401:
        return {"erro": "chave de API ausente ou inativa",
                "como_resolver": f"Crie uma chave grátis ou assine em {API}/assinar "
                                 "e passe em chave_api. WEGE3 é aberta sem chave."}
    r.raise_for_status()
    return r.json()


@mcp.tool()
def listar_empresas() -> dict:
    """Lista as companhias abertas brasileiras disponíveis, com nome, CNPJ e
    ticker. A contagem vem na resposta — não fica congelada nesta descrição,
    que é lida por clientes de IA e envelheceria sem ninguém ver. Gratuito."""
    return _get("/empresas")


@mcp.tool()
def indicadores_anuais(ticker: str, chave_api: str = "") -> dict:
    """ROIC, ROE, margens, crescimento e dívida líquida/EBITDA (série anual
    2010–hoje) de uma empresa da B3. WEGE3 é gratuita; demais exigem chave_api."""
    return _get(f"/empresas/{ticker}/indicadores", chave_api)


@mcp.tool()
def multiplos(ticker: str, chave_api: str = "") -> dict:
    """Múltiplos ponto-no-tempo (P/L, P/VP, EV/EBITDA; P/L TTM trimestral) —
    preço do 1º pregão APÓS a publicação real do balanço, sem look-ahead.
    WEGE3 gratuita."""
    return _get(f"/empresas/{ticker}/multiplos", chave_api)


@mcp.tool()
def fatos_contabeis(ticker: str, trimestral: bool = False, chave_api: str = "") -> dict:
    """Contas padronizadas (receita, EBIT, lucro, PL, dívida...) com a conta
    CVM de origem de cada número. Anual ou trimestral. WEGE3 gratuita."""
    return _get(f"/empresas/{ticker}/fatos?trimestral={str(trimestral).lower()}",
                chave_api)


@mcp.tool()
def metodologia(nome: str = "") -> dict:
    """Metodologia pública dos indicadores. Sem argumento lista as páginas;
    com nome (ex.: 'roic') devolve o texto. Gratuito."""
    if not nome:
        return _get("/metodologia")
    return {"nome": nome, "conteudo": httpx.get(
        f"{API}/metodologia/{nome}.md", timeout=30).text}


@mcp.tool()
def saude() -> dict:
    """Cobertura atual do banco (contagens e última atualização). Gratuito."""
    return _get("/saude")


if __name__ == "__main__":
    mcp.run()
