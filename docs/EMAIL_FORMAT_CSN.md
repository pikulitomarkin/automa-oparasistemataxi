# 📧 Formato de Emails - CSN Mineração

## Padrões Identificados

Os emails de solicitação de táxi da CSN Mineração seguem estes formatos:

### **Formato 1: Email Simples com Tabela**

```
Assunto: PROGRAMAÇÃO DE TAXI amanhã 16:00H

Prezados, boa Noite!

Gentileza programar um TAXI amanhã 06/09/2025 16:00H

CSN DESTINHO BH

CC:20086

┌────────────────────────────┬────────┬──────────────┬──────┬─────────┐
│ EDIMAR JULIO FERREIRA SOARES│ MIN7956│ (31)988873751│ CSN  │ MARIANA │
│ FERNANDO ANGELO GONCALVES   │ MIN7956│ (31)984840900│      │         │
└────────────────────────────┴────────┴──────────────┴──────┴─────────┘
```

**Extração esperada:**
- Nome: "EDIMAR JULIO FERREIRA SOARES, FERNANDO ANGELO GONCALVES"
- Telefone: "31988873751"
- Origem: "CSN Mineração, Congonhas, MG"
- Destino: "Mariana, MG"
- Horário: 2025-09-06T16:00:00-03:00
- Notes: "CC:20086, 2 passageiros: EDIMAR (MIN7956), FERNANDO (MIN7956)"

---

### **Formato 2: Email com Destino Especificado**

```
Assunto: PROGRAMAÇÃO DE TAXI amanhã 15:30h

Prezados, boa Noite!

Gentileza programar um TAXI amanhã 06/09/2025 15:30h

CSN DESTINHO BH

CC:20063

┌────────────────────────────┬────────┬──────────────┬──────┬──────┐
│ Harlle Jonathan da Rocha   │ MIP 0060│ 37998742019 │ CSN  │  BH  │
└────────────────────────────┴────────┴──────────────┴──────┴──────┘
```

**Extração esperada:**
- Nome: "Harlle Jonathan da Rocha"
- Telefone: "37998742019"
- Origem: "CSN Mineração, Congonhas, MG"
- Destino: "Belo Horizonte, MG"
- Horário: 2025-09-06T15:30:00-03:00
- Notes: "CC:20063, Matrícula: MIP 0060"

---

### **Formato 3: Email com Endereço Completo**

```
Assunto: PROGRAMAÇÃO DE TAXI hoje 04:30h

Prezados, bom dia!

Gentileza programar um TAXI hoje 04:30h

CC:20381

RUA BARRAS, N200 BAIRRO CALAFATE destino CSN

┌────────┬────────┬──────────────────────┐
│ MAICON │ MIO3554│ 9 8440-1424/9 9062-6923│
└────────┴────────┴──────────────────────┘
```

**Extração esperada:**
- Nome: "MAICON"
- Telefone: "98440-1424"
- Origem: "Rua Barras, 200, Bairro Calafate, Belo Horizonte, MG"
- Destino: "CSN Mineração, Congonhas, MG"
- Horário: 2025-08-31T04:30:00-03:00 (hoje + hora)
- Notes: "CC:20381, Matrícula: MIO3554, Telefone alternativo: 99062-6923"

---

### **Formato 4: Múltiplos Passageiros com Endereços Detalhados**

```
Assunto: PROGRAMAÇÃO DE CARRO HOJE 15:00h

Prezados, boa Tarde!

Gentileza programar CARRO HOJE 15:00 FERNANDINHO 15:00h DESTINO LAFAIETE

CC:20049

┌───────────────────┬────────┬────────────────────────────────┬────────────────────┐
│ GRACY ADRIANE COSTA│MNC0789│RUA JOSE ALEXANDRE RAMOS, 38   │CONSELHEIRO LAFAIETE│
│ AGNALDO FERNANDES  │MI05688│RUA ETELVINA DE LIMA,426, STA M│CONSELHEIRO LAFAIETE│
│ MARCIANO           │MNC0220│RUA JOAO FERREIRA, 346, S.C. JE│CONSELHEIRO LAFAIETE│
│ DIEGO              │       │RUA ARNALDO SEZARINO 18 FONTE G│                    │
└───────────────────┴────────┴────────────────────────────────┴────────────────────┘
```

**Extração esperada:**
- Nome: "GRACY ADRIANE COSTA, AGNALDO FERNANDES, MARCIANO, DIEGO"
- Telefone: (buscar no contexto ou deixar primeiro encontrado)
- Origem: "Rua Jose Alexandre Ramos, 38, Conselheiro Lafaiete, MG"
- Destino: "Conselheiro Lafaiete, MG"
- Horário: 2025-08-23T15:00:00-03:00
- Notes: "CC:20049, 4 passageiros com endereços diferentes. GRACY (MNC0789), AGNALDO (MI05688), MARCIANO (MNC0220), DIEGO"

