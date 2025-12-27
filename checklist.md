# ✅ Checklist de Produção - Sistema de Automação de Táxi

**Status Atual:** 🟡 **Pronto para staging, NÃO pronto para produção**

**Data da Análise:** 26 de dezembro de 2025

---

## 🚨 BLOQUEADORES CRÍTICOS

### 🔴 1. API MinasTaxi Não Validada (BLOQUEADOR HARD)

**Status:** ❌ Não Resolvido

**Problema:**
- Payload da API é especulativo e não foi validado com documentação oficial
- Endpoint `/dispatch` não foi testado em ambiente real
- Estrutura de autenticação (Bearer token) não confirmada
- Error codes e respostas da API são assumidas

**Localização:** `src/services/minastaxi_client.py`

**Ações Necessárias:**
- [ ] Obter documentação oficial da API MinasTaxi
- [ ] Validar estrutura exata do payload JSON
- [ ] Confirmar endpoint correto (URL e método HTTP)
- [ ] Testar autenticação em ambiente de teste/sandbox
- [ ] Mapear todos os códigos de erro possíveis
- [ ] Validar formato da resposta de sucesso
- [ ] Atualizar método `dispatch_order()` com payload real
- [ ] Documentar comportamento real da API

**Risco:** Sistema vai falhar 100% ao tentar despachar pedidos em produção.

**Tempo Estimado:** 1-2 dias

---

### 🔴 2. Testes Inexistentes (BLOQUEADOR CRÍTICO)

**Status:** ❌ Pasta `tests/` vazia

**Problema:**
- Zero cobertura de testes
- Impossível validar comportamento do sistema
- Bugs não detectados antes de produção
- Pytest e pytest-cov configurados mas não utilizados

**Ações Necessárias:**
- [ ] Criar `tests/test_email_reader.py` - mock conexão IMAP
- [ ] Criar `tests/test_llm_extractor.py` - mock OpenAI API
- [ ] Criar `tests/test_geocoding_service.py` - mock Nominatim/Google
- [ ] Criar `tests/test_minastaxi_client.py` - mock API MinasTaxi
- [ ] Criar `tests/test_processor.py` - teste pipeline completo end-to-end
- [ ] Criar `tests/test_database.py` - teste operações CRUD
- [ ] Alcançar cobertura mínima de 50%
- [ ] Configurar CI/CD para rodar testes automaticamente

**Exemplo de Estrutura:**
```python
# tests/test_llm_extractor.py
import pytest
from unittest.mock import Mock, patch
from src.services.llm_extractor import LLMExtractor

@patch('openai.OpenAI')
def test_extract_order_data_success(mock_openai):
    # Implementar teste
    pass
```

**Risco:** Bugs em produção sem detecção prévia, impossível fazer refactoring seguro.

**Tempo Estimado:** 2-3 dias

---

### 🔴 3. Backup de Database

**Status:** ❌ Não implementado

**Problema:**
- SQLite armazena todos os pedidos em `data/taxi_orders.db`
- Sem estratégia de backup automático
- Perda de dados irreversível em caso de falha

**Ações Necessárias:**
- [ ] Criar script `backup_database.py` para backup automático
- [ ] Configurar backup diário via Railway Cron Jobs ou script externo
- [ ] Fazer upload de backups para cloud storage (AWS S3, Google Cloud Storage, etc)
- [ ] Implementar rotação de backups (manter últimos 30 dias)
- [ ] Testar processo de restore do backup
- [ ] Documentar procedimento de recuperação

**Exemplo de Script:**
```python
# backup_database.py
import shutil
from datetime import datetime
import os

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source = os.getenv('DATABASE_PATH', 'data/taxi_orders.db')
    backup_path = f'backups/taxi_orders_{timestamp}.db'
    shutil.copy2(source, backup_path)
    # Upload para cloud storage aqui
```

**Risco:** Perda total de dados históricos em caso de falha.

**Tempo Estimado:** 1 dia

---

## 🟡 MELHORIAS IMPORTANTES (Recomendado)

