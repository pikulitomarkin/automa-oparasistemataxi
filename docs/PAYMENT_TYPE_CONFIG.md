# Configuração de Tipo de Pagamento (payment_type)

## Visão Geral

O campo `payment_type` define como a cobrança do pedido será processada na API MinasTaxi.

## Valores Possíveis

| Valor | Descrição |
|-------|-----------|
| `ONLINE_PAYMENT` | Pagamento online (padrão) |
| `BE` | Boleto Eletrônico |
| `BOLETO` | Boleto tradicional |
| `VOUCHER` | Pagamento via voucher |

## Configuração

### Variável de Ambiente

Adicione no arquivo `.env`:

```bash
MINASTAXI_PAYMENT_TYPE=BE
```

### Valores Comuns por Cliente

- **CSN/Empresas Corporativas**: `BE` (Boleto Eletrônico)
- **Pagamentos Online**: `ONLINE_PAYMENT`
- **Sistema de Vouchers**: `VOUCHER`

## Como Funciona

1. O valor é lido do arquivo `.env` via variável `MINASTAXI_PAYMENT_TYPE`
2. Se não configurado, usa `ONLINE_PAYMENT` como padrão
3. O valor é passado para o `MinasTaxiClient` na inicialização
4. Cada pedido despachado usa esse valor no campo `payment_type` do payload

## Logs

Quando um pedido é despachado, o sistema loga o tipo de pagamento:

```
2026-01-05 23:23:46 - INFO - 💳 Tipo de pagamento: BE
```

## Exemplo de Payload

```json
{
  "partner": "1",
  "user": "17161936000873",
  "password": "0104",
  "payment_type": "BE",
  "passenger_name": "João Silva",
  ...
}
```

## Railway / Produção

Para alterar o tipo de pagamento no Railway:

1. Acesse o dashboard do Railway
2. Vá em **Variables**
3. Adicione/edite: `MINASTAXI_PAYMENT_TYPE=BE`
4. Faça redeploy se necessário

## Troubleshooting

### Todos os pedidos aparecem como "BE"

Se todos os pedidos estão sendo marcados como "BE" na MinasTaxi, verifique:

1. **Variável de ambiente configurada?**
   ```bash
   echo $MINASTAXI_PAYMENT_TYPE
   # Deve retornar: BE
   ```

2. **Railway configurado?**
   - Verificar se `MINASTAXI_PAYMENT_TYPE=BE` está nas variáveis de ambiente

3. **Logs confirmam?**
   ```bash
   npx railway logs | grep "Tipo de pagamento"
   # Deve mostrar: 💳 Tipo de pagamento: BE
   ```

### Mudar para outro tipo

Para mudar de `BE` para `VOUCHER`:

1. **Localmente**: Editar `.env`
   ```bash
   MINASTAXI_PAYMENT_TYPE=VOUCHER
   ```

2. **Railway**: Editar variável de ambiente e redeploy

---

**Data**: 2026-01-05  
**Status**: ✅ Implementado e configurável
