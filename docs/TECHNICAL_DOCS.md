# 📖 Documentação Técnica - Sistema de Automação de Táxi

## Prompt de Sistema para LLM (Extração de Dados)

### Prompt Completo Usado no Sistema

O seguinte prompt é usado no arquivo `src/services/llm_extractor.py` para garantir extração precisa de dados:

```
Você é um assistente especializado em extrair dados estruturados de pedidos de táxi recebidos via e-mail.

Sua tarefa é analisar o corpo do e-mail e extrair APENAS os seguintes campos em formato JSON:

{
  "passenger_name": "Nome completo do passageiro",
  "phone": "Telefone com DDD (formato: XX XXXXX-XXXX ou similar)",
  "pickup_address": "Endereço completo de coleta (rua, número, bairro, cidade)",
  "dropoff_address": "Endereço completo de destino (ou null se não mencionado)",
  "pickup_time": "Data e hora de coleta no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
}

REGRAS IMPORTANTES:
1. Para horários relativos ("amanhã às 14h", "hoje às 15h30", "dia 25 às 10h"), converta para formato ISO 8601 absoluto.
2. Se o ano não for mencionado, assuma o ano atual ou próximo (se a data já passou este ano).
3. Se apenas a hora for mencionada, assuma que é para hoje.
4. Use fuso horário de Brasília (America/Sao_Paulo).
5. Se um campo não puder ser extraído com confiança, use null.
6. Retorne APENAS o JSON, sem texto adicional antes ou depois.
7. Normalize endereços: capitalize corretamente e inclua cidade se não mencionada (assuma Belo Horizonte, MG).

Data/hora de referência para conversões: {reference_datetime}
```

### Configurações da API OpenAI

```python
model="gpt-4-turbo-preview"
temperature=0.1  # Baixa para máxima consistência
max_tokens=500
```

### Exemplos de E-mails e Respostas Esperadas

#### Exemplo 1: E-mail Simples

**Input (corpo do e-mail)**:
```
Olá,

Preciso de um táxi para amanhã às 14h.

Nome: João Silva
Telefone: 31 98765-4321
Endereço: Rua das Flores, 123, Savassi

Obrigado!
```

**Output Esperado**:
```json
{
  "passenger_name": "João Silva",
  "phone": "31 98765-4321",
  "pickup_address": "Rua das Flores, 123, Savassi, Belo Horizonte, MG",
  "dropoff_address": null,
  "pickup_time": "2025-12-24T14:00:00-03:00"
}
```

#### Exemplo 2: E-mail Completo com Destino

**Input**:
```
Novo Agendamento

Passageiro: Maria Oliveira
Tel: (31) 3333-4444
Coleta: Av. Afonso Pena, 1500, Centro, BH
Destino: Aeroporto de Confins
Horário: dia 25/12 às 09:30
```

**Output Esperado**:
```json
{
  "passenger_name": "Maria Oliveira",
  "phone": "31 3333-4444",
  "pickup_address": "Av. Afonso Pena, 1500, Centro, Belo Horizonte, MG",
  "dropoff_address": "Aeroporto de Confins, Belo Horizonte, MG",
  "pickup_time": "2025-12-25T09:30:00-03:00"
}
```

---

## Payload da API MinasTaxi

### Estrutura Atual (Mock)

O cliente atual envia o seguinte payload para `POST /dispatch`:

```json
{
  "passenger": {
    "name": "João Silva",
    "phone": "31 98765-4321"
  },
  "pickup": {
    "address": "Rua das Flores, 123, Savassi, Belo Horizonte, MG",
    "coordinates": {
      "latitude": -19.935556,
      "longitude": -43.924722
    },
    "scheduled_time": "2025-12-24T14:00:00-03:00"
  },
  "dropoff": {
    "address": "Aeroporto de Confins, MG",
    "coordinates": {
      "latitude": -19.624444,
      "longitude": -43.971944
    }
  },
  "metadata": {
    "source": "email_automation",
    "email_id": "unique-email-id"
  }
}
```

### Headers

```json
{
  "Authorization": "Bearer YOUR_API_KEY",
  "Content-Type": "application/json",
  "User-Agent": "TaxiAutomationSystem/1.0"
}
```

### Resposta Esperada (Sucesso)

```json
{
  "order_id": "MTX-2025-001234",
  "status": "confirmed",
  "driver": {
    "name": "Carlos Souza",
    "vehicle": "Fiat Argo - ABC1234",
    "eta": "5 minutos"
  },
  "created_at": "2025-12-23T10:30:00-03:00"
}
```