### 🟡 4. Health Check Endpoint

**Status:** ❌ Não implementado

**Problema:**
- Railway precisa validar se aplicação está viva
- Streamlit não tem endpoint `/health` nativo
- Deploy pode não detectar crashes

**Ações Necessárias:**
- [ ] Criar arquivo `health_check.py` com FastAPI simples
- [ ] Adicionar endpoint `GET /health` retornando status do sistema
- [ ] Verificar conectividade com database
- [ ] Atualizar `Procfile` para rodar health check em paralelo
- [ ] Configurar Railway para usar o endpoint

**Exemplo:**
```python
# health_check.py
from fastapi import FastAPI
import sqlite3
import os

app = FastAPI()

@app.get("/health")
def health_check():
    try:
        # Testa conexão com database
        conn = sqlite3.connect(os.getenv('DATABASE_PATH'))
        conn.close()
        return {"status": "healthy", "database": "ok"}
    except:
        return {"status": "unhealthy"}, 503
```

**Tempo Estimado:** 4 horas

---

### 🟡 5. Validação de Environment Variables no Startup

**Status:** ⚠️ Parcialmente implementado

**Problema:**
- Se `.env` estiver incompleto, app quebra em runtime
- Erros genéricos difíceis de debugar
- Type hints mostram `str | None` mas código assume sempre presente

**Ações Necessárias:**
- [ ] Criar `src/config.py` para centralizar configurações
- [ ] Validar variáveis obrigatórias no startup (fail fast)
- [ ] Fornecer mensagens de erro claras
- [ ] Atualizar `src/processor.py` para usar config centralizado

**Exemplo:**
```python
# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Email
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # MinasTaxi
    MINASTAXI_API_KEY = os.getenv('MINASTAXI_API_KEY')
    
    @classmethod
    def validate(cls):
        required = ['EMAIL_HOST', 'EMAIL_USER', 'EMAIL_PASSWORD', 
                   'OPENAI_API_KEY', 'MINASTAXI_API_KEY']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")

# No início do processor.py
Config.validate()
```

**Tempo Estimado:** 3 horas

---

### 🟡 6. Type Hints Completos e Corretos

**Status:** ⚠️ Presentes mas com warnings

**Problema:**
- Múltiplos warnings de tipo no Pylance/mypy
- `dict` sem generics (deve ser `Dict[str, Any]`)
- `Optional[Unknown]` em várias funções
- Dificuldade para detectar bugs de tipo

**Localização:** Principalmente em `src/processor.py` e `src/services/llm_extractor.py`

**Ações Necessárias:**
- [ ] Substituir `dict` por `Dict[str, Any]` em todos os arquivos
- [ ] Adicionar type hints explícitos em métodos que retornam JSON
- [ ] Corrigir `Optional` types para refletir validações
- [ ] Rodar `mypy src/` e corrigir todos os erros
- [ ] Adicionar mypy no CI/CD pipeline

**Exemplo de Correções:**
```python
# Antes
def extract_order_data(self, email_body: str) -> Optional[Dict]:
    
# Depois
from typing import Dict, Any, Optional

def extract_order_data(self, email_body: str) -> Optional[Dict[str, Any]]:
```

**Tempo Estimado:** 4 horas

---

## 🟢 MELHORIAS OPCIONAIS (Nice to Have)

### 🟢 7. Clustering Geográfico

**Status:** 🟡 Código presente mas não implementado

**Problema:**
- Flag `ENABLE_CLUSTERING=true` existe no `.env.example`
- Campo `cluster_id` existe na tabela `orders`
- Funcionalidade não implementada

**Ações Necessárias:**
- [ ] Implementar algoritmo de clustering (K-means ou DBSCAN)
- [ ] Agrupar pedidos próximos geograficamente
- [ ] Otimizar rotas para motoristas
- [ ] OU remover flag e campo se não for necessário

**Tempo Estimado:** 1-2 dias (se implementar)

---

### 🟢 8. Rate Limiting para OpenAI

