# 🚀 Configuração Rápida - MinasTaxi API

## ✅ Credenciais Configuradas

As credenciais da API MinasTaxi já estão configuradas no sistema:

- **URL**: `https://vm2c.taxifone.com.br:11048`
- **User ID**: `02572696000156`
- **Password**: `0104`
- **Auth Header**: `Basic Original.#2024`

## 📝 Próximos Passos

### 1. Configure seu arquivo `.env` local

Copie o arquivo `.env.production` para `.env`:

```bash
cp .env.production .env
```

Depois edite `.env` e atualize apenas:
- `EMAIL_USER` - seu Gmail
- `EMAIL_PASSWORD` - App Password do Gmail
- `OPENAI_API_KEY` - sua chave da OpenAI

**As credenciais do MinasTaxi já estão corretas!** ✅

### 2. Teste a Conexão

```bash
python -c "from src.services.minastaxi_client import MinasTaxiClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MinasTaxiClient(api_url=os.getenv('MINASTAXI_API_URL'), user_id=os.getenv('MINASTAXI_USER_ID'), password=os.getenv('MINASTAXI_PASSWORD'), auth_header=os.getenv('MINASTAXI_AUTH_HEADER')); print('✅ Cliente MinasTaxi inicializado com sucesso!')"
```

### 3. Teste Completo do Sistema

```bash
python run_test_completo.bat
```

Ou manualmente:

```bash
python test_sistema_completo.py
```

## 🔧 Estrutura do Payload

O sistema agora envia requisições no formato correto:

```json
{
  "partner": "1",
  "user": "02572696000156",
  "password": "0104",
  "request_id": "20251229120000ABC123",
  "pickup_time": "1735484400",
  "category": "taxi",
  "passenger_name": "João Silva",
  "passenger_phone_number": "31988888888",
  "payment_type": "ONLINE_PAYMENT",
  "users": [{
    "id": 1,
    "sequence": 1,
    "name": "João Silva",
    "phone": "31988888888",
    "pickup": {
      "address": "Av Afonso Pena, 1500",
      "city": "Belo Horizonte",
      "state": "MG",
      "postal_code": "",
      "lat": "-19.9191",
      "lng": "-43.9387"
    }
  }],
  "destinations": [{
    "passengerId": 1,
    "sequence": 2,
    "location": {
      "address": "Aeroporto de Confins",
      "city": "Confins",
      "state": "MG",
      "postal_code": "",
      "lat": "-19.6247",
      "lng": "-43.9719"
    }
  }]
}
```

## 📚 Documentação Completa

Veja [docs/API_MINASTAXI.md](docs/API_MINASTAXI.md) para documentação completa dos endpoints.

## ⚠️ Importante

- O arquivo `.env` **NÃO deve ser commitado** no Git
- Use `.env.production` apenas como referência
- As credenciais são sensíveis - mantenha-as seguras
- O sistema já está configurado para usar a API real

## 🎯 Checklist de Integração

- [x] Credenciais da API configuradas
- [x] Cliente MinasTaxi atualizado para formato correto
- [x] Payload com estrutura Original Software
- [x] Autenticação Basic Auth implementada
- [x] Conversão de horários para UNIX timestamp
- [x] Extração automática de cidade/estado
- [ ] Configurar Gmail e OpenAI no `.env`
- [ ] Testar envio de pedido real
- [ ] Validar resposta da API
- [ ] Configurar WhatsApp (opcional)

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs**: `data/taxi_automation.log`
2. **Teste a API manualmente** usando Postman ou curl
3. **Confira as variáveis de ambiente** no `.env`
4. **Consulte a documentação** em `docs/`

---

**Sistema pronto para integração real com MinasTaxi! 🚀**
