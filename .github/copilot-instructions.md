# Sistema de Automação de Táxi - Instruções para IA

## Visão Geral do Sistema

Sistema de processamento automatizado de pedidos de táxi que opera em **pipeline sequencial de 5 fases**:
1. **EmailReader** → Lê e-mails via IMAP (assunto: "Novo Agendamento")
2. **LLMExtractor** → Extrai dados estruturados com GPT-4
3. **GeocodingService** → Converte endereços em coordenadas (Nominatim ou Google Maps)
4. **MinasTaxiClient** → Despacha pedidos via API REST
5. **DatabaseManager** → Persiste tudo no SQLite

O processador principal ([src/processor.py](src/processor.py)) orquestra todo o fluxo no método `_process_single_email()`.

## Modelo de Dados Central

**Order** ([src/models/order.py](src/models/order.py)) é o objeto que flui pelo pipeline com os seguintes status:
- `RECEIVED` → e-mail capturado
- `EXTRACTED` → dados extraídos pelo LLM
- `GEOCODED` → coordenadas obtidas
- `DISPATCHED` → enviado para MinasTaxi (sucesso)
- `FAILED` ou `MANUAL_REVIEW` → requer intervenção

Todos os serviços recebem/retornam `Order` ou modificam seu estado.

## Padrões de Código Específicos

### 1. LLM Prompting (Extração)
O sistema usa **prompt engineering rígido** em [src/services/llm_extractor.py](src/services/llm_extractor.py):
- Sempre retorna JSON puro (sem markdown)
- Converte horários relativos ("amanhã às 14h") para ISO 8601 com timezone `America/Sao_Paulo`
- Normaliza endereços assumindo "Belo Horizonte, MG" se cidade não mencionada
- Usa `temperature=0.1` para máxima consistência
- Método `extract_with_fallback()` tenta 3 vezes com delays crescentes

Ao modificar a extração: mantenha o formato JSON estrito e as conversões de timezone.

### 2. Retry e Error Handling
**Padrão crítico**: todos os serviços externos usam retry com exponential backoff:
- `@retry` decorator do pacote `retry` (veja [src/services/minastaxi_client.py](src/services/minastaxi_client.py))
- Geocoding usa `max_retries` explícito com `time.sleep()`
- Emails marcados como processados mesmo em falha (field `email_id` único)

Nunca deixe falhas silenciosas: sempre atualizar `order.status` e `order.error_message`.

### 3. Ambiente e Configuração
**`.env` é obrigatório** para execução. Ver [.env.example](.env.example) para todas as variáveis.
- Todos os serviços leem config via `os.getenv()` no `__init__`
- Gmail requer **App Password**, não senha normal
- MinasTaxi API é **mock/placeholder** - payload em [src/services/minastaxi_client.py](src/services/minastaxi_client.py) linha 86

### 4. Database Patterns
SQLite em [src/services/database.py](src/services/database.py) usa:
- `email_id` como chave única para deduplicação
- Índices em `status`, `pickup_time`, `created_at`
- Métodos `create_order()` e `update_order()` retornam/modificam IDs
- Sempre usar `with sqlite3.connect()` para garantir commits

## Execução e Debugging

### Comandos Principais
```bash
# Processar novos pedidos (batch)
python run_processor.py

# Dashboard Streamlit (visualização)
streamlit run app_liquid.py
```

### Logs e Troubleshooting
- Logs em `data/taxi_automation.log` (configurável via `LOG_FILE`)
- Pedidos problemáticos ficam em status `MANUAL_REVIEW` ou `FAILED`
- Dashboard mostra métricas em tempo real (mapa, timeline, tabelas)

### Testes
```bash
pytest tests/ -v --cov=src
```

Ao adicionar features, sempre criar testes que mockam APIs externas (OpenAI, Geocoding, MinasTaxi).

## Pontos de Integração Críticos

### OpenAI API
- Modelo: `gpt-4-turbo-preview` (configurável)
- Parsing: usa `json.loads()` em [src/services/llm_extractor.py](src/services/llm_extractor.py) linha 88
- Se falhar parse, retorna `None` → pedido vai para `MANUAL_REVIEW`

### Geocoding (Nominatim/Google)
- **Rate limits**: Nominatim requer 1 req/segundo (implementado com `time.sleep(1)`)
- Fallback: se Google falhar, não há fallback para Nominatim (escolha única no init)
- Coordenadas inválidas (None) → ordem vai para `MANUAL_REVIEW`

### MinasTaxi API (Placeholder)
- **Endpoint atual**: `POST /dispatch` (não validado com API real)
- Payload em [src/services/minastaxi_client.py](src/services/minastaxi_client.py) `dispatch_order()`
- Quando documentação real chegar: ajustar URL, headers, e payload nesse arquivo

## Convenções de Código

- **Docstrings**: Google style com Args/Returns
- **Type hints**: obrigatórios em funções públicas
- **Imports**: agrupados (stdlib, terceiros, locais) com linha em branco entre grupos
- **Logging**: usar `logger.info/warning/error` extensivamente, nunca `print()`
- **Formatação**: Black + Flake8 (ver [requirements.txt](requirements.txt))

## Dashboard (Streamlit)

[app_liquid.py](app_liquid.py) é uma SPA que:
- Lê diretamente do SQLite (não usa API)
- Usa Folium para mapas interativos (marcadores de coleta)
- CSS customizado com tema "Liquid iPhone" (gradientes animados)
- **Sidebar**: frosted glass com métricas em tempo real

Ao modificar UI: respeitar o tema visual existente (variáveis CSS nas linhas 26-280).

## Estrutura de Branches e Deploy

- `main`: produção estável
- Deploy via Railway.app (ver [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md))
- `Procfile` e `railway.toml` configuram deploy automático
- `start.sh` inicia o dashboard Streamlit

---

**Dica final**: Ao adicionar novas fontes de pedidos (WhatsApp, SMS), siga o padrão de [src/services/email_reader.py](src/services/email_reader.py) - retornar lista de `EmailMessage` (ou equivalente) e integrar no `process_new_orders()`.
