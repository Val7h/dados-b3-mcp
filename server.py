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

# Versão DESTE servidor, anunciada no handshake MCP. Sem ela o SDK publica a
# versão do próprio pacote `mcp` (`server_version=self.version if self.version
# else pkg_version("mcp")`), e qualquer cliente que inspecione o conector vê o
# número do SDK achando que é o nosso. FastMCP não aceita `version=` no
# construtor — o campo mora no servidor de baixo nível que ele embrulha.
VERSAO = "1.1.0"

mcp = FastMCP("dados-b3")
mcp._mcp_server.version = VERSAO


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
    """Lista as companhias abertas brasileiras cobertas pelo Dados B3.

    Devolve, para cada empresa: nome, CNPJ, código CVM e ticker principal,
    mais a contagem total. É o ponto de partida para descobrir qual ticker
    passar nas outras ferramentas.

    Sem parâmetros. Gratuito — não exige chave.

    A contagem não fica escrita nesta descrição de propósito: o universo
    cresce quando a CVM publica, e um número congelado aqui envelheceria sem
    ninguém ver. Para o número de hoje, chame `saude`."""
    return _get("/empresas")


@mcp.tool()
def indicadores_anuais(ticker: str, chave_api: str = "") -> dict:
    """Série anual de indicadores fundamentalistas de uma empresa da B3.

    Cobre de 2010 até o último exercício publicado e devolve, por ano: ROIC,
    ROE, margens (bruta, EBIT e líquida), crescimento de receita e de lucro, e
    dívida líquida/EBITDA. Para saber como cada um é calculado, chame
    `metodologia`.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3" (ordinária), "PETR4" (preferencial), "SANB11"
        (unit). Use `listar_empresas` para descobrir os disponíveis.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para qualquer outra empresa. Deixe "" para usar
        a variável de ambiente DADOS_B3_API_KEY, quando existir. Sem chave
        válida a resposta vem com o campo `erro` explicando como obter uma."""
    return _get(f"/empresas/{ticker}/indicadores", chave_api)


@mcp.tool()
def multiplos(ticker: str, chave_api: str = "") -> dict:
    """Múltiplos de avaliação ponto-no-tempo de uma empresa da B3.

    Devolve P/L, P/VP e EV/EBITDA por exercício, mais P/L TTM por trimestre.

    O preço usado é o do primeiro pregão APÓS a data real de publicação do
    balanço — não o fechamento do exercício, que ninguém conhecia naquela
    data. É essa escolha que elimina o look-ahead e permite usar a série em
    backtest sem contaminar o passado.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3", "PETR4", "SANB11". Veja `listar_empresas`.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para as demais. Deixe "" para usar a variável
        de ambiente DADOS_B3_API_KEY, quando existir."""
    return _get(f"/empresas/{ticker}/multiplos", chave_api)


@mcp.tool()
def fatos_contabeis(ticker: str, trimestral: bool = False, chave_api: str = "") -> dict:
    """Contas contábeis padronizadas de uma empresa da B3, com a origem de cada número.

    Devolve, por período: receita, EBIT, lucro líquido, patrimônio líquido,
    caixa, dívida bruta e dívida líquida, entre outras — e, junto de cada
    valor, o código da conta CVM de onde ele saiu, para auditoria.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3", "PETR4", "SANB11". Veja `listar_empresas`.
      trimestral — escolhe a granularidade da série, e só isso. False (padrão)
        devolve os exercícios ANUAIS, vindos dos formulários DFP; True devolve
        os TRIMESTRES, vindos dos ITR. Não é um filtro: os dois modos cobrem o
        mesmo histórico, muda apenas o período de cada linha.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para as demais. Deixe "" para usar a variável
        de ambiente DADOS_B3_API_KEY, quando existir."""
    return _get(f"/empresas/{ticker}/fatos?trimestral={str(trimestral).lower()}",
                chave_api)


@mcp.tool()
def metodologia(nome: str = "") -> dict:
    """Metodologia pública por trás dos indicadores — como cada número é calculado.

    Tem dois modos, conforme o argumento:
      - sem `nome` (padrão): devolve a LISTA das páginas disponíveis, com o
        identificador de cada uma;
      - com `nome`: devolve o TEXTO completo daquela página, em Markdown.

    Parâmetros:
      nome — identificador da página, exatamente como aparece na listagem.
        Exemplo: "roic". Deixe "" para listar em vez de ler.

    Gratuito — não exige chave. Use quando precisar auditar ou justificar um
    número devolvido pelas outras ferramentas."""
    if not nome:
        return _get("/metodologia")
    return {"nome": nome, "conteudo": httpx.get(
        f"{API}/metodologia/{nome}.md", timeout=30).text}


@mcp.tool()
def saude() -> dict:
    """Estado atual da base do Dados B3: o que está coberto e quão fresco está.

    Devolve as contagens por tipo de dado (empresas, fatos anuais e
    trimestrais, indicadores, múltiplos e preços) e a data-hora da última
    ingestão. Serve para saber o tamanho do universo hoje e para conferir se a
    base foi atualizada antes de confiar num número.

    Sem parâmetros. Gratuito — não exige chave."""
    return _get("/saude")


if __name__ == "__main__":
    mcp.run()
