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
VERSAO = "1.2.0"

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
def dividendos(ticker: str, chave_api: str = "") -> dict:
    """Proventos em dinheiro pagos por uma empresa da B3, com dividend yield.

    Devolve cada provento (dividendo ou JCP) com valor por ação, data-com e
    data de aprovação, mais o resumo por ano e o dividend yield dos últimos 12
    meses. A fonte é a própria B3, e o registro guarda o tipo original
    declarado por ela, não só o normalizado.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3", "PETR4", "SANB11". Veja `listar_empresas`.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para as demais. Deixe "" para usar a variável
        de ambiente DADOS_B3_API_KEY, quando existir.

    Ausência de provento e ausência de informação são coisas diferentes aqui:
    a resposta distingue "a B3 respondeu que não houve" de "não conseguimos
    perguntar", em vez de devolver zero para os dois casos."""
    return _get(f"/empresas/{ticker}/dividendos", chave_api)


@mcp.tool()
def scores(ticker: str, chave_api: str = "") -> dict:
    """Scores de qualidade e de valor de uma empresa da B3, critério por critério.

    Devolve o Piotroski F-Score (0 a 9) com **cada um dos nove critérios
    aberto**, dizendo qual passou e com que número, e o critério de Graham.
    O objetivo é poder discordar do score: você vê a conta, não só a nota.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3", "PETR4", "SANB11". Veja `listar_empresas`.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para as demais. Deixe "" para usar a variável
        de ambiente DADOS_B3_API_KEY, quando existir."""
    return _get(f"/empresas/{ticker}/scores", chave_api)


@mcp.tool()
def reapresentacoes(ticker: str, chave_api: str = "") -> dict:
    """Balanços que a empresa republicou depois, com as duas versões lado a lado.

    Quando uma companhia reapresenta um exercício já publicado, o número
    antigo costuma sumir das bases — aqui ele fica. Devolve, por conta
    afetada, o valor da versão original e o da versão nova, com as datas das
    duas publicações. Serve para auditar mudança de histórico e para saber se
    um backtest rodou sobre números que depois foram revistos.

    Parâmetros:
      ticker — código da ação na B3, em maiúsculas e com o dígito da classe.
        Exemplos: "WEGE3", "PETR4", "SANB11". Veja `listar_empresas`.
      chave_api — chave do Dados B3. Dispensável para WEGE3, aberta como
        degustação; necessária para as demais. Deixe "" para usar a variável
        de ambiente DADOS_B3_API_KEY, quando existir."""
    return _get(f"/empresas/{ticker}/reapresentacoes", chave_api)


@mcp.tool()
def screener(filtros: dict[str, float] | None = None, ano: int = 0,
             limite: int = 100, chave_api: str = "") -> dict:
    """Filtra o universo inteiro da B3 por faixas de indicadores.

    Parâmetros:
      filtros — dicionário de faixas. Cada chave é o nome de um indicador
        seguido de `_min` ou `_max`, e o valor é o número da faixa. Frações,
        não porcentagens: ROIC de 15% é 0.15.
        Exemplo: {"roic_min": 0.15, "dl_ebitda_max": 2}
        Indicadores aceitos: roic, roe, margem_bruta, margem_ebit,
        margem_liquida, dl_ebitda, cresc_receita_1a, cresc_receita_5a_cagr,
        piotroski.
        Chame SEM filtros para receber o cardápio: a lista de indicadores
        válidos e exemplos de uso.
      ano — exercício alvo. 0 (padrão) usa, para cada empresa, o último ano
        com dado disponível — que não é o mesmo ano para todas.
      limite — máximo de empresas na resposta. Padrão 100.
      chave_api — obrigatória aqui, mesmo para WEGE3, porque a consulta
        percorre todo o universo. Deixe "" para usar DADOS_B3_API_KEY.

    Só entram valores SEM flag, isto é, números que passaram limpos pela
    bateria de invariantes. Um indicador marcado como suspeito não é filtrado
    silenciosamente: ele simplesmente não participa. Nome de indicador
    desconhecido é recusado com erro, nunca ignorado."""
    q = []
    for chave, valor in (filtros or {}).items():
        q.append(f"{chave}={valor}")
    if ano:
        q.append(f"ano={ano}")
    q.append(f"limite={limite}")
    return _get("/screener?" + "&".join(q), chave_api)


@mcp.tool()
def dicionario() -> dict:
    """Dicionário técnico dos indicadores: fórmula, contas CVM e base do lucro.

    Devolve, para cada indicador que o Dados B3 publica, a fórmula exata, os
    códigos de conta CVM que entram nela, e qual linha de lucro é usada como
    base. É o mapa que permite recalcular qualquer número à mão a partir dos
    documentos originais.

    Sem parâmetros. Gratuito — não exige chave.

    Diferença para `metodologia`: aqui vem a definição em JSON, própria para
    um programa consumir; lá vem o texto explicativo, próprio para leitura."""
    return _get("/dicionario")


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