### ⚠️ IMPORTANTE: Adaptação para API Real

**Quando obtiver a documentação oficial da MinasTaxi:**

1. Abra [`src/services/minastaxi_client.py`](../src/services/minastaxi_client.py)
2. Localize o método `dispatch_order()`
3. Ajuste o payload na seção que começa com `payload = {...}`
4. Atualize o endpoint se não for `/dispatch`
5. Modifique headers de autenticação se necessário

**Exemplo de ajuste**:
```python
# Se a API real usa estrutura diferente:
payload = {
    'cliente': {  # ao invés de 'passenger'
        'nome': passenger_name,
        'telefone': phone
    },
    'origem': {  # ao invés de 'pickup'
        'endereco': pickup_address,
        'lat': pickup_lat,
        'lng': pickup_lng
    },
    # ... adapte conforme necessário
}
```

---

## Schema do Banco de Dados

### Tabela: `orders`

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT UNIQUE,              -- UID do e-mail (previne duplicatas)
    passenger_name TEXT,               -- Nome do passageiro
    phone TEXT,                        -- Telefone
    pickup_address TEXT,               -- Endereço de coleta
    dropoff_address TEXT,              -- Endereço de destino (opcional)
    pickup_lat REAL,                   -- Latitude da coleta
    pickup_lng REAL,                   -- Longitude da coleta
    dropoff_lat REAL,                  -- Latitude do destino
    dropoff_lng REAL,                  -- Longitude do destino
    pickup_time TEXT,                  -- Horário de coleta (ISO 8601)
    status TEXT NOT NULL,              -- Status: received, extracted, geocoded, dispatched, failed, manual_review
    created_at TEXT NOT NULL,          -- Timestamp de criação
    updated_at TEXT NOT NULL,          -- Timestamp de última atualização
    raw_email_body TEXT,               -- Corpo original do e-mail (para debug)
    error_message TEXT,                -- Mensagem de erro se falhou
    minastaxi_order_id TEXT,          -- ID retornado pela API MinasTaxi
    cluster_id INTEGER                 -- ID do cluster geográfico (para otimização futura)
);

-- Índices para performance
CREATE INDEX idx_status ON orders(status);
CREATE INDEX idx_pickup_time ON orders(pickup_time);
CREATE INDEX idx_created_at ON orders(created_at DESC);
```

### Estados de Status (OrderStatus)

```python
class OrderStatus(Enum):
    RECEIVED = "received"           # E-mail recebido
    EXTRACTED = "extracted"         # Dados extraídos com sucesso
    GEOCODED = "geocoded"          # Endereços geocodificados
    DISPATCHED = "dispatched"      # Enviado para MinasTaxi com sucesso
    FAILED = "failed"              # Falha no envio
    MANUAL_REVIEW = "manual_review" # Requer atenção manual
```

### Fluxo de Estados

```
RECEIVED → EXTRACTED → GEOCODED → DISPATCHED ✓

         ↓           ↓          ↓
      MANUAL_REVIEW / FAILED (requer intervenção)
```

---

## Integração com Google Maps API (Opcional)

### Por que usar Google Maps?

- **Nominatim** (padrão): Gratuito, mas rate limit de 1 req/s
- **Google Maps**: Pago, mas maior throughput e precisão

### Como configurar

1. Crie uma conta no Google Cloud Platform
2. Ative a API "Geocoding API"
3. Crie uma API Key com restrições:
   - Restrição por aplicativo: IP do servidor
   - Restrição por API: Apenas Geocoding API
4. Configure no `.env`:

```env
USE_GOOGLE_MAPS=true
GOOGLE_MAPS_API_KEY=AIzaSy...
```

### Custos Estimados (Google Maps)

- Geocoding: $5 por 1.000 requisições
- Primeiro $200/mês são grátis (crédito Google Cloud)
- Para 1000 pedidos/mês: ~$5 após créditos

---

## Tratamento de Erros e Retry Logic

### Email Reader

- **Timeout**: 30s por conexão
- **Retry**: 3 tentativas com delay crescente
- **Rate Limit**: Respeita limites do provedor

### LLM Extractor

- **Retry**: Até 2 tentativas em caso de falha no parse JSON
- **Temperatura**: 0.1 (baixa para consistência)
- **Validação**: Verifica campos obrigatórios antes de retornar

### Geocoding Service

- **Retry**: 3 tentativas com exponential backoff
- **Timeout**: 10s por requisição
- **Rate Limit**: 1s de delay entre requisições (Nominatim)
- **Fallback**: Se endereço não tem cidade, adiciona "Belo Horizonte, MG"

### MinasTaxi Client

```python
@retry(
    exceptions=requests.exceptions.RequestException,
    tries=3,
    delay=2,
    backoff=2  # 2s, 4s, 8s
)
```

- **HTTP 429** (Rate Limit): Retry automático
- **HTTP 5xx** (Server Error): Retry automático
- **HTTP 400** (Bad Request): Falha imediata, não retenta
- **HTTP 401** (Unauthorized): Falha imediata, problema com API key
- **Timeout**: 30s configurável

---

## Logging e Monitoramento

### Níveis de Log

```python
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Locais de Log

