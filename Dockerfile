# Servidor MCP stdio do Dados B3 — um proxy fino que chama a API pública por
# HTTP. Usado por diretórios (Glama) para rodar e introspectar as ferramentas,
# e por quem quiser embutir o conector localmente. O uso RECOMENDADO é o
# conector remoto https://dadosb3.com/mcp/ (nada para instalar).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./

# Servidor MCP stdio. A base da API pode ser trocada por env (DADOS_B3_API);
# a chave, quando necessária, vai em DADOS_B3_API_KEY ou no argumento chave_api.
ENV DADOS_B3_API=https://dadosb3.com
CMD ["python", "server.py"]
