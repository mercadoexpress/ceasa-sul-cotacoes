#!/usr/bin/env python3
"""
Script para processar e consolidar dados de cotações
Prepara os dados para serem consumidos pelo frontend
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_json(filepath):
    """Carrega arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {filepath}: {e}")
        return None

def save_json(data, filepath):
    """Salva arquivo JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def consolidate_data():
    """
    Consolida todos os dados em um arquivo único
    para o frontend consumir
    """
    
    dados_dir = Path('dados')
    
    # Carrega dados de cada estado
    pr_data = load_json(dados_dir / 'ceasa_pr_hoje.json')
    sc_data = load_json(dados_dir / 'ceasa_sc_links.json')
    rs_data = load_json(dados_dir / 'ceasa_rs_links.json')
    
    # Consolida em um arquivo único
    consolidated = {
        'data_atualizacao': datetime.now().isoformat(),
        'estados': {
            'PR': pr_data or {'estado': 'Paraná', 'sigla': 'PR', 'erro': 'Dados não disponíveis'},
            'SC': sc_data or {'estado': 'Santa Catarina', 'sigla': 'SC', 'erro': 'Dados não disponíveis'},
            'RS': rs_data or {'estado': 'Rio Grande do Sul', 'sigla': 'RS', 'erro': 'Dados não disponíveis'}
        }
    }
    
    # Salva arquivo consolidado
    output_path = Path('public/data/cotacoes.json')
    save_json(consolidated, output_path)
    print(f"Dados consolidados salvos em {output_path}")
    
    return consolidated

def generate_summary():
    """
    Gera um resumo em markdown com os aumentos de preço
    """
    
    dados_dir = Path('dados')
    pr_data = load_json(dados_dir / 'ceasa_pr_hoje.json')
    
    if not pr_data or 'cotacoes' not in pr_data:
        return
    
    # Filtra produtos com aumento
    aumentos = [c for c in pr_data['cotacoes'] if c.get('aumento')]
    
    if not aumentos:
        return
    
    # Gera markdown
    md_content = f"""# Relatório de Aumentos de Preço
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Resumo
Total de produtos com aumento: {len(aumentos)}

## Detalhes

"""
    
    for item in aumentos:
        md_content += f"""### {item['produto']}
- **Região**: {item.get('regiao', 'N/A')}
- **Preço anterior**: R$ {item['preco'] - item['aumento']['valor']:.2f}
- **Preço atual**: R$ {item['preco']:.2f}
- **Aumento**: {item['aumento']['percentual']:.2f}% (+R$ {item['aumento']['valor']:.2f})

"""
    
    # Salva relatório
    output_path = Path('public/data/relatorio.md')
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Relatório salvo em {output_path}")

if __name__ == "__main__":
    print("Processando dados de cotações...")
    consolidate_data()
    generate_summary()
    print("Processamento concluído!")
