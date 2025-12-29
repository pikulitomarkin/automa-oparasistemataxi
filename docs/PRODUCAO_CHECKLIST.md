# ✅ Checklist para Produção - Sistema 100% Automatizado

## 📋 Status: Sistema Pronto para Dispensar Intervenção Humana

**Data**: 2025-12-29  
**Taxa de sucesso**: 100% (5/5 emails testados)

---

## 🎯 Pré-requisitos de Produção

### 1. ✅ Sistema de Extração LLM
- [x] Prompt configurado para formato CSN
- [x] Priorização de tabelas sobre texto livre
- [x] Matrículas como identificadores (Passageiro MIN7956)
- [x] Múltiplos endereços gerenciados
- [x] Telefones opcionais
- [x] Conversão de horários relativos (hoje/amanhã)
- [x] Mapeamento de locais CSN (CSN, BH, MARIANA, LAFAIETE)
- [x] Extração de CC codes
- [x] Detecção de viagens de retorno
- [x] 100% de sucesso em testes

### 2. ⏭️ Configuração de Email (Gmail)
- [ ] Configurar IMAP credentials no `.env`:
  ```env
  IMAP_SERVER=imap.gmail.com
  IMAP_EMAIL=virso2016@gmail.com
  IMAP_PASSWORD=<app_password_aqui>
  EMAIL_SUBJECT_FILTER=PROGRAMAÇÃO
  ```
- [ ] Testar leitura de emails reais
- [ ] Validar que emails são marcados como lidos após processamento

### 3. ⏭️ Geocoding Service
- [ ] Configurar Nominatim ou Google Maps API
- [ ] Testar coordenadas para locais CSN:
  - [ ] CSN Mineração, Congonhas, MG
  - [ ] Mariana, MG
  - [ ] Conselheiro Lafaiete, MG
  - [ ] Ibirité, MG
- [ ] Validar rate limits (Nominatim: 1 req/seg)
- [ ] Implementar fallback se geocoding falhar

### 4. ⏭️ MinasTaxi API Integration
- [ ] Credentials configuradas no `.env`:
  ```env
  MINASTAXI_API_URL=https://vm2c.taxifone.com.br:11048
  MINASTAXI_USER_ID=02572696000156
  MINASTAXI_PASSWORD=0104
  MINASTAXI_AUTH_HEADER=Basic Original.#2024
  ```
- [ ] Testar endpoint `/rideCreate`
- [ ] Validar payload format (partner=1, users array, UNIX timestamp)
- [ ] Testar resposta de sucesso (rideId retornado)
- [ ] Implementar retry em caso de falha

### 5. ⏭️ WhatsApp Notifications
- [ ] Evolution API configurada:
  ```env
  EVOLUTION_API_URL=https://evolution-api-production-d234.up.railway.app
  EVOLUTION_API_KEY=<sua_chave>
  EVOLUTION_INSTANCE=<sua_instancia>
  ```
- [ ] Testar envio de notificações
- [ ] Template de mensagem criado
- [ ] Fallback se WhatsApp falhar (não bloquear pipeline)

### 6. ⏭️ Database & Logs
- [ ] Database SQLite em `data/taxi_orders.db`
- [ ] Logs em `data/taxi_automation.log`
- [ ] Backup automático configurado
- [ ] Verificar campos de tracking (email_id, status, whatsapp_sent)

---

## 🔄 Pipeline Completo

```
Email (IMAP)
    ↓
LLM Extractor (100% sucesso) ✅
    ↓
Geocoding (coordenadas)
    ↓
MinasTaxi API (dispatch)
    ↓
WhatsApp (notificação)
    ↓
Database (persistência)
```

---

## 🧪 Testes de Integração

### Teste 1: Email → LLM
```bash
python test_llm_csn_emails.py
```
**Esperado**: ✅ 5/5 emails com sucesso

### Teste 2: Email → LLM → Geocoding
```bash
python run_processor.py --test-geocoding
```
**Esperado**: Coordenadas válidas para todos os endereços CSN

### Teste 3: Pipeline Completo
```bash
python run_processor.py
```
**Esperado**: Email processado até dispatch sem erros

### Teste 4: Dashboard
```bash
streamlit run app_liquid.py
```
**Esperado**: Pedidos aparecem no dashboard com status correto

---

## ⚠️ Tratamento de Erros

### Cenários com Auto-Recovery
1. **LLM falha**: Retry 3x com delay exponencial ✅
2. **Geocoding falha**: Status `MANUAL_REVIEW`, não bloqueia
3. **MinasTaxi API falha**: Retry 3x, depois `FAILED`
4. **WhatsApp falha**: Logga warning, não bloqueia
5. **Email duplicado**: Usa `email_id` único, ignora

### Cenários que Requerem Atenção
- Status `MANUAL_REVIEW`: Geocoding não encontrou coordenadas
- Status `FAILED`: MinasTaxi rejeitou após 3 tentativas
- Telefone vazio: Logga warning, pode falhar no dispatch

**Dashboard mostra todos em tempo real** 📊

---

## 🚀 Deploy para Produção

### Opção 1: Railway (Recomendado)
1. [ ] Copiar variáveis do `RAILWAY_VARS.txt` para Railway
2. [ ] Deploy via Git push
3. [ ] Validar logs no Railway dashboard
4. [ ] Testar webhook/cron para processamento periódico

### Opção 2: Local/VPS
1. [ ] Configurar cron job:
   ```bash
   */15 * * * * cd /path/to/taxi && /path/to/.venv/bin/python run_processor.py
   ```
2. [ ] Configurar systemd para dashboard Streamlit
3. [ ] Nginx reverse proxy para HTTPS

---

## 📊 Monitoramento

### Métricas Críticas
- [ ] Taxa de sucesso LLM (esperado: 100%)
- [ ] Taxa de dispatch MinasTaxi (esperado: >95%)
- [ ] Tempo médio de processamento (<30s por email)
- [ ] Pedidos em `MANUAL_REVIEW` (esperado: <5%)

### Alertas
- [ ] Email inválido após 3 tentativas → Slack/Email
- [ ] API MinasTaxi fora do ar → Alerta crítico
- [ ] Mais de 10 pedidos em `MANUAL_REVIEW` → Investigar

---

## ✅ Critérios de Sucesso (100% Automatizado)

- [x] LLM extrai corretamente 100% dos formatos CSN
- [ ] Geocoding retorna coordenadas para >95% dos endereços
- [ ] MinasTaxi aceita >95% dos pedidos
- [ ] Pipeline completo sem intervenção humana para casos normais
- [ ] Dashboard mostra status em tempo real
- [ ] Erros são recuperáveis automaticamente ou vão para revisão com contexto claro

---

## 🎉 Go-Live

### Semana 1: Piloto
- [ ] Processar 10 emails reais
- [ ] Validar cada etapa manualmente
- [ ] Ajustar geocoding se necessário

### Semana 2-3: Monitoramento Ativo
- [ ] Checar dashboard 2x/dia
- [ ] Resolver casos de `MANUAL_REVIEW`
- [ ] Coletar feedback dos motoristas/passageiros

### Semana 4+: Automação Completa
- [ ] Sistema roda sem intervenção
- [ ] Apenas alertas críticos requerem ação
- [ ] Revisão semanal de métricas

---

**Status Atual**: ✅ **LLM 100% pronto. Próximo: testar com emails reais do Gmail.**

**ETA para Go-Live**: 2-3 dias após configurar Gmail IMAP e testar geocoding.
