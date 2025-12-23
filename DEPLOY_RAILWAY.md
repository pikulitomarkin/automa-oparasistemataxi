# 🚀 Deploy no Railway - Sistema de Automação de Táxi

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app/)
2. Repositório Git (GitHub, GitLab ou Bitbucket)
3. Chaves de API necessárias

## 🔧 Passos para Deploy

### 1. Preparar o Repositório

```bash
# Inicializar Git (se ainda não fez)
git init

# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit - Taxi Automation System"

# Adicionar remote (GitHub/GitLab)
git remote add origin https://github.com/seu-usuario/taxi-automation.git
git push -u origin main
```

### 2. Criar Projeto no Railway

1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha seu repositório `taxi-automation`

### 3. Configurar Variáveis de Ambiente

No Railway Dashboard, vá em **Variables** e adicione:

#### Email (IMAP)
```
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
EMAIL_FOLDER=INBOX
EMAIL_SUBJECT_FILTER=Novo Agendamento
```

#### OpenAI
```
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

#### MinasTaxi API
```
MINASTAXI_API_URL=https://api.minastaxi.com.br
MINASTAXI_API_KEY=your-minastaxi-api-key-here
MINASTAXI_TIMEOUT=30
MINASTAXI_RETRY_ATTEMPTS=3
```

#### Geocoding (Opcional)
```
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
USE_GOOGLE_MAPS=false
```

#### Database & Logging
```
DATABASE_PATH=data/taxi_orders.db
LOG_LEVEL=INFO
LOG_FILE=data/taxi_automation.log
PROCESS_INTERVAL_SECONDS=300
ENABLE_CLUSTERING=true
```

#### Railway Específico
```
PORT=8501
```

### 4. Deploy Automático

Railway detectará automaticamente:
- `railway.toml` - Configurações de build/deploy
- `runtime.txt` - Versão do Python (3.11.7)
- `requirements.txt` - Dependências
- `start.sh` - Script de inicialização

O deploy iniciará automaticamente!

### 5. Adicionar Volume Persistente (Recomendado)

Para não perder os dados do SQLite entre deploys:

1. No Railway Dashboard, vá em **Volumes**
2. Clique em **"New Volume"**
3. Configure:
   - **Name**: `taxi-data`
   - **Mount Path**: `/app/data`
4. Salve e faça redeploy

### 6. Configurar Domínio (Opcional)

1. No Railway, vá em **Settings**
2. Clique em **"Generate Domain"**
3. Ou adicione seu domínio customizado

## 🎯 Como Funciona no Railway

### Arquitetura

O Railway executará **2 processos simultâneos**:

1. **Processador** (`run_processor.py`)
   - Monitora emails a cada 5 minutos
   - Processa pedidos automaticamente
   - Roda em background

2. **Dashboard Streamlit** (`app_liquid.py`)
   - Interface web no Tema Liquid iPhone
   - Visualização em tempo real
   - Acessível via URL do Railway

### Logs

Visualize logs no Railway Dashboard:
```
railway logs
```

Ou via CLI:
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Logs específicos
railway logs --service web
railway logs --service worker
```

## 🔍 Troubleshooting

### Erro: "Port already in use"
- Railway define a variável `$PORT` automaticamente
- Certifique-se de usar `--server.port=$PORT`

### Erro: "Database locked"
- Use o Volume persistente
- Verifique permissões do diretório `data/`

### Processador não está executando
- Verifique logs: `railway logs`
- Confirme que `start.sh` tem permissão de execução
- Teste localmente: `bash start.sh`

### Emails não estão sendo processados
- Verifique credenciais IMAP
- Gmail: Use senha de app, não senha normal
- Outlook: Ative IMAP nas configurações

## 📊 Monitoramento

### Health Check
Railway verifica automaticamente se a aplicação está rodando.

### Métricas
Acesse no Dashboard:
- CPU usage
- Memory usage
- Request count
- Response time

## 🔐 Segurança

✅ **Recomendações:**
- Nunca commite o arquivo `.env`
- Use variáveis de ambiente do Railway
- Ative 2FA na conta Railway
- Use senhas de app para email
- Rotacione API keys regularmente

## 💡 Comandos Úteis

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link projeto
railway link

# Ver status
railway status

# Redeploy
railway up

# Executar comando remoto
railway run python run_processor.py

# Shell remoto
railway shell

# Variáveis
railway variables
```

## 🔄 Atualizações

Para atualizar o sistema:

```bash
# Fazer alterações no código
git add .
git commit -m "Atualização: descrição"
git push

# Railway fará deploy automático!
```

## 📞 Suporte

- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Streamlit Docs](https://docs.streamlit.io/)

## 🎉 Pronto!

Seu sistema está no ar! Acesse a URL fornecida pelo Railway.

**URL exemplo:** `https://taxi-automation-production.up.railway.app`

---

Desenvolvido com ❤️ • Sistema de Automação de Táxi v1.0
