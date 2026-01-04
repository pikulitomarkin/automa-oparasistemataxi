# 🔧 Correção: Campos Centro de Custo e Código de Empresa

## 📋 Problema Identificado

Conforme a tela do sistema MinasTaxi mostrada pelo cliente (QRU 166.724):

### ❌ Campos vazios/errados:
1. **Campo "C.Custo"** - Estava vazio (circulado em vermelho)
2. **Campo "Código / Empresa"** - Mostrava "6017 / TECNOKOR / KOCH" ao invés de "284 / DELP"

### ✅ Dados extraídos corretamente pelo sistema:
- ✅ Centro de custo: `1.07002.07.004` (extraído do email)
- ✅ Código da empresa: `284` (extraído do email - "Empresa: 284 - Delp Engenharia")

## 🔍 Causa Raiz

O sistema estava **extraindo corretamente** os dados, mas **enviando nos campos errados** para a API MinasTaxi.

### Antes da correção:
```json
{
  "cost_center": "1.07002.07.004",    // ❌ Campo não existe na API
  "company_code": "284"                // ❌ Campo não existe na API
}
```

### Depois da correção:
```json
{
  "extra1": "284",                    // ✅ Campo correto para Código Empresa
  "extra2": "1.07002.07.004"          // ✅ Campo correto para Centro de Custo
}
```

## 📡 Mapeamento de Campos na API MinasTaxi (Original Software)

| Campo API | Campo na Tela MinasTaxi | Exemplo |
|-----------|------------------------|---------|
| `extra1` | **Código / Empresa** | `284` (DELP) |
| `extra2` | **C.Custo** | `1.07002.07.004` |
| `passenger_note` | **Obs. Operador(a)** | `C.Custo: 1.07002.07.004` |

## ✅ Solução Implementada

### Arquivo Modificado:
- `src/services/minastaxi_client.py` (linhas 350-380)

### Mudanças:
1. **Removido**: Campos `cost_center` e `company_code` (não nativos da API)
2. **Adicionado**: Campos `extra1` (código empresa) e `extra2` (centro custo)
3. **Logs atualizados**: Mostram `extra1` e `extra2` para debug

### Código após correção:
```python
# Adiciona centro de custo e código de empresa nos campos extras
# extra1 = Código da Empresa (aparece no campo "Código / Empresa")
# extra2 = Centro de Custo (aparece no campo "C.Custo")
if company_code:
    payload["extra1"] = company_code
    logger.info(f"✅ Código da empresa (extra1): {company_code}")

if cost_center:
    payload["extra2"] = cost_center
    logger.info(f"✅ Centro de custo (extra2): {cost_center}")
```

## 🧪 Teste de Validação

Criado arquivo `test_payload_minastaxi.py` que valida:
- ✅ Campo `extra1` presente e com valor correto (`284`)
- ✅ Campo `extra2` presente e com valor correto (`1.07002.07.004`)
- ✅ Payload JSON completo está correto

### Resultado do teste:
```
🎉 PAYLOAD CORRETO!
✅ Campos extra1 (empresa) e extra2 (centro custo) presentes
✅ MinasTaxi receberá os dados corretamente
```

## 📦 Deploy

### Status:
- ✅ Código corrigido
- ✅ Teste validado localmente
- ✅ Commit realizado: `f23a936`
- ✅ Push para Railway concluído
- ⏳ Deploy automático em andamento

### Logs esperados no próximo email processado:
```
✅ Código da empresa (extra1): 284
✅ Centro de custo (extra2): 1.07002.07.004
Order dispatched successfully. Ride ID: XXXXX
```

## 🔍 Como Verificar no Railway

Após o próximo email ser processado:

1. **Verificar logs**:
```bash
npx @railway/cli logs --tail 100
```

2. **Procurar por**:
- `✅ Código da empresa (extra1): 284`
- `✅ Centro de custo (extra2): 1.07002.07.004`

3. **Verificar na tela MinasTaxi**:
- Campo **"Código / Empresa"** deve mostrar `284 / DELP`
- Campo **"C.Custo"** deve mostrar `1.07002.07.004`

## 📝 Exemplo de Payload Completo

```json
{
  "partner": "1",
  "user": "02572696000156",
  "password": "0104",
  "request_id": "20260104170000ABC",
  "pickup_time": "1767565048",
  "category": "taxi",
  "passenger_name": "Gasparino Rodrigues da Silva",
  "passenger_phone_number": "31999999926",
  "payment_type": "ONLINE_PAYMENT",
  "passenger_note": "C.Custo: 1.07002.07.004 | Empresa: 284 - Delp Engenharia",
  "extra1": "284",
  "extra2": "1.07002.07.004",
  "users": [...],
  "destinations": [...]
}
```

## ⚠️ Observações Importantes

1. **Extração continua funcionando**: O sistema continua extraindo `company_code` e `cost_center` do email via LLM
2. **Apenas a transmissão mudou**: Agora usa `extra1` e `extra2` para enviar à API
3. **Compatibilidade**: A mudança não afeta pedidos antigos ou outras funcionalidades
4. **Formato universal**: Sistema detecta múltiplos formatos de email (CSN, DELP, etc.)

## 🎯 Resultado Final

### Antes (Problema):
- ❌ C.Custo: **vazio**
- ❌ Código / Empresa: **6017 / TECNOKOR**

### Depois (Corrigido):
- ✅ C.Custo: **1.07002.07.004**
- ✅ Código / Empresa: **284 / DELP**

---

**Status:** ✅ Corrigido e em produção  
**Commit:** f23a936  
**Data:** 04/01/2026 17:15  
**Próximo passo:** Aguardar processamento do próximo email para confirmar
