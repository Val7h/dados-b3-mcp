# Dados B3 — MCP server (Brazilian stock market, auditable fundamentals)

*[Português abaixo](#dados-b3--servidor-mcp-bolsa-brasileira-fundamentos-auditáveis)*

An [MCP](https://modelcontextprotocol.io) connector that gives your AI agent
(Claude, ChatGPT, Cursor and others) access to **fundamentals for Brazilian
listed companies (B3) — banks and insurers included — from 2010 to today**,
with a **fully published methodology**: ROE, ROIC, margins, growth, net
debt/EBITDA, **point-in-time multiples** (P/E, P/B, EV/EBITDA priced at the
first trading session *after* the filing actually became public — no
look-ahead, usable for backtests), **dividends and dividend yield**,
**ready-made scores (Piotroski F-Score and Graham)** and a **record of restated
filings**.

Sources: CVM open data (ODbL) and B3 (COTAHIST). Every figure carries the CVM
account it came from, and **nothing is published unless a suite of invariant
tests passes** — the balance sheet balances, the income statement reconciles,
and a price never precedes the filing that justifies it.

Product and plans: **https://dadosb3.com**

## Use 1 — remote (nothing to install, recommended)

Add this remote connector to your AI client:

```
https://dadosb3.com/mcp/
```

In Claude: Settings → Connectors → add custom connector → paste the URL.

## Use 2 — local (stdio)

```bash
pip install -r requirements.txt
python server.py
```

```json
{
  "mcpServers": {
    "dados-b3": {
      "command": "python",
      "args": ["server.py"],
      "env": { "DADOS_B3_API_KEY": "your_optional_key" }
    }
  }
}
```

## Use 3 — Docker image (one command, no local Python)

```bash
docker run -i --rm -e DADOS_B3_API_KEY=your_optional_key ghcr.io/val7h/dados-b3-mcp:latest
```

```json
{
  "mcpServers": {
    "dados-b3": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/val7h/dados-b3-mcp:latest"]
    }
  }
}
```

The image is published on every push to `main`
(`.github/workflows/publicar-imagem.yml`). It exists for two reasons: a
one-command install path, and letting MCP directories actually run the server
in order to evaluate it.

## Tools

| Tool | What it does | Free? |
|---|---|---|
| `listar_empresas` | Every covered company (name, tax ID, ticker), banks and insurers included | yes |
| `indicadores_anuais` | ROE, ROIC, margins, growth, net debt/EBITDA — annual series from 2010 | WEGE3 yes; others need a key |
| `multiplos` | P/E, P/B, EV/EBITDA point-in-time; trailing P/E | WEGE3 yes; others need a key |
| `fatos_contabeis` | Standardised accounts carrying the CVM code each figure came from | WEGE3 yes; others need a key |
| `dividendos` | Cash distributions, annual summary and 12-month dividend yield | WEGE3 yes; others need a key |
| `scores` | Piotroski F-Score with all nine criteria shown, plus the Graham test | WEGE3 yes; others need a key |
| `reapresentacoes` | Restated filings — the original and the revised figure side by side | WEGE3 yes; others need a key |
| `screener` | Filters the whole market by indicator ranges | key required |
| `dicionario` | Formula, CVM accounts and earnings base of each indicator, as JSON | yes |
| `metodologia` | The published methodology pages, as text | yes |
| `saude` | Current coverage and last ingestion | yes |

**WEGE3** and the **whole methodology** are open, no key needed. For other
companies, create a **free key** (200 queries/day, no card) or subscribe to
**Pro** at https://dadosb3.com, and pass it in the `chave_api` argument or the
`DADOS_B3_API_KEY` environment variable.

The company count is deliberately not written here: the universe grows whenever
the CVM publishes, and a number frozen in a README ages without anyone
noticing. Call `saude` for today's figure.

## Banks and insurers

Financial institutions file under a different chart of accounts — there is no
EBIT and no sales revenue. The connector classifies them by their actual chart
of accounts and returns the indicators that mean something for them — **ROE,
margin, growth, P/E, P/B, dividends** — and deliberately does **not** publish
ROIC, EBITDA or EV/EBITDA for them, because those do not apply. Examples: Itaú,
Bradesco, Banco do Brasil, BB Seguridade, IRB.

## Why this one

A methodology published rather than described, invariant tests gating every
release, multiples with no future information leaking in, and **restatements
kept on the record** — when a company republishes a filing, both versions stay
side by side. An honest comparison, including where competitors are better:
**https://dadosb3.com/comparativo**

## Licence

MIT (this connector). The underlying data is public (CVM/B3); the service adds
standardisation, methodology and tests.

---

# Dados B3 — servidor MCP (bolsa brasileira, fundamentos auditáveis)

Conector [MCP](https://modelcontextprotocol.io) que dá ao seu agente de IA
(Claude, ChatGPT, Cursor e outros) acesso a **dados fundamentalistas das
companhias abertas brasileiras (B3) — inclusive bancos e seguradoras —, de 2010
até hoje**, com **metodologia 100% pública**: ROE, ROIC, margens, crescimento,
dívida líquida/EBITDA, **múltiplos ponto-no-tempo** (P/L, P/VP, EV/EBITDA com o
preço do 1º pregão *após a publicação real do balanço* — sem look-ahead,
próprio para backtest), **dividendos e dividend yield**, **scores prontos
(Piotroski F-Score e Graham)** e **histórico de reapresentações de balanço**.

Fonte: CVM (dados abertos, ODbL) e B3 (COTAHIST). Cada número carrega a conta
CVM de origem; **nada é publicado sem uma bateria de testes de invariantes
passando** (o balanço fecha, a DRE fecha, o preço nunca antecede a publicação).

Produto e planos: **https://dadosb3.com**

## Uso 1 — remoto (nada para instalar, recomendado)

Adicione este conector remoto ao seu cliente de IA:

```
https://dadosb3.com/mcp/
```

No Claude: Configurações → Conectores → adicionar conector personalizado → cole a URL.

## Uso 2 — local (stdio)

```bash
pip install -r requirements.txt
python server.py
```

## Uso 3 — imagem Docker (um comando, sem Python local)

```bash
docker run -i --rm -e DADOS_B3_API_KEY=sua_chave_opcional ghcr.io/val7h/dados-b3-mcp:latest
```

A imagem é publicada a cada push na `main`. Ela existe por dois motivos: dar um
caminho de instalação de um comando só, e permitir que diretórios de MCP rodem
o servidor para avaliá-lo.

## Ferramentas

| Ferramenta | O que faz | Grátis? |
|---|---|---|
| `listar_empresas` | Todas as companhias cobertas (nome, CNPJ, ticker), incl. bancos e seguradoras | sim |
| `indicadores_anuais` | ROE, ROIC, margens, crescimento, DL/EBITDA — série anual desde 2010 | WEGE3 sim; demais com chave |
| `multiplos` | P/L, P/VP, EV/EBITDA ponto-no-tempo; P/L TTM | WEGE3 sim; demais com chave |
| `fatos_contabeis` | Contas padronizadas com a conta CVM de origem de cada número | WEGE3 sim; demais com chave |
| `dividendos` | Proventos, resumo anual e dividend yield de 12 meses | WEGE3 sim; demais com chave |
| `scores` | Piotroski F-Score com os nove critérios abertos, e o critério de Graham | WEGE3 sim; demais com chave |
| `reapresentacoes` | Balanços republicados — versão original e revisada lado a lado | WEGE3 sim; demais com chave |
| `screener` | Filtra o mercado inteiro por faixas de indicadores | exige chave |
| `dicionario` | Fórmula, contas CVM e base do lucro de cada indicador, em JSON | sim |
| `metodologia` | As páginas de metodologia publicadas, em texto | sim |
| `saude` | Cobertura atual e última ingestão | sim |

A empresa **WEGE3** e a **metodologia** são abertas para degustação, sem chave.
Para as demais, crie uma **chave grátis** (200 consultas/dia, sem cartão) ou
assine o **Pro** em https://dadosb3.com e passe a chave no argumento
`chave_api` (ou na variável `DADOS_B3_API_KEY`).

A contagem de empresas não fica escrita aqui de propósito: o universo cresce
quando a CVM publica, e um número congelado num README envelheceria sem
ninguém ver. Para o número de hoje, chame `saude`.

## Bancos e seguradoras

Instituições financeiras têm plano de contas próprio (não há EBIT nem receita
de venda). O conector as classifica pelo plano de contas real e entrega os
indicadores que fazem sentido — **ROE, margem, crescimento, P/L, P/VP,
dividendos** — e **não** publica ROIC/EBITDA/EV-EBITDA para elas (não se
aplicam). Ex.: Itaú, Bradesco, Banco do Brasil, BB Seguridade, IRB.

## Por que este e não outro

Metodologia 100% pública, testes de invariantes antes de cada publicação,
múltiplos sem vazamento de informação futura, e **histórico de reapresentações
registrado**. Comparativo honesto, inclusive onde os concorrentes são
melhores: **https://dadosb3.com/comparativo**

## Licença

MIT (este conector). Os dados são públicos (CVM/B3); o serviço adiciona
padronização, metodologia e testes.
