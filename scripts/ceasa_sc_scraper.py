#!/usr/bin/env python3
"""Scraper para cotações do CEASA Santa Catarina."""

import requests
from bs4 import BeautifulSoup
import pdfplumber
import re
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://www.ceasa.sc.gov.br"
COTACOES_URL = "https://www.ceasa.sc.gov.br/index.php/cotacao-de-precos"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

MONTH_SLUGS = {
    1: "01-janeiro", 2: "02-fevereiro", 3: "03-marco",
    4: "04-abril", 5: "05-maio", 6: "06-junho",
    7: "07-julho", 8: "08-agosto", 9: "09-setembro",
    10: "10-outubro", 11: "11-novembro", 12: "12-dezembro"
}


def get_year_url(year: int) -> str:
    """Retorna a URL do ano no CEASA SC."""
    # 2026 usa sufixo -1, anos anteriores sem sufixo
    if year == 2026:
        return f"{COTACOES_URL}/2026-1"
    return f"{COTACOES_URL}/{year}"


def get_latest_pdf_url() -> tuple[str | None, str | None]:
    """Obtém a URL do PDF mais recente de cotações do CEASA SC."""
    try:
        now = datetime.now()
        year = now.year
        month = now.month

        # Tentar mês atual e depois mês anterior
        for attempt_month in [month, month - 1 if month > 1 else 12]:
            attempt_year = year if attempt_month <= month else year - 1
            month_slug = MONTH_SLUGS.get(attempt_month, f"{attempt_month:02d}")
            year_url = get_year_url(attempt_year)

            # Primeiro, obter a URL correta do mês na página do ano
            r_year = requests.get(year_url, headers=HEADERS, timeout=30)
            if r_year.status_code != 200:
                continue

            soup_year = BeautifulSoup(r_year.text, "html.parser")
            month_url = None

            # Procurar link do mês atual
            for link in soup_year.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if month_slug in href.lower() or (
                    str(attempt_month).zfill(2) in href
                    and str(attempt_year) in href
                ):
                    month_url = BASE_URL + href if href.startswith("/") else href
                    break

            if not month_url:
                # Tentar URL direta
                month_url = f"{year_url}/{month_slug}"

            # Acessar página do mês
            r_month = requests.get(month_url, headers=HEADERS, timeout=30)
            if r_month.status_code != 200:
                # Tentar variações do slug
                for suffix in ["-16", "-15", "-14", "-13", ""]:
                    test_url = f"{year_url}/{month_slug}{suffix}"
                    r_test = requests.get(test_url, headers=HEADERS, timeout=30)
                    if r_test.status_code == 200:
                        r_month = r_test
                        month_url = test_url
                        break
                else:
                    continue

            soup_month = BeautifulSoup(r_month.text, "html.parser")
            links = soup_month.find_all("a", href=True)

            # Encontrar links de PDF com data
            pdf_links = []
            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)
                # Filtrar links de arquivo com data no formato DD-MM-YYYY
                if "/file" in href and re.search(r"\d{2}-\d{2}-\d{4}", text):
                    pdf_links.append((text, href))

            if pdf_links:
                # Ordenar por data (mais recente primeiro)
                def parse_link_date(item):
                    text, _ = item
                    m = re.search(r"(\d{2})-(\d{2})-(\d{4})", text)
                    if m:
                        try:
                            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                        except Exception:
                            pass
                    return datetime.min

                pdf_links.sort(key=parse_link_date, reverse=True)
                data_str, pdf_path = pdf_links[0]
                pdf_url = BASE_URL + pdf_path if pdf_path.startswith("/") else pdf_path
                logger.info(f"CEASA SC: PDF mais recente: {data_str} -> {pdf_url}")
                return pdf_url, data_str

        logger.warning("CEASA SC: nenhum PDF encontrado")
        return None, None

    except Exception as e:
        logger.error(f"Erro ao obter URL do PDF CEASA SC: {e}")
        return None, None


