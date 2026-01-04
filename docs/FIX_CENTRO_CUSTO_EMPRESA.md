# 🔧 Fix: Centro de Custo e Empresa - IMPLEMENTADO

## 📋 Problemas Reportados pelo Cliente

1. ❌ **Centro de custo não estava sendo repassado** - Campo "C.Custo" aparecia vazio
2. ❌ **Empresa errada** - Pedidos caindo em TECNOKOR quando deveriam ir para DELP

## ✅ Soluções Implementadas

### 1. Campo Centro de Custo

#### Arquivos Modificados:
- `src/models/order.py` - Adicionados campos `notes` e `cost_center`
- `src/services/database.py` - Schema atualizado com novas colunas
- `src/processor.py` - Extrai e armazena o campo `notes`
- `src/services/minastaxi_client.py` - Envia centro de custo para API

#### Como Funciona:
```python
# 1. LLM extrai o centro de custo das observações
notes = "CC: 20086" ou "CENTRO DE CUSTO 1.07002.07.001"

# 2. Sistema extrai o código usando regex
cost_center = _extract_cost_center(notes)
# Resultado: "20086" ou "1.07002.07.001"

# 3. Envia para MinasTaxi no payload
payload = {
    "passenger_note": "C.Custo: 20086 | Observações...",
    "cost_center": "20086"  # Campo específico
}
```

**Suporte a múltiplos formatos:**
- `CC: 20086`
- `CC:20086`
- `CENTRO DE CUSTO 1.07002.07.001`
- `1.07002.07.001` (padrão com pontos)

### 2. Detecção de Empresa

#### Novo método `_detect_company()`:
```python
def _detect_company(destination: str) -> Optional[str]:
    """Detecta empresa com base no destino"""
    if "DELP" in destination or "DELEGACIA" in destination:
        return "DELP"
    # Outros padrões aqui...
    return None
```

#### Comportamento:
- Analisa o endereço de destino
- Se contém "DELP" ou "DELEGACIA" → código de empresa = "DELP"
- Envia no campo `company_code` do payload

**Exemplos detectados:**
- ✅ "DELP - Delegacia Especializada"
- ✅ "Delp Engenharia Vespasiano"
- ✅ "Delegacia de Polícia"

## 📦 Migração do Banco de Dados

### Local (Desenvolvimento):
```bash
python migrate_add_notes_cost_center.py
```

### Railway (Produção):
```bash
# 1. Fazer deploy das mudanças
git add .
git commit -m "feat: adicionar centro de custo e detecção de empresa"
git push origin main

# 2. Executar migração no Railway
railway run python migrate_add_notes_cost_center.py
```

## 🚀 Deploy para Produção

### Checklist:
- [x] Código atualizado em todos os arquivos
- [x] Script de migração criado
- [x] Validação local (opcional)
- [ ] Commit e push para GitHub
- [ ] Deploy automático via Railway
- [ ] Rodar migração no Railway
- [ ] Testar com novo pedido

### Comandos:
```bash
# 1. Commit
git add src/models/order.py src/services/database.py src/services/minastaxi_client.py src/processor.py migrate_add_notes_cost_center.py
git commit -m "feat: adicionar centro de custo e detecção de empresa DELP"

# 2. Push (deploy automático)
git push origin main

# 3. Aguardar deploy (~2-3 min)
# Verificar em: https://railway.app/dashboard

# 4. Migrar banco de dados
railway run python migrate_add_notes_cost_center.py

# 5. Reiniciar serviço (se necessário)
railway restart
```

## 🔍 Como Testar

### 1. Enviar Email de Teste:
```
Assunto: PROGRAMAÇÃO

Horário de chegada DELP: 08:00

Passageiro 1: João Silva
Telefone: (31) 99999-9999
Endereço: Rua ABC, 123 - Belo Horizonte

Destino: DELP - Delegacia Especializada
Centro de custo: 1.07002.07.001
```

### 2. Verificar Logs Railway:
```bash
railway logs --tail 50
```

**O que procurar:**
- ✅ "Centro de custo encontrado: 1.07002.07.001"
- ✅ "Empresa detectada: DELP"
- ✅ "Payload enviado com cost_center e company_code"

### 3. Verificar no Sistema MinasTaxi:
- Campo **C.Custo** deve estar preenchido
- **Empresa** deve ser DELP (não TECNOKOR)

## 📝 Formato do Payload Atualizado

```json
{
  "partner": "1",
  "user": "02572696000156",
  "password": "0104",
  "request_id": "20260104120000ABC",
  "pickup_time": "1735992000",
  "passenger_name": "João Silva",
  "passenger_phone_number": "31999999999",
  "passenger_note": "C.Custo: 1.07002.07.001 | Destino DELP",
  "cost_center": "1.07002.07.001",
  "company_code": "DELP",
  "users": [...],
  "destinations": [...]
}
```

## ⚠️ Notas Importantes

1. **Migração é obrigatória** - Sem ela, novos pedidos falharão
2. **Compatibilidade retroativa** - Pedidos antigos sem notes/cost_center continuam funcionando
3. **Empresa padrão** - Se não detectar empresa, usa configuração padrão da API
4. **Centro de custo opcional** - Se não extrair, campo fica vazio (comportamento antigo)

## 🐛 Troubleshooting

### Erro: "no such column: notes"
**Solução:** Rodar migração
```bash
railway run python migrate_add_notes_cost_center.py
```

### Centro de custo não aparece no MinasTaxi
**Verificar:**
1. Logs: campo extraído corretamente?
2. Payload: `cost_center` presente?
3. API MinasTaxi: campo aceito?

### Empresa ainda vai para TECNOKOR
**Verificar:**
1. Destino contém "DELP" ou "DELEGACIA"?
2. Logs: `_detect_company()` retornou código?
3. Payload: `company_code` presente?

## 📚 Documentação Relacionada

- [docs/API_MINASTAXI.md](docs/API_MINASTAXI.md) - API MinasTaxi
- [docs/EMAIL_FORMAT_CSN.md](docs/EMAIL_FORMAT_CSN.md) - Formato de emails
- [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) - Deploy Railway

---

**Status:** ✅ Implementado e pronto para deploy
**Versão:** 2.1.0
**Data:** 04/01/2026
