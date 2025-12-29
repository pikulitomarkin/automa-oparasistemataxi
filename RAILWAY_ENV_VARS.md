# 🔐 Variáveis de Ambiente - Railway Deploy

## 🎯 **CREDENCIAIS MINASTAXI - INFORMAÇÃO CRÍTICA**

As credenciais da API MinasTaxi **já estão configuradas** e prontas para uso:

| Variável | Valor |
|----------|-------|
| `MINASTAXI_API_URL` | `https://vm2c.taxifone.com.br:11048` |
| `MINASTAXI_USER_ID` | `02572696000156` |
| `MINASTAXI_PASSWORD` | `0104` |
| `MINASTAXI_AUTH_HEADER` | `Basic Original.#2024` |

✅ **Use EXATAMENTE estes valores no Railway!**

---

## 📋 LISTA COMPLETA DE VARIÁVEIS

Copie e cole todas essas variáveis no Railway Dashboard → **Variables**

---

## ✉️ **EMAIL (IMAP)**
```
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=virso2016@gmail.com
EMAIL_PASSWORD=ubyb zngk utbv gvsq
EMAIL_FOLDER=INBOX
EMAIL_SUBJECT_FILTER=Novo Agendamento
```

---

## 🤖 **OPENAI API**
```
OPENAI_API_KEY=sua-chave-openai-aqui
OPENAI_MODEL=gpt-4-turbo-preview
```

⚠️ **Substitua `sua-chave-openai-aqui` pela sua chave real da OpenAI**

---

## 🚕 **MINASTAXI API** (Original Software - CREDENCIAIS REAIS)
```
MINASTAXI_API_URL=https://vm2c.taxifone.com.br:11048
MINASTAXI_USER_ID=02572696000156
MINASTAXI_PASSWORD=0104
MINASTAXI_AUTH_HEADER=Basic Original.#2024
MINASTAXI_TIMEOUT=30
MINASTAXI_RETRY_ATTEMPTS=3
```

⚠️ **IMPORTANTE**: Estas são as credenciais REAIS fornecidas pela MinasTaxi.
- **URL**: `https://vm2c.taxifone.com.br:11048`
- **User ID (Contrato)**: `02572696000156`
- **Password**: `0104`
- **Autenticação**: `Basic Original.#2024`

---

## 📱 **WHATSAPP (Evolution API)**
```
EVOLUTION_API_URL=https://evolution-api-production-d234.up.railway.app/
EVOLUTION_API_KEY=minas2025taxi2026automacao
EVOLUTION_INSTANCE_NAME=taxiautomacao
ENABLE_WHATSAPP_NOTIFICATIONS=true
```

---

## 🗺️ **GEOCODING (Opcional - Nominatim é padrão)**
```
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
USE_GOOGLE_MAPS=false
```

💡 Se não tiver Google Maps API, deixe `USE_GOOGLE_MAPS=false` (usa Nominatim gratuito)

---

## 💾 **DATABASE & LOGGING**
```
DATABASE_PATH=/data/taxi_orders.db
LOG_LEVEL=INFO
LOG_FILE=/data/taxi_automation.log
```

⚠️ **IMPORTANTE**: Note o `/data/` com barra no início para persistir dados no Railway Volume!

---

## ⚙️ **PROCESSAMENTO**
```
PROCESS_INTERVAL_SECONDS=300
ENABLE_CLUSTERING=true
```

---

## 🌐 **RAILWAY ESPECÍFICO**
```
PORT=8501
```

---

## 📝 **INSTRUÇÕES DE CONFIGURAÇÃO NO RAILWAY**

### **1. Criar Projeto no Railway**
1. Acesse https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Selecione seu repositório: `automa-oparasistemataxi`

### **2. Configurar Variáveis de Ambiente** ⚠️ **PASSO CRÍTICO**
1. No projeto, vá em **Variables**
2. Clique em **RAW Editor**
3. **COPIE E COLE** todas as variáveis abaixo:

```env
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USER=virso2016@gmail.com
EMAIL_PASSWORD=ubyb zngk utbv gvsq
EMAIL_FOLDER=INBOX
EMAIL_SUBJECT_FILTER=Novo Agendamento

OPENAI_API_KEY=sua-chave-openai-aqui
OPENAI_MODEL=gpt-4-turbo-preview

MINASTAXI_API_URL=https://vm2c.taxifone.com.br:11048
MINASTAXI_USER_ID=02572696000156
MINASTAXI_PASSWORD=0104
MINASTAXI_AUTH_HEADER=Basic Original.#2024
MINASTAXI_TIMEOUT=30
MINASTAXI_RETRY_ATTEMPTS=3

EVOLUTION_API_URL=https://evolution-api-production-d234.up.railway.app/
EVOLUTION_API_KEY=minas2025taxi2026automacao
EVOLUTION_INSTANCE_NAME=taxiautomacao
ENABLE_WHATSAPP_NOTIFICATIONS=true

GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
USE_GOOGLE_MAPS=false

DATABASE_PATH=/data/taxi_orders.db
LOG_LEVEL=INFO
LOG_FILE=/data/taxi_automation.log

PROCESS_INTERVAL_SECONDS=300
ENABLE_CLUSTERING=true

PORT=8501
```

