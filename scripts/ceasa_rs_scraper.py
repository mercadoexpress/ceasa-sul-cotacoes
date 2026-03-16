#!/usr/bin/env python3
"""Scraper para cotações do CEASA Rio Grande do Sul."""

import requests
from bs4 import BeautifulSoup
import re
import csv
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

COTACOES_URL = "https://ceasa.rs.gov.br/cotacoes-de-precos"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Pastas do Drive por mês (fallback quando o site CEASA RS não está acessível)
DRIVE_FOLDERS_FALLBACK = {
    "2026-03": "https://drive.google.com/drive/folders/1rFc6Z9rOw5xVa4OjfVw--0-UzzsB8TzM",
    "2026-02": "https://drive.google.com/drive/folders/1WMryDfV3gbj7zRk3jP1mDtl-vIE9vAHb",
    "2026-01": "https://drive.google.com/drive/folders/11rUjgzDqn89DVZrhPdWcP02LP9Ja4EoK",
}


def get_drive_folder_ids() -> dict[str, str]:
    """Obtém os IDs das pastas do Google Drive por mês/ano."""
    import urllib3
    urllib3.disable_warnings()
    try:
        r = requests.get(COTACOES_URL, headers=HEADERS, timeout=30, verify=False)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        month_map = {
            "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03",
            "ABRIL": "04", "MAIO": "05", "JUNHO": "06",
            "JULHO": "07", "AGOSTO": "08", "SETEMBRO": "09",
            "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12",
        }

        folders = {}
        current_year = None

        # Iterar por todos os elementos para manter contexto de ano
        for elem in soup.find_all(["h2", "h3", "h4", "h5", "a", "button"]):
            text = elem.get_text(strip=True)
            # Detectar ano
            year_match = re.match(r'^(202\d)$', text)
            if year_match:
                current_year = int(year_match.group(1))
                continue

            # Detectar link de pasta
            if elem.name == "a":
                href = elem.get("href", "")
                if "drive.google.com" in href and "folders" in href:
                    text_upper = text.upper()
                    for month_name, month_num in month_map.items():
                        if month_name in text_upper:
                            year = current_year or datetime.now().year
                            key = f"{year}-{month_num}"
                            # Só adicionar se não existir (prioriza o mais recente)
                            if key not in folders:
                                folders[key] = href
                            break

        return folders
    except Exception as e:
        logger.error(f"Erro ao obter pastas do Drive: {e}")
        return {}


def get_latest_sheet_id(folder_url: str) -> tuple[str | None, str | None]:
    """Obtém o ID da planilha mais recente em uma pasta do Drive."""
    try:
        r = requests.get(folder_url, headers=HEADERS, timeout=30)
        html = r.text.replace("&quot;", '"').replace("&amp;", "&")

        # Encontrar todos os IDs de arquivo (44 chars)
        id_positions = [
            (m.start(), m.group(1))
            for m in re.finditer(r'"(1[A-Za-z0-9_-]{43})"', html)
        ]

        # Para cada ID, procurar data associada (múltiplos formatos)
        file_dates = {}
        for pos, file_id in id_positions:
            ctx = html[pos : pos + 600]
            # Formato DD/MM/YYYY
            date_match = re.search(r"Cotação (\d{2}/\d{2}/\d{4})", ctx)
            if date_match:
                date_str = date_match.group(1)
                if file_id not in file_dates:
                    file_dates[file_id] = date_str
                continue
            # Formato YYYY-MM-DD
            date_match2 = re.search(r"Cotação - (\d{4})-(\d{2})-(\d{2})", ctx)
            if date_match2:
                y, m, d = date_match2.group(1), date_match2.group(2), date_match2.group(3)
                date_str = f"{d}/{m}/{y}"
                if file_id not in file_dates:
                    file_dates[file_id] = date_str

        if not file_dates:
            logger.warning("CEASA RS: nenhum arquivo encontrado na pasta")
            return None, None

        # Ordenar por data e pegar o mais recente
        def parse_date(d):
            try:
                return datetime.strptime(d, "%d/%m/%Y")
            except Exception:
                return datetime.min

        latest_id = max(file_dates, key=lambda k: parse_date(file_dates[k]))
        latest_date = file_dates[latest_id]

        logger.info(f"CEASA RS: planilha mais recente: {latest_date} (ID: {latest_id})")
        return latest_id, latest_date

    except Exception as e:
        logger.error(f"Erro ao obter planilha do Drive: {e}")
        return None, None


def parse_preco(valor: str) -> float | None:
    """Converte string de preço para float."""
    if not valor:
        return None
    # Remover "R$", espaços, pontos de milhar
    val = re.sub(r"[R$\s]", "", valor).replace(".", "").replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None


