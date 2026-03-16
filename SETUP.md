# Guia de Configuração - Cotações CEASA Sul

Este guia explica como configurar o projeto no GitHub e ativar a atualização automática de cotações.

## 📋 Pré-requisitos

- Conta no GitHub
- Git instalado localmente
- Node.js 22+ e pnpm instalados

## 🚀 Passo 1: Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Preencha os dados:
   - **Repository name**: `ceasa-sul-cotacoes`
   - **Description**: "Monitoramento de cotações diárias CEASA RS, SC, PR"
   - **Visibility**: Public (para usar GitHub Pages gratuito)
   - **Initialize this repository**: Deixe desmarcado

3. Clique em "Create repository"

## 📤 Passo 2: Push do Código Local

```bash
# Clone o repositório local
cd ceasa-sul-cotacoes

# Adicione o remote
git remote add origin https://github.com/seu-usuario/ceasa-sul-cotacoes.git

# Configure a branch padrão
git branch -M main

# Faça o push inicial
git push -u origin main
```

## ⚙️ Passo 3: Ativar GitHub Pages

1. Vá para **Settings** do repositório
2. Na seção **Pages** (lado esquerdo):
   - **Source**: Selecione "Deploy from a branch"
   - **Branch**: Selecione `gh-pages` e pasta `/ (root)`
   - Clique em "Save"

3. Aguarde alguns minutos. Seu site estará disponível em:
   ```
   https://seu-usuario.github.io/ceasa-sul-cotacoes/
   ```

## 🔄 Passo 4: Configurar Atualização Automática

### Opção A: Scraping Automático (Recomendado)

O workflow `scrape-cotacoes.yml` já está configurado para executar diariamente:

1. Vá para **Actions** no repositório
2. Clique em "Scrape Cotações Diárias"
3. Clique em "Enable workflow"

O workflow executará:
- **Todos os dias úteis às 8:00 AM (UTC-3)**
- Coleta dados dos três CEASAs
- Processa e consolida os dados
- Faz commit automático com as atualizações

### Opção B: Execução Manual

Para testar o workflow manualmente:

1. Vá para **Actions**
2. Selecione "Scrape Cotações Diárias"
3. Clique em "Run workflow"
4. Selecione a branch `main`
5. Clique em "Run workflow"

## 📊 Passo 5: Verificar Funcionamento

### Verificar Deploy

1. Vá para **Actions**
2. Verifique se o workflow "Deploy to GitHub Pages" foi executado com sucesso
3. Visite seu site em `https://seu-usuario.github.io/ceasa-sul-cotacoes/`

### Verificar Scraping

1. Vá para **Actions**
2. Clique em "Scrape Cotações Diárias"
3. Verifique se há commits automáticos com dados atualizados
4. Veja os dados em `dados/ceasa_pr_hoje.json`, etc.

## 🔧 Personalização

### Alterar Horário de Execução

Edite `.github/workflows/scrape-cotacoes.yml`:

```yaml
schedule:
  # Mude o horário aqui (formato cron UTC)
  - cron: '0 11 * * 1-5'  # 8:00 AM UTC-3 (11:00 AM UTC)
```

Formatos comuns:
- `0 11 * * 1-5` = Seg-Sex 8:00 AM (UTC-3)
- `0 14 * * 1-5` = Seg-Sex 11:00 AM (UTC-3)
- `0 0 * * *` = Todos os dias à meia-noite (UTC)

### Adicionar Domínio Customizado

1. Vá para **Settings** → **Pages**
2. Em "Custom domain", digite seu domínio (ex: `ceasa.seu-dominio.com`)
3. Configure os registros DNS do seu domínio:
   ```
   A record: 185.199.108.153
   A record: 185.199.109.153
   A record: 185.199.110.153
   A record: 185.199.111.153
   ```

## 🐛 Troubleshooting

### Workflow não executa

- Verifique se o workflow está habilitado em **Actions**
- Verifique se a branch padrão é `main`
- Verifique os logs do workflow para erros

### Site não aparece

- Aguarde 5-10 minutos após o push
- Limpe o cache do navegador (Ctrl+Shift+Del)
- Verifique se GitHub Pages está habilitado em **Settings**

### Dados não atualizam

- Execute manualmente o workflow para testar
- Verifique os logs do workflow em **Actions**
- Verifique se os scripts Python têm permissão de execução

## 📝 Estrutura de Branches

```
main (branch principal)
  ↓
  Commits do código
  ↓
  GitHub Actions: Deploy
  ↓
gh-pages (branch de publicação)
  ↓
  Site publicado em GitHub Pages
```

## 🔐 Segurança

- O token `GITHUB_TOKEN` é automaticamente criado pelo GitHub
- Nenhuma chave de API é necessária
- Os dados são públicos (de fontes oficiais)

## 📞 Suporte

Para problemas:

1. Verifique os logs em **Actions**
2. Abra uma issue no repositório
3. Consulte a documentação do GitHub Pages

## ✅ Checklist Final

- [ ] Repositório criado no GitHub
- [ ] Código feito push para `main`
- [ ] GitHub Pages habilitado
- [ ] Workflow "Deploy to GitHub Pages" executado com sucesso
- [ ] Site acessível em `https://seu-usuario.github.io/ceasa-sul-cotacoes/`
- [ ] Workflow "Scrape Cotações Diárias" habilitado
- [ ] Teste manual do scraping executado com sucesso

---

**Pronto!** Seu site está configurado e será atualizado automaticamente todos os dias úteis.