def parse_preco(valor: str) -> float | None:
    """Converte string de preço para float."""
    if not valor:
        return None
    val = valor.strip().replace(".", "").replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def parse_pdf_text(text: str) -> list[dict]:
    """Extrai cotações do texto de uma página do PDF."""
    cotacoes = []
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Pular linhas de cabeçalho
        skip_patterns = [
            "Governo do Estado", "Secretaria", "Centrais de Abastecimento",
            "Relatório", "Produto", "Preço", "Mínimo", "Unidade São José",
            "BR-", "Telefone", "Página", "CEASA/SC", "Pecuária",
            "Variedade", "Classificação", "Embalagem", "Conv.", "Kg",
        ]
        if any(skip in line for skip in skip_patterns):
            continue

        # Procurar por preços no formato "XXX,XX"
        precos = re.findall(r"\b\d{1,4}[.,]\d{2}\b", line)
        if len(precos) < 2:
            continue

        # Extrair nome do produto
        # O produto está no início da linha, antes dos números
        # Remover números e palavras de classificação do início
        produto_match = re.match(
            r'^([A-Za-záàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ][A-Za-záàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ\s\-\/\(\)]+)',
            line
        )
        if not produto_match:
            continue

        produto_raw = produto_match.group(1).strip()

        # Remover palavras de classificação do final
        classificacoes = [
            "Convenci", "Nacional", "Importado", "Organico", "Orgânico",
            "Caixa", "Saco", "Maço", "Unidade", "Kilo", "Bandeja",
            "Molho", "Grande", "Médio", "Médio(a)", "Pequeno", "Extra",
            "Tipo", "Primeira", "Segunda", "Comum", "Especial",
            "Avocado", "Liso", "Liso(a)", "Ananas", "Perola",
        ]
        produto_words = produto_raw.split()
        produto_final_words = []
        for w in produto_words:
            if w in classificacoes or w.lower() in [c.lower() for c in classificacoes]:
                break
            produto_final_words.append(w)

        produto_nome = " ".join(produto_final_words).strip()
        if not produto_nome or len(produto_nome) < 2:
            continue

        # Pegar preços: mínimo, comum, máximo
        preco_min = parse_preco(precos[0]) if len(precos) > 0 else None
        preco_comum = parse_preco(precos[1]) if len(precos) > 1 else None
        preco_max = parse_preco(precos[2]) if len(precos) > 2 else None

        if preco_comum is None and preco_min is not None:
            preco_comum = preco_min

        if preco_comum is None:
            continue

        cotacoes.append(
            {
                "produto": produto_nome.upper(),
                "preco": preco_comum,
                "preco_min": preco_min,
                "preco_max": preco_max,
                "unidade": "R$",
            }
        )

    return cotacoes


def parse_pdf(pdf_content: bytes) -> list[dict]:
    """Extrai cotações do PDF do CEASA SC."""
    cotacoes = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    page_cotacoes = parse_pdf_text(text)
                    cotacoes.extend(page_cotacoes)

    except Exception as e:
        logger.error(f"Erro ao parsear PDF CEASA SC: {e}")

    # Remover duplicatas mantendo o primeiro
    seen = set()
    unique = []
    for c in cotacoes:
        key = c["produto"]
        if key not in seen and key:
            seen.add(key)
            unique.append(c)

    return unique


def scrape() -> dict:
    """Coleta cotações do CEASA SC."""
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    try:
        pdf_url, data_str = get_latest_pdf_url()

        if not pdf_url:
            return {
                "estado": "SC",
                "nome": "CEASA Santa Catarina",
                "data": data_hoje,
                "cotacoes": [],
                "erro": "Não foi possível encontrar PDF de cotações",
                "fonte": COTACOES_URL,
            }

        # Baixar PDF
        r = requests.get(pdf_url, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            return {
                "estado": "SC",
                "nome": "CEASA Santa Catarina",
                "data": data_hoje,
                "cotacoes": [],
                "erro": f"Erro ao baixar PDF: HTTP {r.status_code}",
                "fonte": COTACOES_URL,
            }

        # Parsear data do nome do arquivo
        if data_str:
            date_match = re.search(r"(\d{2})-(\d{2})-(\d{4})", data_str)
            if date_match:
                data_hoje = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"

        cotacoes = parse_pdf(r.content)

        logger.info(f"CEASA SC: {len(cotacoes)} cotações coletadas em {data_hoje}")
        return {
            "estado": "SC",
            "nome": "CEASA Santa Catarina",
            "data": data_hoje,
            "cotacoes": cotacoes,
            "fonte": COTACOES_URL,
        }

    except Exception as e:
        logger.error(f"Erro ao coletar CEASA SC: {e}")
        return {
            "estado": "SC",
            "nome": "CEASA Santa Catarina",
            "data": data_hoje,
            "cotacoes": [],
            "erro": str(e),
            "fonte": COTACOES_URL,
        }


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)
    dados = scrape()
    print(json.dumps(dados, ensure_ascii=False, indent=2))
