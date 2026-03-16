#!/usr/bin/env python3
"""Script principal que coordena o scraping dos três CEASAs e gera o JSON de dados."""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório de scripts ao path
sys.path.insert(0, str(Path(__file__).parent))

import ceasa_pr_scraper
import ceasa_sc_scraper
import ceasa_rs_scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Diretório de saída dos dados
OUTPUT_DIR = Path(__file__).parent.parent / "client" / "public" / "data"


def calcular_variacoes(dados_hoje: list[dict], dados_ontem: list[dict]) -> list[dict]:
    """Calcula variações de preço entre hoje e ontem."""
    # Criar dicionário de preços de ontem
    precos_ontem = {c["produto"]: c["preco"] for c in dados_ontem}

    variacoes = []
    for cotacao in dados_hoje:
        produto = cotacao["produto"]
        preco_hoje = cotacao["preco"]
        preco_ontem = precos_ontem.get(produto)

        if preco_ontem and preco_ontem > 0:
            variacao_pct = ((preco_hoje - preco_ontem) / preco_ontem) * 100
            cotacao["preco_anterior"] = preco_ontem
            cotacao["variacao_pct"] = round(variacao_pct, 2)
            cotacao["aumentou"] = variacao_pct > 0
            cotacao["diminuiu"] = variacao_pct < 0
        else:
            cotacao["preco_anterior"] = None
            cotacao["variacao_pct"] = None
            cotacao["aumentou"] = False
            cotacao["diminuiu"] = False

        variacoes.append(cotacao)

    return variacoes


def carregar_dados_anteriores(estado: str) -> list[dict]:
    """Carrega dados do dia anterior para comparação."""
    historico_file = OUTPUT_DIR / f"historico_{estado.lower()}.json"
    if historico_file.exists():
        try:
            with open(historico_file, "r", encoding="utf-8") as f:
                historico = json.load(f)
            if historico and len(historico) > 0:
                return historico[-1].get("cotacoes", [])
        except Exception as e:
            logger.warning(f"Erro ao carregar histórico de {estado}: {e}")
    return []


def salvar_historico(estado: str, dados: dict):
    """Salva dados no histórico para comparação futura."""
    historico_file = OUTPUT_DIR / f"historico_{estado.lower()}.json"
    historico = []

    if historico_file.exists():
        try:
            with open(historico_file, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except Exception:
            historico = []

    # Manter apenas os últimos 30 dias
    historico.append({"data": dados["data"], "cotacoes": dados["cotacoes"]})
    historico = historico[-30:]

    with open(historico_file, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def main():
    """Executa scraping de todos os CEASAs e gera arquivo JSON."""
    logger.info("Iniciando scraping dos CEASAs...")

    # Criar diretório de saída
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resultados = []
    scrapers = [
        ("PR", ceasa_pr_scraper.scrape),
        ("SC", ceasa_sc_scraper.scrape),
        ("RS", ceasa_rs_scraper.scrape),
    ]

    for estado, scraper_fn in scrapers:
        logger.info(f"Coletando dados do CEASA {estado}...")
        try:
            dados = scraper_fn()

            # Carregar dados anteriores para comparação
            dados_anteriores = carregar_dados_anteriores(estado)

            # Calcular variações
            if dados.get("cotacoes") and dados_anteriores:
                dados["cotacoes"] = calcular_variacoes(
                    dados["cotacoes"], dados_anteriores
                )
            else:
                # Sem dados anteriores, marcar tudo sem variação
                for c in dados.get("cotacoes", []):
                    c.setdefault("preco_anterior", None)
                    c.setdefault("variacao_pct", None)
                    c.setdefault("aumentou", False)
                    c.setdefault("diminuiu", False)

            # Calcular resumo de aumentos
            cotacoes = dados.get("cotacoes", [])
            aumentos = [c for c in cotacoes if c.get("aumentou")]
            diminuicoes = [c for c in cotacoes if c.get("diminuiu")]

            dados["total_produtos"] = len(cotacoes)
            dados["total_aumentos"] = len(aumentos)
            dados["total_diminuicoes"] = len(diminuicoes)
            dados["aumentos"] = [
                {
                    "produto": c["produto"],
                    "preco": c["preco"],
                    "preco_anterior": c["preco_anterior"],
                    "variacao_pct": c["variacao_pct"],
                }
                for c in sorted(aumentos, key=lambda x: x.get("variacao_pct", 0), reverse=True)
            ]

            # Salvar histórico
            if cotacoes:
                salvar_historico(estado, dados)

            resultados.append(dados)
            logger.info(
                f"CEASA {estado}: {len(cotacoes)} produtos, "
                f"{len(aumentos)} aumentos, {len(diminuicoes)} quedas"
            )

        except Exception as e:
            logger.error(f"Erro no scraper do CEASA {estado}: {e}")
            resultados.append(
                {
                    "estado": estado,
                    "nome": f"CEASA {estado}",
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "cotacoes": [],
                    "aumentos": [],
                    "total_produtos": 0,
                    "total_aumentos": 0,
                    "total_diminuicoes": 0,
                    "erro": str(e),
                }
            )

    # Salvar resultado final
    output = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "estados": resultados,
    }

    output_file = OUTPUT_DIR / "cotacoes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"Dados salvos em {output_file}")
    return output


if __name__ == "__main__":
    result = main()
    total = sum(e.get("total_produtos", 0) for e in result["estados"])
    aumentos = sum(e.get("total_aumentos", 0) for e in result["estados"])
    print(f"\nResumo: {total} produtos coletados, {aumentos} com aumento de preço")
