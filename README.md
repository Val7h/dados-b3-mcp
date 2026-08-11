# Dados B3 — servidor MCP (bolsa brasileira, fundamentos auditáveis)

Conector [MCP](https://modelcontextprotocol.io) que dá ao seu agente de IA
(Claude, ChatGPT, Cursor e outros) acesso a **dados fundamentalistas de 400+
companhias abertas brasileiras (B3) — inclusive bancos e seguradoras —, de 2010
até hoje**, com **metodologia 100% pública**: ROE, ROIC, margens, crescimento,
dívida líquida/EBITDA, **múltiplos ponto-no-tempo** (P/L, P/VP, EV/EBITDA com o
preço do 1º pregão *após a publicação real do balanço* — sem look-ahead, próprio
para backtest), **dividendos e dividend yield**, **scores prontos (Piotroski
F-Score e Graham)** e **histórico de reapresentações de balanço**.

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

Config de exemplo para um cliente MCP local:

```json
{
  "mcpServers": {
    "dados-b3": {
      "command": "python",
      "args": ["server.py"],
      "env": { "DADOS_B3_API_KEY": "sua_chave_opcional" }
    }
  }
}
```

## Ferramentas

| Ferramenta | O que faz | Grátis? |
|---|---|---|
| `listar_empresas` | 400+ companhias, incl. bancos/seguradoras (nome, CNPJ, ticker) | sim |
| `indicadores_anuais` | ROE, ROIC, margens, crescimento, DL/EBITDA (16 anos) | WEGE3 sim; demais com chave |
| `multiplos` | P/L, P/VP, EV/EBITDA ponto-no-tempo; P/L TTM | WEGE3 sim; demais com chave |
| `dividendos` | proventos, resumo anual e **dividend yield 12m** | WEGE3 sim; demais com chave |
| `scores` | **Piotroski F-Score (0-9, cada critério aberto)** e critério de Graham | WEGE3 sim; demais com chave |
| `reapresentacoes` | **balanços republicados** — versão antiga × nova lado a lado | WEGE3 sim; demais com chave |
| `fatos_contabeis` | contas padronizadas com a conta CVM de origem (anual/trimestral) | WEGE3 sim; demais com chave |
| `screener` | filtra as empresas por faixas de indicadores | com chave |
| `dicionario` | fórmula, conta CVM e base do lucro de cada indicador (JSON) | sim |
| `metodologia` | fórmulas públicas de cada indicador | sim |
| `saude` | cobertura atual do banco | sim |

A empresa **WEGE3** e a **metodologia** são abertas para degustação, sem chave.
Para as demais, crie uma **chave grátis** (200 consultas/dia, sem cartão) ou
assine o **Pro** (R$ 49,90/mês) em https://dadosb3.com e passe a chave no
argumento `chave_api` (ou na variável `DADOS_B3_API_KEY`).

## Bancos e seguradoras

Instituições financeiras têm plano de contas próprio (não há EBIT nem receita de
venda). O conector as classifica pelo plano de contas real e entrega os
indicadores que fazem sentido — **ROE, margem, crescimento, P/L, P/VP,
dividendos** — e **não** publica ROIC/EBITDA/EV-EBITDA para elas (não se
aplicam). Ex.: Itaú, Bradesco, Banco do Brasil, BB Seguridade, IRB.

## Por que este e não outro

Metodologia 100% pública, testes de invariantes antes de cada publicação,
múltiplos sem vazamento de informação futura, e **histórico de reapresentações
registrado** (quando a empresa republica um balanço, as duas versões ficam
lado a lado) — coisas que nenhuma outra API de dados da B3 faz. Comparativo
honesto, inclusive onde os concorrentes são melhores:
**https://dadosb3.com/comparativo**

## Licença

MIT (este conector). Os dados são públicos (CVM/B3); o serviço adiciona
padronização, metodologia e testes.
