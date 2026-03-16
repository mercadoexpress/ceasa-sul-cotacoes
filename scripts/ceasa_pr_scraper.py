#!/usr/bin/env python3
"""Scraper para cotações do CEASA Paraná."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

URL = "https://celepar7.pr.gov.br/ceasa/hoje.asp"
CIDADES = ["Curitiba", "Maringá", "Londrina", "Foz do Iguaçu", "Cascavel"]


def parse_preco(valor: str) -> float | None:
    """Converte string de preço para float."""
    if not valor or valor.strip() == "-":
        return None
    val = valor.strip().replace(".", "").replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def scrape() -> dict:
    """Coleta cotações do CEASA PR."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = "latin-1"
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")

        # Extrair data da primeira tabela
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        if tables:
            header_text = tables[0].get_text()
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", header_text)
            if date_match:
                data_hoje = date_match.group(1)

        cotacoes = []

        if len(tables) < 2:
            logger.warning("CEASA PR: tabela de cotações não encontrada")
            return {"estado": "PR", "data": data_hoje, "cotacoes": [], "fonte": URL}

        tabela = tables[1]
        rows = tabela.find_all("tr")

        for row in rows[2:]:  # Pular cabeçalhos
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue

            produto_raw = cells[0]
            if not produto_raw or produto_raw.startswith("PRODUTO"):
                continue

            # Parsear produto: "NOME VARIEDADE CLASSE embalagem peso"
            produto_nome = produto_raw

            # Preços por cidade (células 1-5)
            precos_cidades = {}
            for i, cidade in enumerate(CIDADES):
                idx = i + 1
                if idx < len(cells):
                    preco = parse_preco(cells[idx])
                    if preco is not None:
                        precos_cidades[cidade] = preco

            if not precos_cidades:
                continue

            # Preço mais comum (primeiro disponível)
            preco_comum = list(precos_cidades.values())[0]

            cotacoes.append(
                {
                    "produto": produto_nome,
                    "preco": preco_comum,
                    "precos_cidades": precos_cidades,
                    "unidade": "R$",
                }
            )

        logger.info(f"CEASA PR: {len(cotacoes)} cotações coletadas em {data_hoje}")
        return {
            "estado": "PR",
            "nome": "CEASA Paraná",
            "data": data_hoje,
            "cotacoes": cotacoes,
            "fonte": URL,
        }

    except Exception as e:
        logger.error(f"Erro ao coletar CEASA PR: {e}")
        return {
            "estado": "PR",
            "nome": "CEASA Paraná",
            "data": datetime.now().strftime("%d/%m/%Y"),
            "cotacoes": [],
            "erro": str(e),
            "fonte": URL,
        }


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    dados = scrape()
    print(json.dumps(dados, ensure_ascii=False, indent=2))
