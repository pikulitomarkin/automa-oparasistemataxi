# 📧 Template de Email para Pedidos de Táxi

## Formato Esperado pelo Sistema

O sistema processa emails com **assunto: "Novo Agendamento"** e extrai automaticamente os seguintes dados:

### Campos Obrigatórios

1. **Nome do Passageiro**
2. **Telefone** (com DDD)
3. **Endereço de Coleta** (completo)
4. **Data/Hora da Coleta**

### Campos Opcionais

5. **Endereço de Destino**

---

## ✅ Exemplos de Emails Válidos

### Exemplo 1 - Formato Simples
```
Assunto: Novo Agendamento

Nome: João Silva
Telefone: 31 98765-4321
Endereço de coleta: Rua das Flores, 123, Savassi, Belo Horizonte
Horário: amanhã às 14h
```

### Exemplo 2 - Com Destino
```
Assunto: Novo Agendamento

Passageiro: Maria Oliveira
Tel: (31) 99887-6655
Coleta: Av. Afonso Pena, 1500, Centro, Belo Horizonte
Destino: Aeroporto de Confins
Horário: dia 25/12 às 10h
```

### Exemplo 3 - Formato Livre (Natural)
```
Assunto: Novo Agendamento

Olá,

Preciso de um táxi para hoje às 15h30.

Meu nome é Pedro Costa, telefone 31 97654-3210.
Endereço de coleta: Rua Tupis, 456, Centro, BH.

Obrigado!
```

### Exemplo 4 - Formato Estruturado
```
Assunto: Novo Agendamento

==== DADOS DO PASSAGEIRO ====
Nome: Ana Santos
Telefone: 31 3333-4444

==== DETALHES DA CORRIDA ====
Origem: Praça da Liberdade, s/n, Funcionários, Belo Horizonte
Destino: Shopping Del Rey
Data: 26/12/2025
Hora: 18:00
```

---

## 🤖 O Sistema Entende Automaticamente

### Variações de Horário
- "amanhã às 14h" → converte para data/hora ISO 8601
- "hoje às 15h30" → usa data atual
- "dia 25 às 10h" → usa mês/ano atual
- "25/12/2025 às 10:00" → formato exato
- "daqui a 2 horas" → calcula a partir do momento atual

### Variações de Endereço
- Abreviações: "BH" → "Belo Horizonte"
- Sem cidade: "Rua X, 123, Savassi" → adiciona "Belo Horizonte, MG"
- Pontos de referência: "Shopping Del Rey" → geocodifica automaticamente

### Variações de Telefone
- (31) 98765-4321
- 31 98765-4321
- 31987654321
- +55 31 98765-4321

---

## ⚠️ Importante

### O que pode causar "Revisão Manual"
- **Falta de dados obrigatórios** (nome, telefone, endereço ou horário)
- **Endereço não encontrado** pelo geocoding
- **Horário ambíguo** que a IA não consegue interpretar
- **Formato muito confuso** ou misturado com outros textos

### Boas Práticas
✅ Use uma estrutura clara (campos separados)
✅ Inclua sempre cidade/bairro no endereço
✅ Especifique data e hora de forma clara
✅ Mantenha o assunto como "Novo Agendamento"

---

## 🔧 Personalizando o Sistema

Se você tem um formato específico de email (ex: sistema legado, formulário web), você pode:

1. **Ajustar o prompt do LLM** em `src/services/llm_extractor.py`
2. **Adicionar pré-processamento** no `email_reader.py`
3. **Criar campos customizados** no modelo `Order`

### Exemplo: Adaptando para Sistema Legado

Se seus emails vêm no formato:
```
PEDIDO #12345
CLIENTE: João Silva (31987654321)
LOCAL: Rua X, 123
QUANDO: 2025-12-25 14:00:00
```

Entre em contato para ajustarmos o extrator LLM!

---

## 📬 Para Enviar Email de Teste

**Envie para:** virso2016@gmail.com  
**Assunto:** Novo Agendamento  
**Corpo:** Use um dos exemplos acima

Depois execute: `.\.venv\Scripts\python.exe run_processor.py`