1. **Console**: Output em tempo real
2. **Arquivo**: `data/taxi_automation.log`

### Exemplos de Logs

```
2025-12-23 10:30:15 - src.services.email_reader - INFO - Connected to imap.gmail.com as taxi@empresa.com
2025-12-23 10:30:16 - src.services.email_reader - INFO - Fetched email UID=12345, Subject='Novo Agendamento'
2025-12-23 10:30:17 - src.services.llm_extractor - INFO - Successfully extracted data: João Silva
2025-12-23 10:30:18 - src.services.geocoding_service - INFO - Geocoded 'Rua das Flores, 123' -> (-19.9356, -43.9247)
2025-12-23 10:30:20 - src.services.minastaxi_client - INFO - Order successfully dispatched. Order ID: MTX-001234
```

---

## Performance e Otimização

### Benchmarks Esperados

- **Email fetch**: 1-3s para 10 e-mails
- **LLM extraction**: 2-5s por pedido
- **Geocoding** (Nominatim): 1-2s por endereço
- **Geocoding** (Google): 200-500ms por endereço
- **API dispatch**: 500ms - 2s

### Gargalos

1. **Geocoding**: Maior latência no pipeline
   - **Solução**: Cache de endereços comuns (futuro)
   
2. **LLM**: Custo e latência
   - **Solução**: Usar modelos mais rápidos para casos simples

3. **Rate Limits**:
   - Nominatim: 1 req/s
   - OpenAI: 3500 req/min (tier free)

### Otimizações Futuras

- [ ] Cache Redis para geocoding
- [ ] Batch processing de e-mails
- [ ] Fila assíncrona (Celery + RabbitMQ)
- [ ] Clustering geográfico para otimização de rotas

---

## Segurança

### Credenciais

✅ **BOM**:
- Usar `.env` para todas as credenciais
- App Passwords para e-mail
- API keys com permissões mínimas

❌ **RUIM**:
- Hardcoded credentials no código
- Commitar `.env` no Git
- Usar senhas pessoais reais

### Validação de Input

- ✅ Validação de payload antes de enviar para API
- ✅ Sanitização de endereços
- ✅ Validação de formato de telefone (via LLM)
- ✅ Prevenção de duplicatas por email_id

### HTTPS

- Todas as APIs usam HTTPS (OpenAI, Google, MinasTaxi)
- Certificados verificados automaticamente por `requests`

---

## FAQ - Perguntas Frequentes

### 1. O sistema processa e-mails automaticamente?

Não por padrão. Você precisa:
- Executar manualmente: `python -m src.processor`
- OU agendar com cron/Task Scheduler

### 2. Posso usar outro provedor de e-mail além do Gmail?

Sim! Qualquer provedor com suporte IMAP. Ajuste `EMAIL_HOST` e `EMAIL_PORT` no `.env`.

### 3. Quanto custa rodar o sistema?

**Custos**:
- **E-mail**: Gratuito
- **OpenAI**: ~$0.01 por pedido (GPT-4)
- **Geocoding**: Gratuito (Nominatim) ou ~$0.005/pedido (Google)
- **MinasTaxi API**: Depende do contrato

**Estimativa para 1000 pedidos/mês**: ~$10-15

### 4. Como adicionar novos campos para extrair?

Edite [`src/services/llm_extractor.py`](../src/services/llm_extractor.py):
1. Atualize o `SYSTEM_PROMPT` com o novo campo
2. Adicione o campo ao model em [`src/models/order.py`](../src/models/order.py)
3. Atualize o schema do banco em [`src/services/database.py`](../src/services/database.py)

### 5. Como testar sem enviar para a API real?

No `.env`, use uma URL de teste/mock:
```env
MINASTAXI_API_URL=http://localhost:8000/mock
```

Ou comente temporariamente a chamada em `processor.py`.

---

**Última atualização**: 23/12/2025
**Versão do Sistema**: 1.0.0
