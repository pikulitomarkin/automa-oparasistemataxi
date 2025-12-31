# 🚕 Sistema de Automação de Táxi

Sistema completo de automação para processamento de pedidos de táxi via e-mail, com extração inteligente de dados usando IA, geocodificação e integração com API MinasTaxi.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Dashboard](#dashboard)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

Este sistema automatiza o fluxo completo de processamento de pedidos de táxi:

1. **Monitoramento de E-mail**: Lê pedidos recebidos via IMAP
2. **Extração Inteligente**: Usa LLM (OpenAI GPT-4) para extrair dados estruturados
3. **Geocodificação**: Converte endereços em coordenadas geográficas
4. **Integração API**: Envia pedidos para a API MinasTaxi automaticamente
5. **Dashboard Operacional**: Interface visual para monitoramento em tempo real

## ✨ Funcionalidades

## ✨ Funcionalidades

### FASE 1: Ingestão de Pedidos (Modo Contínuo)
- ✅ **Monitoramento automático contínuo** com intervalo configurável
- ✅ Loop infinito que verifica novos e-mails periodicamente
- ✅ Intervalo padrão: 15 minutos (configurável)
- ✅ Filtro por assunto "Novo Agendamento"
- ✅ Suporte a Gmail, Outlook e outros provedores IMAP
- ✅ Processamento de e-mails não lidos
- ✅ Prevenção de duplicatas
- ✅ Tratamento robusto de erros (não para em falhas)

### FASE 2: Extração e Tratamento (NLP/LLM)
- ✅ Extração automática via OpenAI GPT-4
- ✅ Campos extraídos:
  - Nome do passageiro
  - Telefone com DDD
  - Endereço de coleta completo
  - Endereço de destino (opcional)
  - Data/hora de coleta
- ✅ Conversão de horários relativos ("amanhã às 14h" → ISO 8601)
- ✅ Normalização automática de dados
- ✅ Retry automático em caso de falha

### FASE 2.5: Módulo de Logística (Geo-Intelligence)
- ✅ Geocodificação usando Nominatim (OpenStreetMap)
- ✅ Suporte opcional para Google Maps API
- ✅ Cálculo de distâncias (Haversine)
- ✅ Reverse geocoding
- ✅ Batch processing com rate limiting

### FASE 3: Integração MinasTaxi (API)
- ✅ Cliente robusto com retry automático (exponential backoff)
- ✅ Tratamento completo de erros HTTP
- ✅ Validação de payload antes do envio
- ✅ Logging detalhado de requisições
- ✅ Timeout configurável
- ✅ Marcação de pedidos com falha para revisão manual

### FASE 4: Monitoramento Operacional (Dashboard)
- ✅ Interface Streamlit responsiva
- ✅ Métricas em tempo real (total, sucessos, falhas, taxa de sucesso)
- ✅ Mapa interativo com marcadores de coleta
- ✅ Visualizações (gráfico de pizza, timeline)
- ✅ Tabelas filtráveis por status
- ✅ Export para CSV
- ✅ Legendas e documentação integrada

## 🏗️ Arquitetura

```
┌─────────────────┐
│   E-mail IMAP   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EmailReader    │ ──► Lê e-mails com filtro
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLMExtractor   │ ──► Extrai dados com GPT-4
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GeocodingService│ ──► Converte endereços em coords
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DatabaseManager │ ──► Salva no SQLite
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│MinasTaxiClient  │ ──► Envia para API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │ ──► Visualização Streamlit
└─────────────────┘
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.9+
- pip
- Git

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd taxi
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o ambiente**
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o .env com suas credenciais
notepad .env  # ou seu editor favorito
```

## ⚙️ Configuração

### 1. Configuração de E-mail (Gmail)

Para usar Gmail com IMAP:

1. Ative IMAP nas configurações do Gmail
2. Crie uma **App Password** (não use sua senha real):
   - Vá em: Conta Google → Segurança → Verificação em duas etapas
   - Role até "Senhas de app"
   - Selecione "E-mail" e "Windows Computer"
   - Copie a senha gerada

No `.env`:
```env
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-app-password-aqui
EMAIL_SUBJECT_FILTER=Novo Agendamento
EMAIL_DAYS_BACK=7
```

### 2. Processador Contínuo (NOVO!)

Configure o intervalo de verificação automática:

```env
# Intervalo entre verificações (em minutos)
PROCESSOR_INTERVAL_MINUTES=5

# Quantos dias para trás buscar e-mails
EMAIL_DAYS_BACK=7
```

**Valores Recomendados**:
- Produção: `5` minutos (padrão) ⚡
- Desenvolvimento: `3` minutos (testes rápidos)
- Alta demanda: `5` minutos
- Baixa demanda: `15` minutos

**📖 Veja documentação completa**: [CONTINUOUS_PROCESSOR.md](CONTINUOUS_PROCESSOR.md)

### 2. OpenAI API

1. Crie uma conta em https://platform.openai.com
2. Gere uma API Key
3. Configure no `.env`:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo-preview
```

### 3. MinasTaxi API

**IMPORTANTE**: Como não temos a documentação real da API MinasTaxi, o sistema usa **mocks/placeholders**.

No `.env`, configure:
```env
MINASTAXI_API_URL=https://api.minastaxi.com.br
MINASTAXI_API_KEY=your-api-key-here
```

**Quando obtiver a documentação real da API:**
1. Atualize a URL base em `MINASTAXI_API_URL`
2. Ajuste o formato do payload em [`src/services/minastaxi_client.py`](src/services/minastaxi_client.py)
3. Verifique o endpoint correto (atualmente `/dispatch`)
4. Ajuste headers de autenticação se necessário

### 4. Geocoding (Opcional)

Por padrão, usa **Nominatim (gratuito)**. Para usar Google Maps API:

```env
USE_GOOGLE_MAPS=true
GOOGLE_MAPS_API_KEY=your-google-key-here
```

## 📖 Uso

### Modo Contínuo (Recomendado para Produção)

O sistema agora roda em **modo contínuo**, verificando e-mails automaticamente:

```bash
# Inicia o processador contínuo
python run_processor.py
```

O sistema irá:
1. ✅ Conectar ao e-mail e outros serviços
2. 🔄 Entrar em loop infinito
3. 📧 A cada X minutos (configurável), buscar novos e-mails
4. 🤖 Processar pedidos automaticamente
5. 💾 Salvar no banco de dados
6. ⏰ Aguardar intervalo e repetir

**Para parar**: Pressione `Ctrl+C`

**Logs em tempo real**:
```bash
# Ver logs do processador
tail -f data/taxi_automation.log

# Windows PowerShell
Get-Content data\taxi_automation.log -Wait -Tail 20
```

### Verificar Status do Sistema

Antes de executar, verifique se tudo está configurado:

```bash
python check_processor_status.py
```

Isso verifica:
- ✓ Variáveis de ambiente
- ✓ Conexão com e-mail
- ✓ OpenAI API key
- ✓ Banco de dados
- ✓ Arquivos de log

### Execução Manual (Uma Vez)

Para processar apenas uma vez (útil para testes):

```bash
python -m src.processor
```

### Deploy em Produção (Railway/Cloud)

O sistema automaticamente inicia em modo contínuo no deploy:

```bash
# O script start.sh faz:
python run_processor.py &  # Background contínuo
streamlit run app_liquid.py  # Dashboard
```

## 📊 Dashboard

Execute o dashboard Streamlit:

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

### Funcionalidades do Dashboard

- **Métricas**: Total de pedidos, despachados, falhas, taxa de sucesso
- **Mapa Interativo**: Visualização geográfica dos pontos de coleta
- **Timeline**: Gráfico de pedidos por dia
- **Tabelas**: Lista detalhada com filtros por status
- **Export**: Download de dados em CSV

## 📁 Estrutura do Projeto

```
taxi/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── order.py              # Models: Order, OrderStatus
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite manager
│   │   ├── email_reader.py       # IMAP email service
│   │   ├── llm_extractor.py      # OpenAI extraction
│   │   ├── geocoding_service.py  # Geocoding (Nominatim/Google)
│   │   └── minastaxi_client.py   # API client com retry
│   ├── __init__.py
│   └── processor.py              # Orchestrator principal
├── data/
│   ├── .gitkeep
│   ├── taxi_orders.db            # SQLite database (gerado)
│   └── taxi_automation.log       # Logs (gerado)
├── tests/                        # (para desenvolvimento futuro)
├── docs/                         # (documentação adicional)
├── app.py                        # Dashboard Streamlit
├── requirements.txt              # Dependências Python
├── .env                          # Configurações (NÃO commitar)
├── .env.example                  # Template de configuração
├── .gitignore
└── README.md                     # Este arquivo
```

## 🔍 Troubleshooting

### Erro: "Failed to connect to email server"

**Solução**:
- Verifique se IMAP está habilitado no Gmail
- Use App Password, não sua senha normal
- Verifique firewall/antivírus bloqueando porta 993

### Erro: "OpenAI API error"

**Solução**:
- Verifique se sua API key está correta
- Confirme que tem créditos disponíveis na conta OpenAI
- Teste a key em: https://platform.openai.com/playground

### Erro: "Geocoding timeout"

**Solução**:
- Nominatim tem rate limits (1 req/s)
- O sistema já implementa delays automáticos
- Considere usar Google Maps API para maior throughput

### Erro: "MinasTaxi API connection failed"

**Solução**:
- Verifique a URL da API no `.env`
- Confirme que a API key está correta
- Use `test_connection()` para diagnóstico:

```python
from src.services.minastaxi_client import MinasTaxiClient
client = MinasTaxiClient(api_url="...", api_key="...")
client.test_connection()
```

### Dashboard não exibe dados

**Solução**:
- Execute o processador primeiro: `python -m src.processor`
- Verifique se o banco de dados foi criado em `data/taxi_orders.db`
- Clique em "🔄 Atualizar Dados" no dashboard

## 🔐 Segurança

**IMPORTANTE**:
- ❌ Nunca commite o arquivo `.env` com credenciais reais
- ✅ Use `.env.example` como template
- ✅ Adicione `.env` ao `.gitignore` (já configurado)
- ✅ Use App Passwords para e-mail, não senhas reais
- ✅ Rotacione API keys periodicamente

## 📝 Prompt de Sistema LLM

O prompt otimizado usado pelo sistema está em [`src/services/llm_extractor.py`](src/services/llm_extractor.py).

**Principais características**:
- Instruções claras para formato JSON
- Conversão automática de horários relativos
- Normalização de endereços
- Validação de campos obrigatórios
- Temperatura baixa (0.1) para consistência
- Retry automático em caso de falha

## 🧪 Testes

Para executar testes (em desenvolvimento):

```bash
pytest tests/ -v --cov=src
```

## 📈 Próximos Passos

- [ ] Implementar clustering geográfico para otimização de rotas
- [ ] Adicionar suporte para leitura de planilhas Excel/CSV
- [ ] Implementar notificações (email/SMS) para falhas
- [ ] Adicionar autenticação no dashboard
- [ ] Criar API REST para integração externa
- [ ] Implementar fila de processamento com Celery
- [ ] Adicionar testes unitários e de integração

## 📄 Licença

Proprietary - Uso interno apenas.

## � Deploy em Produção

### Railway (Recomendado)

Veja instruções completas em [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)

```bash
# 1. Push para GitHub
git push origin main

# 2. Conecte no Railway
# 3. Configure variáveis de ambiente
# 4. Deploy automático!
```

### Outras Plataformas

- **Heroku**: Use `Procfile` incluído
- **Render**: Compatível com `railway.toml`
- **DigitalOcean**: Use Docker ou App Platform
- **AWS/Azure**: Deploy via container ou VM

## �👥 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Consulte os logs em `data/taxi_automation.log`
3. Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ para automação inteligente de táxi**
