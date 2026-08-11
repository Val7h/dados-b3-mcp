# Dados B3 — servidor MCP

Conector [MCP](https://modelcontextprotocol.io) que dá ao seu agente de IA
(Claude, ChatGPT e outros) acesso a **dados fundamentalistas de 402 companhias
abertas brasileiras (B3), de 2010 até hoje**, com **metodologia pública**:
ROIC, ROE, margens, crescimento, dívida líquida/EBITDA e **múltiplos
ponto-no-tempo** (P/L, P/VP, EV/EBITDA calculados com o preço do 1º pregão
*após a publicação real do balanço* — sem look-ahead, próprio para backtest).

Fonte dos dados: CVM (dados abertos, licença ODbL) e B3 (COTAHIST). Cada número
carrega a conta CVM de origem; nenhum é publicado sem uma bateria de testes de
invariantes passando. Produto e planos: **https://dados-b3.onrender.com**

## Uso 1 — remoto (nada para instalar, recomendado)

Adicione este conector remoto ao seu cliente de IA:

```
https://dados-b3.onrender.com/mcp/
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
| `listar_empresas` | 402 companhias (nome, CNPJ, ticker) | sim |
| `indicadores_anuais` | ROIC, ROE, margens, crescimento, DL/EBITDA (16 anos) | WEGE3 sim; demais com chave |
| `multiplos` | P/L, P/VP, EV/EBITDA ponto-no-tempo; P/L TTM | WEGE3 sim; demais com chave |
| `fatos_contabeis` | contas padronizadas com origem CVM (anual/trimestral) | WEGE3 sim; demais com chave |
| `metodologia` | fórmulas públicas de cada indicador | sim |
| `saude` | cobertura atual do banco | sim |

A empresa **WEGE3** e a **metodologia** são abertas para degustação, sem chave.
Para as demais empresas, crie uma **chave grátis** (200 consultas/dia, sem
cartão) ou assine o **Pro** (R$ 49,90/mês) em https://dados-b3.onrender.com e
passe a chave no argumento `chave_api` (ou na variável `DADOS_B3_API_KEY`).

## Por que este e não outro

Metodologia 100% pública, testes de invariantes antes de cada publicação,
múltiplos sem vazamento de informação futura, e histórico de reapresentações
registrado — coisas que nenhuma API de dados da B3 fazia. Comparativo honesto
(inclusive onde os concorrentes são melhores):
https://dados-b3.onrender.com/comparativo

## Licença

MIT (este conector). Os dados são públicos (CVM/B3); o serviço adiciona
padronização, metodologia e testes.
