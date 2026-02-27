# 🔧 CORREÇÃO URGENTE: Forma de Pagamento no Railway

## ❌ Problema Identificado

A variável `MINASTAXI_PAYMENT_TYPE` **NÃO está configurada** no Railway, fazendo com que todos os pedidos sejam criados com forma de pagamento `ONLINE_PAYMENT` (padrão) ao invés de `BE` (Boleto Eletrônico).

## ✅ Solução Imediata

### 1. Adicionar Variável no Railway

Acesse o Railway e adicione a variável:

```bash
MINASTAXI_PAYMENT_TYPE=BE
```

### 2. Passos Detalhados

#### Opção A: Via Railway Dashboard (Recomendado)

1. Acesse: https://railway.app
2. Selecione o projeto: **taxi-automation**
3. Clique em **"Variables"** no menu lateral
4. Clique em **"+ New Variable"** ou **"Raw Editor"**
5. Adicione a linha:
   ```
   MINASTAXI_PAYMENT_TYPE=BE
   ```
6. Clique em **"Save"** ou **"Deploy"**
7. Aguarde o redeploy automático (~2 minutos)

#### Opção B: Via Railway CLI

```bash
# 1. Instalar Railway CLI (se não tiver)
npm install -g @railway/cli

# 2. Fazer login
railway login

# 3. Linkar ao projeto
railway link

# 4. Adicionar variável
railway variables set MINASTAXI_PAYMENT_TYPE=BE

# 5. Verificar
railway variables
```

### 3. Verificar se Funcionou

Após o deploy, verifique os logs:

```bash
# Via Railway CLI
railway logs

# Ou via Dashboard
# Railway → Projeto → Deployments → View Logs
```

**Busque por:**
```
💳 Tipo de pagamento: BE
```

Se aparecer `💳 Tipo de pagamento: ONLINE_PAYMENT`, a variável ainda não foi aplicada.

## 📊 Valores Possíveis

| Valor | Quando Usar |
|-------|-------------|
| `BE` | **Boleto Eletrônico** (CSN e empresas corporativas) |
| `ONLINE_PAYMENT` | Pagamento online (padrão se não configurado) |
| `BOLETO` | Boleto tradicional |
| `VOUCHER` | Sistema de vouchers |

## 🔍 Como Verificar os Pedidos Atuais

Para verificar se os pedidos estão sendo enviados com a forma de pagamento correta:

```bash
# Ver logs do Railway filtrando por payment_type
railway logs | grep "payment_type"
```

Você deve ver algo como:
```json
"payment_type": "BE"
```

## 🚨 IMPORTANTE

- Após adicionar a variável, **todos os pedidos novos** usarão `BE`
- Pedidos antigos que foram criados com `ONLINE_PAYMENT` **não serão alterados automaticamente**
- Se necessário reprocessar pedidos antigos, use o script:
  ```bash
  python reprocess_failed_orders.py
  ```

## 📝 Checklist de Verificação

- [ ] Variável `MINASTAXI_PAYMENT_TYPE=BE` adicionada no Railway
- [ ] Deploy concluído com sucesso
- [ ] Logs mostram `💳 Tipo de pagamento: BE`
- [ ] Próximo pedido processado usa `BE` no payload

## 🔗 Arquivos Atualizados

Os seguintes arquivos foram corrigidos para incluir a variável:
- ✅ `RAILWAY_VARS.txt` - Lista de variáveis para copiar/colar
- ✅ `RAILWAY_ENV_VARS.md` - Documentação completa
- ✅ `.env.example` - Exemplo local

---

**Data:** 06/01/2026  
**Prioridade:** 🔴 ALTA - Afeta todos os pedidos em produção