4. **IMPORTANTE**: Substitua `sua-chave-openai-aqui` pela sua chave OpenAI real
5. Clique em **Save**

### **3. Adicionar Volume Persistente**
Para não perder dados do SQLite entre deploys:

1. Vá em **Volumes** (ícone de disco)
2. **New Volume**
3. Configure:
   - **Mount Path**: `/data`
   - **Name**: `taxi-data`
4. **Save**

### **4. Deploy**
O Railway vai automaticamente:
- ✅ Detectar Python 3.11
- ✅ Instalar dependências do `requirements.txt`
- ✅ Executar `start.sh`
- ✅ Iniciar Dashboard Streamlit

---

## 🔄 **ATUALIZAÇÕES FUTURAS**

### Credenciais MinasTaxi já configuradas:
✅ **API MinasTaxi já está com credenciais reais!**
- URL: `https://vm2c.taxifone.com.br:11048`
- User ID: `02572696000156`
- Password: `0104`
- Auth: `Basic Original.#2024`

**Não precisa alterar nada relacionado ao MinasTaxi!**

### Para atualizar WhatsApp:
- Trocar `EVOLUTION_API_URL` se mudar servidor
- Trocar `EVOLUTION_INSTANCE_NAME` se criar nova instância

---

## 🚨 **IMPORTANTE - SEGURANÇA**

⚠️ **NUNCA** commitar o arquivo `.env` no Git!

O `.gitignore` já está configurado para ignorar:
```
.env
.env.*
*.db
*.log
```

**Credenciais MinasTaxi configuradas:**
- ✅ URL: `https://vm2c.taxifone.com.br:11048`
- ✅ User ID: `02572696000156`
- ✅ Password: `0104`
- ✅ Auth: `Basic Original.#2024`

Todas as credenciais sensíveis devem estar APENAS no Railway Variables!

---

## ✅ **CHECKLIST DE DEPLOY**

- [ ] Criar conta no Railway
- [ ] Fazer push do código para GitHub
- [ ] Criar projeto no Railway conectado ao GitHub
- [ ] **COPIAR E COLAR** todas as variáveis de ambiente no RAW Editor
- [ ] **Substituir** chave OpenAI pela sua chave real
- [ ] Verificar que credenciais MinasTaxi estão corretas (URL, User ID, Password, Auth)
- [ ] Criar Volume em `/data` para persistência
- [ ] Aguardar primeiro deploy (≈ 3-5 minutos)
- [ ] Ativar "Generate Domain" para obter URL pública
- [ ] Testar acessando URL do Railway
- [ ] Enviar email de teste para `Novo Agendamento`
- [ ] Verificar Dashboard, MinasTaxi API e WhatsApp
- [ ] Conferir logs no Railway para validar integração

---

## 📊 **URLs Após Deploy**

Após o deploy, você terá:
- 🌐 **Dashboard**: `https://seu-projeto.up.railway.app`
- 📊 **Streamlit**: Interface web acessível publicamente
- 📱 **WhatsApp**: Notificações automáticas
- 💾 **Dados**: Salvos no volume `/data`

---

## 🆘 **TROUBLESHOOTING**

### Erro de conexão IMAP:
- Verificar se Gmail App Password está correto
- Habilitar "Acesso a apps menos seguros" no Gmail

### Erro no WhatsApp:
- Verificar se Evolution API está rodando
- Testar URL: `https://evolution-api-production-d234.up.railway.app/`
- Confirmar que instância está conectada (QR Code escaneado)

### Erro no OpenAI:
- Verificar saldo da API em https://platform.openai.com
- Confirmar que a chave está correta e ativa
- Verificar limites de rate limit

### Erro na API MinasTaxi:
- ✅ Credenciais já estão configuradas corretamente
- URL: `https://vm2c.taxifone.com.br:11048`
- Testar conectividade: `curl -X POST https://vm2c.taxifone.com.br:11048/rideCreate`
- Verificar se servidor está acessível (pode haver firewall/VPN)
- Confirmar formato do payload (ver `docs/API_MINASTAXI.md`)

### Banco não persiste:
- Certificar que Volume foi criado em `/data`
- Variável `DATABASE_PATH` deve começar com `/data/`
- Verificar permissões de escrita no Railway

---

**Pronto para deploy! 🚀**
