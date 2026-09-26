"""Testes do servidor MCP local — sem rede: `_get` é substituído.

O que eles prendem: a versão anunciada no handshake é a mesma do server.json
e da imagem; toda ferramenta registrada aparece nas duas tabelas do README
(EN e PT); os links do README para o site carregam `?de=github` (menos o
endereço do conector); e as ferramentas da 1.7.0 chamam a rota certa.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import server  # noqa: E402


def _ferramentas() -> list[str]:
    return sorted(t.name for t in asyncio.run(server.mcp.list_tools()))


def test_versao_anunciada_e_a_do_server_json_e_da_imagem():
    j = json.loads((RAIZ / "server.json").read_text(encoding="utf-8"))
    assert server.VERSAO == j["version"]
    assert server.mcp._mcp_server.version == server.VERSAO
    assert all(p["identifier"].endswith(":" + server.VERSAO) for p in j["packages"])


def test_ferramentas_da_1_7_0_existem():
    nomes = _ferramentas()
    for n in ("veredito", "recibo", "screener"):
        assert n in nomes, nomes


def test_toda_ferramenta_esta_nas_duas_tabelas_do_readme():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for n in _ferramentas():
        linhas = [l for l in readme.splitlines() if l.startswith(f"| `{n}` |")]
        assert len(linhas) == 2, f"`{n}` precisa de uma linha na tabela EN e outra na PT: {linhas}"


def test_links_do_readme_para_o_site_carregam_a_origem():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"https://dadosb3\.com[^\s)*`>,]*", readme)
    assert links
    for l in links:
        if l.rstrip("/").endswith("/mcp"):
            continue            # o endereço do conector não leva marca
        assert "de=github" in l, l


@pytest.fixture
def chamadas(monkeypatch):
    feitas = []

    def falso(caminho, chave_api="", **params):
        feitas.append((caminho, chave_api))
        return {"ok": True}
    monkeypatch.setattr(server, "_get", falso)
    return feitas


def test_veredito_chama_a_rota_aberta_do_papel(chamadas):
    assert server.veredito(" wege3 ") == {"ok": True}
    assert chamadas == [("/empresas/WEGE3/veredito", "")]


def test_recibo_aceita_id_endereco_ou_json(chamadas):
    server.recibo("abc123")
    server.recibo("https://dadosb3.com/recibo/abc123")
    server.recibo("abc123.json")
    assert [c[0] for c in chamadas] == ["/recibo/abc123"] * 3
    assert "erro" in server.recibo("  ")


def test_screener_pede_recibo_e_as_of_so_quando_pedido(chamadas):
    server.screener({"roic_min": 0.15}, as_of="2024-06-30", recibo=True, chave_api="k")
    server.screener({"roic_min": 0.15})
    com, sem = chamadas[0][0], chamadas[1][0]
    assert "as_of=2024-06-30" in com and "recibo=true" in com and "roic_min=0.15" in com
    assert "recibo" not in sem and "as_of" not in sem
    assert chamadas[0][1] == "k"


def test_mensagem_de_chave_aponta_para_a_chave_gratis_marcada(monkeypatch):
    class R:
        status_code = 401
    monkeypatch.setattr(server.httpx, "get", lambda *a, **k: R())
    r = server._get("/empresas/PETR4/indicadores")
    assert "chave-gratis?de=mcp" in r["como_resolver"]
