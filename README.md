# Cotações CEASA Sul - RS, SC, PR

Um site estático que monitora e exibe as cotações diárias de alimentos dos CEASAs (Centrais de Abastecimento) da região sul do Brasil, com destaque para produtos que tiveram aumento de preço.

## 🎯 Funcionalidades

- **Monitoramento de Cotações**: Coleta dados diários dos CEASAs de Rio Grande do Sul, Santa Catarina e Paraná
- **Alertas de Aumento**: Identifica e destaca alimentos com aumento de preço
- **Interface Interativa**: Visualização clara com abas para "Todos os Produtos" e "Aumentos de Preço"
- **Atualização Automática**: GitHub Actions executa scraping diariamente
- **Responsivo**: Design adaptado para desktop, tablet e mobile
- **Sem Dependências Backend**: Site estático hospedado no GitHub Pages

## 📊 Dados Monitorados

### CEASA PR (Paraná)
- **Fonte**: https://celepar7.pr.gov.br/ceasa/hoje.asp
- **Regiões**: Curitiba, Maringá, Londrina, Foz do Iguaçu, Cascavel
- **Formato**: Tabela HTML com cotações estruturadas
- **Atualização**: Diária

### CEASA SC (Santa Catarina)
- **Fonte**: https://www.ceasa.sc.gov.br/index.php/cotacao-de-precos/2026-1
- **Regiões**: São José, Blumenau, Tubarão
- **Formato**: PDFs de cotações
- **Atualização**: Diária

### CEASA RS (Rio Grande do Sul)
- **Fonte**: https://ceasa.rs.gov.br/cotacoes-de-precos
- **Regiões**: Porto Alegre
- **Formato**: Arquivos em Google Drive
- **Atualização**: Diária

## 🚀 Como Usar

### Desenvolvimento Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/ceasa-sul-cotacoes.git
   cd ceasa-sul-cotacoes
   ```

2. **Instale as dependências**
   ```bash
   pnpm install
   ```

3. **Inicie o servidor de desenvolvimento**
   ```bash
   pnpm dev
   ```

4. **Acesse no navegador**
   ```
   http://localhost:3000
   ```

### Build para Produção

```bash
pnpm build
```

Os arquivos estáticos serão gerados em `dist/`

## 🔄 Atualização Automática

O projeto usa **GitHub Actions** para executar o scraping automaticamente:

- **Frequência**: Todos os dias úteis às 8:00 AM (UTC-3)
- **Workflow**: `.github/workflows/scrape-cotacoes.yml`
- **Ação**: Coleta dados, processa e faz commit automático

### Configurar GitHub Actions

1. Faça push do repositório para GitHub
2. Ative GitHub Pages nas configurações do repositório
3. Selecione `gh-pages` como branch de publicação
4. O workflow será executado automaticamente conforme agendado

## 📁 Estrutura do Projeto

```
ceasa-sul-cotacoes/
├── client/                          # Frontend React
│   ├── src/
│   │   ├── pages/
│   │   │   └── Home.tsx            # Página principal
│   │   ├── lib/
│   │   │   └── mockData.ts         # Dados de exemplo
│   │   ├── components/             # Componentes reutilizáveis
│   │   ├── App.tsx                 # Roteamento
│   │   └── index.css               # Estilos globais
│   ├── public/
│   │   └── data/                   # Dados JSON gerados
│   └── index.html
├── scripts/
│   ├── ceasa_pr_scraper.py        # Scraper do CEASA PR
│   ├── ceasa_sc_scraper.py        # Scraper do CEASA SC
│   ├── ceasa_rs_scraper.py        # Scraper do CEASA RS
│   ├── main_scraper.py            # Coordenador de scrapers
│   └── process_data.py            # Processamento de dados
├── .github/
│   └── workflows/
│       └── scrape-cotacoes.yml    # GitHub Actions workflow
├── package.json
└── README.md
```

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 19**: Framework UI
- **TypeScript**: Tipagem estática
- **Tailwind CSS 4**: Estilização
- **shadcn/ui**: Componentes de UI
- **Lucide React**: Ícones

### Backend/Scraping
- **Python 3.11**: Linguagem de scraping
- **Requests**: HTTP client
- **BeautifulSoup4**: Parsing HTML
- **pdfplumber**: Extração de PDFs

### DevOps
- **GitHub Actions**: Automação
- **GitHub Pages**: Hospedagem estática
- **Vite**: Build tool

## 📈 Análise de Dados

O site identifica automaticamente:

1. **Aumentos de Preço**: Comparação com o dia anterior
2. **Percentual de Aumento**: Cálculo automático
3. **Produtos Afetados**: Listagem com destaque visual
4. **Tendências**: Padrões de aumento por região

## 🔐 Segurança

- Site estático (sem backend vulnerável)
- Dados públicos de fontes oficiais
- Sem armazenamento de dados sensíveis
- Sem autenticação necessária

## 📝 Licença

Este projeto é de código aberto e disponível sob a licença MIT.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para reportar bugs ou sugerir melhorias, abra uma issue no GitHub.

## 🙏 Agradecimentos

- CEASA RS, SC e PR pelas informações públicas de cotações
- Comunidade de código aberto

---

**Última atualização**: 16/03/2026

Para mais informações, visite: https://github.com/seu-usuario/ceasa-sul-cotacoes