def parse_csv(csv_content: str) -> list[dict]:
    """Extrai cotações do CSV exportado do Google Sheets."""
    cotacoes = []
    try:
        reader = csv.reader(io.StringIO(csv_content))
        categoria_atual = "GERAL"

        for row in reader:
            if not row or all(c.strip() == "" for c in row):
                continue

            # Detectar linha de categoria (ex: "VERDURAS E LEGUMES")
            first_cell = row[0].strip().strip('"')
            if re.match(r'^[A-Z\s]+$', first_cell) and len(first_cell) > 3:
                # Pode ser cabeçalho de categoria
                if any(
                    cat in first_cell.upper()
                    for cat in [
                        "VERDURA", "LEGUME", "FRUTA", "TEMPERO",
                        "CONDIMENTO", "RAIZ", "BULBO", "FOLHA",
                        "PROCESSADO", "OUTROS",
                    ]
                ):
                    categoria_atual = first_cell
                    continue

            # Pular linhas de cabeçalho de coluna
            if any(
                h in str(row).upper()
                for h in ["PRODUTO", "UND", "MAX", "MÍNIMO", "MINIMO", "FREQUENTE"]
            ):
                continue

            # Linha de cotação: [vazio, produto, und, max, mais_freq, min]
            if len(row) >= 5:
                produto = ""
                preco_max = None
                preco_comum = None
                preco_min = None

                # Tentar diferentes posições
                # Formato 1: [lixo, produto, und, max, mais_freq, min]
                if len(row) >= 6:
                    produto = row[1].strip().strip('"')
                    preco_max = parse_preco(row[3])
                    preco_comum = parse_preco(row[4])
                    preco_min = parse_preco(row[5])
                elif len(row) >= 5:
                    produto = row[0].strip().strip('"')
                    preco_max = parse_preco(row[2])
                    preco_comum = parse_preco(row[3])
                    preco_min = parse_preco(row[4])

                if not produto or len(produto) < 2:
                    continue

                # Pular linhas que não são produtos
                if produto.upper() in [
                    "PRODUTO", "UND", "MAX", "MAIS FREQUENTE", "MÍNIMO",
                    "MINIMO", "A,", "A", "",
                ]:
                    continue

                # Verificar se tem pelo menos um preço válido
                preco_final = preco_comum or preco_max or preco_min
                if preco_final is None:
                    continue

                cotacoes.append(
                    {
                        "produto": produto.upper(),
                        "preco": preco_final,
                        "preco_min": preco_min,
                        "preco_max": preco_max,
                        "categoria": categoria_atual,
                        "unidade": "R$",
                    }
                )

    except Exception as e:
        logger.error(f"Erro ao parsear CSV CEASA RS: {e}")

    # Remover duplicatas
    seen = set()
    unique = []
    for c in cotacoes:
        key = c["produto"]
        if key not in seen and key:
            seen.add(key)
            unique.append(c)

    return unique


def scrape() -> dict:
    """Coleta cotações do CEASA RS."""
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    try:
        # Obter pastas do Drive
        folders = get_drive_folder_ids()

        if not folders:
            logger.warning("CEASA RS: nenhuma pasta encontrada, usando fallback")
            # Fallback: usar pastas conhecidas
            now = datetime.now()
            key = f"{now.year}-{now.month:02d}"
            if key in DRIVE_FOLDERS_FALLBACK:
                folders = {key: DRIVE_FOLDERS_FALLBACK[key]}
            else:
                # Usar a pasta mais recente disponível
                folders = dict(sorted(DRIVE_FOLDERS_FALLBACK.items(), reverse=True)[:1])

        # Pegar a pasta mais recente
        sorted_keys = sorted(folders.keys(), reverse=True)
        latest_folder_url = folders[sorted_keys[0]]

        # Obter planilha mais recente
        sheet_id, data_str = get_latest_sheet_id(latest_folder_url)

        if not sheet_id:
            # Tentar pasta anterior
            if len(sorted_keys) > 1:
                latest_folder_url = folders[sorted_keys[1]]
                sheet_id, data_str = get_latest_sheet_id(latest_folder_url)

        if not sheet_id:
            return {
                "estado": "RS",
                "nome": "CEASA Rio Grande do Sul",
                "data": data_hoje,
                "cotacoes": [],
                "erro": "Não foi possível encontrar planilha de cotações",
                "fonte": COTACOES_URL,
            }

        # Baixar como CSV
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        r = requests.get(csv_url, headers=HEADERS, timeout=60)

        if r.status_code != 200:
            return {
                "estado": "RS",
                "nome": "CEASA Rio Grande do Sul",
                "data": data_hoje,
                "cotacoes": [],
                "erro": f"Erro ao baixar planilha: HTTP {r.status_code}",
                "fonte": COTACOES_URL,
            }

        if data_str:
            data_hoje = data_str

        cotacoes = parse_csv(r.text)

        logger.info(f"CEASA RS: {len(cotacoes)} cotações coletadas em {data_hoje}")
        return {
            "estado": "RS",
            "nome": "CEASA Rio Grande do Sul",
            "data": data_hoje,
            "cotacoes": cotacoes,
            "fonte": COTACOES_URL,
        }

    except Exception as e:
        logger.error(f"Erro ao coletar CEASA RS: {e}")
        return {
            "estado": "RS",
            "nome": "CEASA Rio Grande do Sul",
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
