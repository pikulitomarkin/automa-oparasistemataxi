# 🔄 Reprocessar Pedidos com Falha via Railway CLI

## 📋 Pré-requisitos

1. **Instalar Railway CLI**:
```bash
npm install -g @railway/cli
# ou
curl -fsSL https://railway.app/install.sh | sh
```

2. **Fazer Login**:
```bash
railway login
```

3. **Conectar ao Projeto**:
```bash
railway link
# Selecione seu projeto da lista
```

---

## 🚀 Métodos de Reprocessamento

### **Método 1: Executar Script Python Diretamente** ⚡ (Recomendado)

Execute o script de reprocessamento no container Railway:

```bash
railway run python reprocess_failed_orders.py
```

**O que o script faz:**
- ✅ Busca todas as orders com status `FAILED` no banco
- ✅ Tenta reenviar para API MinasTaxi com correções SSL
- ✅ Atualiza status para `DISPATCHED` em caso de sucesso
- ✅ Envia notificações WhatsApp (se habilitado)
- ✅ Mostra relatório com estatísticas finais

---

### **Método 2: Shell Interativo** 🖥️

Para mais controle e debugging:

```bash
# Abrir shell no container Railway
railway shell

# Dentro do shell, executar:
python reprocess_failed_orders.py

# Ou verificar banco diretamente:
python inspect_failed_order.py
```

---

### **Método 3: Reprocessar Order Específica** 🎯

Se quiser reprocessar apenas uma order específica por ID:

```bash
# Criar script temporário
railway run python -c "
from src.services.database import DatabaseManager
from src.services.minastaxi_client import MinasTaxiClient
import os

db = DatabaseManager()
client = MinasTaxiClient(
    api_url=os.getenv('MINASTAXI_API_URL'),
    user_id=os.getenv('MINASTAXI_USER_ID'),
    password=os.getenv('MINASTAXI_PASSWORD'),
    auth_header=os.getenv('MINASTAXI_AUTH_HEADER')
)

# Buscar order por ID
order = db.get_order(ORDER_ID_AQUI)
if order:
    response = client.dispatch_order(order)
    print(f'✅ Order {order.id} reprocessada!')
"
```

---

## 📊 Verificar Status Antes de Reprocessar

### **1. Ver quantas orders falhadas existem**:
```bash
railway run python -c "
from src.services.database import DatabaseManager
db = DatabaseManager()
failed = db.get_orders_by_status('FAILED')
print(f'📊 Total de orders falhadas: {len(failed)}')
for o in failed[:5]:
    print(f'  - ID: {o.id} | Passageiro: {o.passenger_name} | Erro: {o.error_message[:50]}')
"
```

### **2. Inspecionar order específica**:
```bash
railway run python inspect_failed_order.py
```

### **3. Ver logs recentes**:
```bash
railway logs
```

---

## 🔍 Troubleshooting

### **Erro: "No project linked"**
```bash
railway link
# Selecione o projeto manualmente
```

### **Erro: "Module not found"**
O Railway precisa instalar as dependências primeiro:
```bash
railway run pip install -r requirements.txt
railway run python reprocess_failed_orders.py
```

### **Erro de conexão com banco**
Verifique se o volume `/data` está montado:
```bash
railway run ls -la /data/
# Deve mostrar taxi_orders.db
```

### **Ver variáveis de ambiente**
```bash
railway variables
# Confirme que MINASTAXI_API_URL, USER_ID, etc. estão configurados
```

---

## 📈 Output Esperado

Quando executar `railway run python reprocess_failed_orders.py`, você verá:

```
2026-01-02 10:30:15 - INFO - Inicializando reprocessador de orders...
2026-01-02 10:30:16 - INFO - Buscando orders falhadas no banco...
2026-01-02 10:30:16 - INFO - Encontradas 3 orders falhadas

Reprocessando Order ID: 45...
2026-01-02 10:30:17 - INFO - ✅ Order 45 despachada com sucesso!
2026-01-02 10:30:17 - INFO - Viagem ID: 12345

Reprocessando Order ID: 46...
2026-01-02 10:30:18 - ERROR - ❌ Falha ao despachar order 46: SSL Error

Reprocessando Order ID: 47...
2026-01-02 10:30:19 - INFO - ✅ Order 47 despachada com sucesso!

====================================
📊 RELATÓRIO DE REPROCESSAMENTO
====================================
Total processadas: 3
✅ Sucesso: 2
❌ Falhas: 1
Taxa de sucesso: 66.67%
====================================
```

---

## ⚡ Comandos Rápidos

```bash
# Reprocessar tudo
railway run python reprocess_failed_orders.py

# Ver logs em tempo real
railway logs --tail 100

# Verificar status do serviço
railway status

# Reiniciar serviço (recarrega código)
railway up --detach
```

---

## 🔄 Automatizar Reprocessamento

Se quiser reprocessar automaticamente em intervalos regulares, adicione um cron job ou modifique o [run_processor.py](run_processor.py) para incluir:

```python
# No loop principal do processor
if iteration_count % 10 == 0:  # A cada 10 iterações
    logger.info("Reprocessando orders falhadas...")
    reprocessor = OrderReprocessor()
    reprocessor.reprocess_all()
```

---

## 📞 Suporte

- 📖 **Documentação Railway**: https://docs.railway.app/
- 🐛 **Debug**: Use `railway logs` para ver erros
- 📊 **Dashboard**: Acesse Railway web UI para métricas

---

**Pronto para reprocessar! 🚀**
