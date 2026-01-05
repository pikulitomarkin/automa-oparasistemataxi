# Configuração de Empresa - Mapeamento Código → CNPJ

## Visão Geral

O sistema agora suporta múltiplas empresas através do mapeamento de **código de empresa** (extraído do email) para **CNPJ** (enviado para a API MinasTaxi).

## Como Funciona

### 1. Email contém código da empresa
```
Empresa: 284
ou
*Empresa: 284 - DELP*
ou
Emp. 123
ou
Company: 456
```

### 2. Sistema extrai o código via LLM
O `LLMExtractor` procura por padrões como:
- `Empresa:`, `Emp.`, `Company:`
- Extrai apenas o código numérico (ex: "284")

### 3. Sistema converte código → CNPJ
Usando o arquivo [src/config/company_mapping.py](src/config/company_mapping.py):
```python
COMPANY_CODE_TO_CNPJ = {
    "284": "02572696000156",  # Empresa 284
    "123": "00000000000001",  # Empresa 123
    ...
}
```

### 4. CNPJ é enviado no campo `user` da API MinasTaxi
```json
{
  "user": "02572696000156",  // CNPJ da empresa
  "password": "0104",
  "extra1": "284",  // Código original (para referência)
  ...
}
```

## Campos no Banco de Dados

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `company_code` | TEXT | Código extraído do email | "284" |
| `company_cnpj` | TEXT | CNPJ mapeado | "02572696000156" |

## Configuração

### Adicionar Nova Empresa

Edite [src/config/company_mapping.py](src/config/company_mapping.py):

```python
COMPANY_CODE_TO_CNPJ = {
    "284": "02572696000156",  # DELP
    "123": "00000000000001",  # Nova Empresa 1
    "456": "00000000000002",  # Nova Empresa 2
    "789": "11122233344455",  # Nova Empresa 3 (ADICIONE AQUI)
}
```

### CNPJ Padrão

Se o código da empresa **não for encontrado** no mapeamento, o sistema usa:
```python
DEFAULT_CNPJ = "02572696000156"
```

Para alterar o CNPJ padrão, edite `DEFAULT_CNPJ` no arquivo `company_mapping.py`.

## Migração do Banco de Dados

A migração é **automática**! Quando o sistema inicia, o `DatabaseManager`:
1. Detecta se a coluna `company_cnpj` existe
2. Adiciona automaticamente se não existir
3. Popula CNPJs baseado nos códigos existentes
4. Tudo sem intervenção manual

Isso garante compatibilidade com Railway e outros ambientes cloud.

### Migração Manual (opcional, apenas para ambientes locais)

Se preferir executar manualmente:

```bash
python migrate_add_company_cnpj.py
```

## API MinasTaxi

### Campo `user` (CNPJ da Empresa)
- **Propósito**: Identificar qual empresa está fazendo o pedido
- **Formato**: CNPJ sem formatação (apenas números)
- **Exemplo**: `"02572696000156"`

### Campo `extra1` (Código da Empresa)
- **Propósito**: Referência ao código original do email
- **Formato**: String numérica
- **Exemplo**: `"284"`

## Centro de Custo

**IMPORTANTE**: O campo de centro de custo ainda **não existe na API MinasTaxi**. Quando for criado:

1. Atualizar [src/services/minastaxi_client.py](src/services/minastaxi_client.py)
2. Adicionar campo específico no payload (ex: `cost_center`)
3. Por enquanto, centro de custo é incluído em `passenger_note`

## Fluxo Completo

```
Email
  │
  ├─> LLM Extractor
  │   ├─> company_code = "284"
  │   └─> cost_center = "1.07002.07.001"
  │
  ├─> Processor
  │   └─> company_cnpj = get_cnpj_from_company_code("284")
  │       = "02572696000156"
  │
  ├─> Database
  │   └─> Salva company_code + company_cnpj
  │
  └─> MinasTaxi Client
      └─> Envia:
          {
            "user": "02572696000156",  // CNPJ
            "extra1": "284",           // Código
            "passenger_note": "C.Custo: 1.07002.07.001 | ..."
          }
```

## Logs e Debugging

### Verificar mapeamento
```python
from src.config.company_mapping import list_all_companies

print(list_all_companies())
# {'284': '02572696000156', '123': '00000000000001', ...}
```

### Ver logs do processamento
```bash
tail -f data/taxi_automation.log | grep -i "company\|cnpj"
```

Exemplo de log:
```
2026-01-05 14:30:15 - processor - INFO - Company code 284 mapped to CNPJ 02572696000156
2026-01-05 14:30:20 - minastaxi_client - INFO - Using CNPJ in 'user' field: 02572696000156
2026-01-05 14:30:20 - minastaxi_client - INFO - ✅ Código da empresa (extra1): 284
```

## Testes

Arquivo de teste: `test_company_code_extraction.py`

```bash
python test_company_code_extraction.py
```

Verifica:
- Extração do código da empresa do email
- Mapeamento código → CNPJ
- Envio correto para API MinasTaxi

## Troubleshooting

### Código da empresa não detectado
```
⚠️ WARNING - No company code found in email - will use default CNPJ
```

**Solução**: Verificar se email contém "Empresa:", "Emp." ou similar. Adicionar variações no prompt do LLM se necessário.

### CNPJ padrão sendo usado
```
INFO - Using CNPJ in 'user' field: 02572696000156
```

Se deveria ser outro CNPJ:
1. Verificar se `company_code` foi extraído corretamente
2. Verificar se código existe em `COMPANY_CODE_TO_CNPJ`
3. Adicionar mapeamento se necessário

### Centro de custo não aparece na API
**Normal** - campo ainda não implementado pela Original Software. Por enquanto, aparece apenas em `passenger_note`.

## Próximos Passos

1. ✅ **Implementado**: Mapeamento código → CNPJ
2. ✅ **Implementado**: Envio de CNPJ no campo `user`
3. ⏳ **Aguardando**: Campo específico para centro de custo na API
4. 📋 **Futuro**: Interface web para gerenciar mapeamentos

---

**Última atualização**: 2026-01-05  
**Arquivo de configuração**: [src/config/company_mapping.py](src/config/company_mapping.py)
