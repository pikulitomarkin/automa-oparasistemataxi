# Processador Contínuo de E-mails - Documentação

## Visão Geral

O sistema foi atualizado para operar em **modo contínuo**, verificando e processando novos e-mails automaticamente em intervalos regulares.

## Como Funciona

### Antes (Problema)
- ❌ Executava apenas UMA vez e parava
- ❌ Requeria execução manual ou cron jobs externos
- ❌ Não processava e-mails que chegavam após a execução

### Agora (Solução)
- ✅ Loop infinito com intervalo configurável
- ✅ Verifica novos e-mails automaticamente
- ✅ Tratamento robusto de erros (não para em falhas)
- ✅ Logs detalhados de cada ciclo

## Configuração

### Variáveis de Ambiente

Adicione estas variáveis ao seu `.env` ou no Railway:

```bash
# Intervalo entre verificações (em minutos)
PROCESSOR_INTERVAL_MINUTES=15

# Quantos dias para trás buscar e-mails
EMAIL_DAYS_BACK=7
```

### Valores Recomendados

| Ambiente | `PROCESSOR_INTERVAL_MINUTES` | Descrição |
|----------|------------------------------|-----------|
| **Produção** | `5` | Verifica a cada 5 minutos (padrão) ⚡ |
| **Desenvolvimento** | `3` | Verifica a cada 3 minutos (testes rápidos) |
| **Alta Demanda** | `5` | Verifica a cada 5 minutos (resposta rápida) |
| **Baixa Demanda** | `15` | Verifica a cada 15 minutos (economiza recursos) |

## Logs do Sistema

### Logs de Inicialização

```
============================================================
CONTINUOUS TAXI ORDER PROCESSOR STARTED
Checking for new emails every 5 minutes
Email search window: last 7 days
============================================================
```

### Logs de Ciclo

Cada ciclo mostra:
```
============================================================
PROCESSING CYCLE #1 - 2025-12-31 14:30:00
============================================================
Fetching new order emails (last 7 days)...
Found 3 new order emails
Processing email UID=12345...
...
Processing Statistics: {'emails_fetched': 3, 'orders_created': 3, 'orders_dispatched': 2, 'orders_failed': 1}
Database Statistics: {'received': 0, 'extracted': 0, 'geocoded': 0, 'dispatched': 9, 'failed': 4, 'manual_review': 2, 'total': 15}

Cycle #1 complete. Next check at 2025-12-31 14:35:00
Sleeping for 5 minutes...
```

## Railway Deploy

### 1. Atualizar Variáveis de Ambiente

No Railway Dashboard:
1. Acesse seu projeto
2. Vá em **Variables**
3. Adicione:
   ```
   PROCESSOR_INTERVAL_MINUTES=5
   EMAIL_DAYS_BACK=7
   ```

### 2. Verificar Logs

Após deploy, os logs devem mostrar:
```
Starting Taxi Automation System...
Starting continuous email processor (checking every 5 minutes)...
Processor started with PID: 123
Starting Streamlit dashboard on port 8501...
```

### 3. Monitoramento

- **Dashboard Streamlit**: `https://seu-app.railway.app/`
- **Logs do Railway**: Em tempo real no painel
- **Arquivo de log**: `/data/taxi_automation.log` (persistido em volume)

## Tratamento de Erros

O sistema é resiliente a falhas:

### Erro em Ciclo Individual
```
Error in processing cycle #5: Connection timeout
Waiting 5 minutes before retry...
```
→ Sistema continua rodando, próximo ciclo tenta novamente

### Erro Crítico (Inicialização)
```
Failed to initialize processor: Invalid API key
```
→ Sistema para e precisa correção manual

## Modo de Teste Local

Para testar localmente:

```bash
# Windows
python run_processor.py

# Linux/Mac
python run_processor.py
```

Para parar:
- Pressione `Ctrl+C` (KeyboardInterrupt)

## Arquivos Modificados

1. **`run_processor.py`** - Loop contínuo implementado
2. **`start.sh`** - Script de inicialização atualizado
3. **`.env.example`** - Novas variáveis documentadas

## Solução de Problemas

### Sistema não processa e-mails

**Sintomas**: Logs mostram "No new order emails found" sempre

**Soluções**:
1. Verificar se `EMAIL_SUBJECT_FILTER` está correto
2. Verificar se há e-mails não lidos na caixa
3. Aumentar `EMAIL_DAYS_BACK` para buscar mais no passado

### Sistema para após erro

**Sintomas**: Logs param de aparecer após erro

**Soluções**:
1. Verificar logs completos: `cat data/processor.log`
2. Verificar se é erro crítico de inicialização
3. Corrigir credenciais/configurações e fazer redeploy

### Consumo alto de recursos

**Sintomas**: Railway mostra uso alto de CPU/memória

**Soluções**:
1. Aumentar `PROCESSOR_INTERVAL_MINUTES` (ex: 15 ou 30)
2. Reduzir `EMAIL_DAYS_BACK` (ex: 3 ou 5 dias)
3. Verificar se há loops infinitos em geocoding

## Próximas Melhorias

- [ ] Webhook para processar e-mails instantaneamente
- [ ] Dashboard de monitoramento do processador
- [ ] Alertas quando sistema para de processar
- [ ] Métricas de performance (tempo por ciclo, taxa de sucesso)

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs no Railway
2. Consulte a documentação em `/docs/`
3. Entre em contato com suporte técnico