---

### **Formato 5: Ida e Volta**

```
Assunto: PROGRAMAÇÃO DE CARRO AMANHÃ 23/08/2025

Prezados, boa Noite!

Gentileza programar um TÁXI AMANHÃ 23/08/2025 04:00H E RETORNO 16:00H

CC:20049

┌──────────┬────────┬────────────────────────────┬──────────────┬─────────────────────────────┬────────┬──────┬─┐
│23/08/2025│ MIO9580│ Rua Antonio Barbosa 55     │Ibirité / MG  │Estrada Casa de Pedra, S/N   │Congonhas│04:00 │-│
│          │        │ centro                     │              │Zona Rural                   │/ MG     │      │ │
├──────────┼────────┼────────────────────────────┼──────────────┼─────────────────────────────┼────────┼──────┼─┤
│23/08/2025│ MIO9580│ Estrada Casa de Pedra, S/N │Congonhas / MG│Rua Antonio Barbosa 55-centro│Ibirité │16:00 │-│
│          │        │ Zona Rural                 │              │                             │/ MG     │      │ │
└──────────┴────────┴────────────────────────────┴──────────────┴─────────────────────────────┴────────┴──────┴─┘
```

**Extração esperada:**
- Nome: "Passageiro MIO9580"
- Telefone: (buscar ou inferir)
- Origem: "Rua Antonio Barbosa, 55, Centro, Ibirité, MG"
- Destino: "Estrada Casa de Pedra, S/N, Zona Rural, Congonhas, MG"
- Horário IDA: 2025-08-23T04:00:00-03:00
- Notes: "CC:20049, RETORNO às 16:00 de Congonhas para Ibirité. Matrícula: MIO9580"

---

## Mapeamento de Locais Comuns

| Sigla/Termo | Endereço Completo | Coordenadas Aproximadas |
|-------------|-------------------|-------------------------|
| CSN | CSN Mineração, Congonhas, MG | -20.5033, -43.8569 |
| BH | Belo Horizonte, MG | -19.9191, -43.9387 |
| MARIANA | Mariana, MG | -20.3778, -43.4172 |
| LAFAIETE / CONSELHEIRO LAFAIETE | Conselheiro Lafaiete, MG | -20.6606, -43.7858 |
| CONGONHAS | Congonhas, MG | -20.5033, -43.8569 |
| IBIRITÉ | Ibirité, MG | -20.0219, -44.0588 |

---

## Configuração do Sistema

### Variável de Ambiente

```env
EMAIL_SUBJECT_FILTER=PROGRAMAÇÃO
```

Isso capturará:
- "PROGRAMAÇÃO DE TAXI amanhã 16:00H"
- "PROGRAMAÇÃO DE CARRO HOJE 15:00h"
- "PROGRAMAÇÃO DE CARRO AMANHÃ 23/08/2025"

### LLM Prompt

O sistema LLM foi configurado para:
1. ✅ Reconhecer siglas e expandi-las
2. ✅ Converter horários relativos (hoje, amanhã)
3. ✅ Extrair dados de tabelas e texto livre
4. ✅ Identificar múltiplos passageiros
5. ✅ Detectar viagens de retorno
6. ✅ Normalizar telefones (remover caracteres especiais)
7. ✅ Adicionar timezone de Brasília (-03:00)
8. ✅ Fallback por regex: se o LLM omitir destino ou forma de pagamento, tentamos capturar linhas `Destino:` / `Pagamento:` no corpo do email

---

## Testes Recomendados

Para testar o sistema com seus emails reais:

1. **Configure o filtro de assunto**:
   ```env
   EMAIL_SUBJECT_FILTER=PROGRAMAÇÃO
   ```

2. **Execute o processador**:
   ```bash
   python run_processor.py
   ```

3. **Verifique os logs**:
   ```bash
   tail -f data/taxi_automation.log
   ```

4. **Confira o Dashboard**:
   ```bash
   streamlit run app_liquid.py
   ```

---

## Próximos Passos

1. ✅ LLM atualizado para reconhecer formato CSN
2. ✅ Filtro de email ajustado para "PROGRAMAÇÃO"
3. ⏭️ Testar com emails reais
4. ⏭️ Ajustar geocoding para locais CSN
5. ⏭️ Validar integração com MinasTaxi API

**O sistema está pronto para processar os emails da CSN Mineração!** 🚀