**Status:** ⚠️ Retry implementado mas sem rate limit

**Problema:**
- Nominatim tem rate limit (1 req/s) implementado
- OpenAI pode ter rate limits dependendo do plano
- Sem controle de requisições por minuto

**Ações Necessárias:**
- [ ] Implementar rate limiter para OpenAI API
- [ ] Adicionar queue de pedidos se necessário
- [ ] Monitorar uso de tokens

**Tempo Estimado:** 4 horas

---

### 🟢 9. Alertas e Notificações

**Status:** ❌ Não implementado

**Problema:**
- Pedidos com falha ficam silenciosos
- Operador precisa checar dashboard manualmente

**Ações Necessárias:**
- [ ] Integrar com Slack/Discord/Email para alertas
- [ ] Notificar quando pedidos entram em `MANUAL_REVIEW`
- [ ] Alertar quando taxa de falha > 10%
- [ ] Daily summary report

**Tempo Estimado:** 1 dia

---

### 🟢 10. Documentação de Runbook Operacional

**Status:** ⚠️ Documentação técnica OK, falta ops

**Ações Necessárias:**
- [ ] Criar `docs/RUNBOOK.md` com procedimentos operacionais
- [ ] Documentar como lidar com pedidos em `MANUAL_REVIEW`
- [ ] Procedimento de troubleshooting de falhas
- [ ] Como fazer rollback de deploy
- [ ] Contatos de emergência

**Tempo Estimado:** 3 horas

---

## 📊 RESUMO DE ESFORÇO

| Categoria | Itens | Tempo Estimado | Prioridade |
|-----------|-------|----------------|------------|
| 🔴 Bloqueadores Críticos | 3 | 4-6 dias | **OBRIGATÓRIO** |
| 🟡 Melhorias Importantes | 3 | 1-2 dias | Recomendado |
| 🟢 Melhorias Opcionais | 4 | 3-5 dias | Nice to Have |

**Total para Produção Mínima Viável:** 5-8 dias de trabalho focado

---

## 🎯 PLANO DE AÇÃO SUGERIDO

### Semana 1: Bloqueadores Críticos
- [ ] **Dia 1-2:** Validar API MinasTaxi (bloqueador hard)
- [ ] **Dia 3-5:** Criar suite de testes (cobertura mínima 50%)
- [ ] **Dia 6:** Implementar backup automático

### Semana 2: Melhorias Importantes + Testes em Staging
- [ ] **Dia 1:** Health check endpoint + validação de env vars
- [ ] **Dia 2:** Corrigir type hints e rodar mypy
- [ ] **Dia 3-5:** Testes em staging completo (end-to-end)

### Pós-Produção: Melhorias Incrementais
- Implementar clustering geográfico se necessário
- Adicionar alertas e notificações
- Criar runbook operacional

---

## ✅ CRITÉRIOS DE APROVAÇÃO PARA PRODUÇÃO

- [x] Código bem estruturado e documentado
- [ ] **API MinasTaxi validada e testada**
- [ ] **Cobertura de testes ≥ 50%**
- [ ] **Backup automático configurado**
- [ ] Health check endpoint funcionando
- [ ] Validação de .env no startup
- [ ] Testes end-to-end passando em staging
- [ ] Documentação completa (incluindo runbook)
- [ ] Deploy Railway configurado e testado
- [ ] Monitoramento e logs operacionais

---

## 📞 PRÓXIMOS PASSOS IMEDIATOS

1. **URGENTE:** Contatar MinasTaxi para obter documentação da API
2. **URGENTE:** Criar testes mínimos para validar lógica de negócio
3. **IMPORTANTE:** Configurar backup do database
4. **RECOMENDADO:** Implementar health check e validação de env vars
5. **OPCIONAL:** Melhorias incrementais pós-lançamento

---

**Última Atualização:** 26 de dezembro de 2025  
**Responsável pela Análise:** GitHub Copilot  
**Próxima Revisão:** Após resolução dos bloqueadores críticos
