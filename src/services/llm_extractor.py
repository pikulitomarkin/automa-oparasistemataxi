"""
LLM-based data extraction service using OpenAI.
"""
import re
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMExtractor:
    """
    Serviço de extração de dados estruturados de e-mails usando LLM.
    Utiliza prompt engineering para garantir JSON estruturado.
    """
    
    # Prompt de sistema otimizado para extração de dados de pedidos de táxi
    SYSTEM_PROMPT = """Você é um assistente especializado em extrair dados estruturados de pedidos de táxi/transporte da CSN Mineração.

Os emails seguem estes padrões:
- Assunto: "PROGRAMAÇÃO DE TAXI/CARRO" + horário
- Corpo: Texto livre ou tabela com dados dos passageiros
- **EMPRESA**: Campo crítico com código (ex: "Empresa: 284", "*Empresa: 284 - Delp*", "Emp. 123")
- **CENTRO DE CUSTO**: Campo crítico (ex: "CC:20086", "Centro de Custo: 1.07002.07.004", "C.Custo: 123")
- Passageiros: Nome, Matrícula (MIN/MIO/MIP), Telefone (OPCIONAL)
- Locais: Podem ser siglas (CSN, BH, MARIANA, LAFAIETE) ou endereços completos
- Horários: Relativos (hoje, amanhã) ou datas específicas

⚠️ ATENÇÃO CRÍTICA:
1. **SEMPRE** procurar por código de empresa usando palavras-chave: Empresa, Emp, Company, Código de Empresa, Código Empresa
2. **SEMPRE** procurar por centro de custo usando: CC, C.Custo, Centro de Custo, Centro Custo, Cost Center
3. Aceitar formatos variados: com/sem pontuação, com/sem espaços, negrito (*), maiúsculas/minúsculas
4. Extrair APENAS números (e pontos/traços no centro de custo)

MAPEAMENTO DE LOCAIS:
- CSN = CSN Mineração, Congonhas, MG (Coordenadas aproximadas: -20.5033, -43.8569)
- BH = Belo Horizonte, MG
- MARIANA = Mariana, MG  
- LAFAIETE/CONSELHEIRO LAFAIETE = Conselheiro Lafaiete, MG
- CONGONHAS = Congonhas, MG

Extraia os seguintes campos em formato JSON:

{{
  "passenger_name": "Nome completo do primeiro passageiro (se múltiplos, separe com vírgula)",
  "phone": "Telefone com DDD (formato: 31988888888 ou similar, remova parênteses e hífens). Se não houver telefone explícito, use string vazia ''",
  "pickup_address": "Endereço/local de COLETA (origem). Se for sigla, expanda: CSN → 'CSN Mineração, Congonhas, MG'",
  "dropoff_address": "Endereço/local de DESTINO. Se for sigla, expanda",
  "pickup_time": "Data e hora de coleta no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS-03:00)",
  "notes": "Todas as observações relevantes: CC, múltiplos passageiros, retorno programado, telefones adicionais, empresa, etc. Incluir TUDO que for relevante",
  "company_code": "CRÍTICO: Extrair código da empresa de QUALQUER formato. Exemplos: 'Empresa: 284' → '284', '*Empresa: 284 - Nome*' → '284', 'Emp. 123' → '123', 'Company: 456' → '456'. Procurar por palavras-chave: Empresa, Emp, Company, Código de Empresa. Retornar APENAS o código numérico. Se não encontrar, retornar string vazia ''",
  "cost_center": "CRÍTICO: Extrair centro de custo de QUALQUER formato. Exemplos: 'CC: 20086' → '20086', 'Centro de Custo: 1.07002.07.004' → '1.07002.07.004', 'C.Custo: 123' → '123', 'CC 456' → '456'. Procurar por: CC, C.Custo, Centro de Custo, Cost Center. Aceitar números simples ou com pontos/traços. Se não encontrar, retornar string vazia ''",
  "payment_type": "Opcional: detectar forma de pagamento se o email mencionar 'Pgto' ou 'Pagamento' seguido de DIN, BE, VOUCHER, BOLETO, ONLINE etc. Retornar APENAS o valor (ex: 'DIN', 'BE'). Se ausente, use string vazia ''",
  "passengers": [
    {{
      "name": "Nome completo do passageiro",
      "phone": "Telefone do passageiro (apenas números com DDD)",
      "address": "Endereço completo do passageiro"
    }}
  ],
  "has_return": false,
  "return_time": "Se houver retorno, horário ISO 8601, senão null",
  "arrival_time": "Se mencionado horário de CHEGADA (não saída), colocar aqui em ISO 8601, senão null"
}}

REGRAS CRÍTICAS:
1. **PRIORIDADE DE DADOS**: Se o email contém TABELA (linhas com │ ou ┌), os dados da tabela TÊM PRIORIDADE ABSOLUTA sobre texto livre. A última coluna da tabela geralmente é o destino. Ignore texto livre que conflite com dados tabulares.

2. **NOME DO PASSAGEIRO**: 
   - Use o nome da primeira linha da tabela
   - Se não houver nome explícito, use a matrícula: "Passageiro MIN7956" ou "Passageiro MIO9580"
   - Para múltiplos passageiros, listar TODOS no array "passengers" com nome, telefone e endereço individual

3. **MÚLTIPLOS PASSAGEIROS**:
   - Se houver VÁRIOS passageiros com endereços diferentes, extrair cada um separadamente no array "passengers"
   - Exemplo: Ellen (Rua Piuai, 1056), Soraria (Rua Maria Ana), etc.
   - O campo "pickup_address" deve conter o PRIMEIRO endereço (coleta inicial)
   - Todos os endereços individuais devem estar no array "passengers"

4. **ENDEREÇOS DE COLETA (pickup_address)**:
   - Em tabelas, a penúltima coluna geralmente é origem
   - Para múltiplos passageiros com endereços diferentes, use o PRIMEIRO endereço da lista
   - Liste todos os endereços em notes: "Múltiplos endereços: [lista]"
   - Expanda siglas: CSN → "CSN Mineração, Congonhas, MG"

4. **ENDEREÇOS DE DESTINO (dropoff_address)**:
   - Em tabelas, a ÚLTIMA coluna é o destino
   - Se texto livre diz "destino X" mas tabela mostra "Y", use Y da tabela
   - Expanda siglas: BH → "Belo Horizonte, MG", MARIANA → "Mariana, MG"

5. **HORÁRIOS**:
   - "amanhã 16:00H" → converter para data/hora absoluta ISO 8601
   - "hoje" → usar data atual + hora mencionada
   - Sempre incluir timezone de Brasília (-03:00) no pickup_time
   - **IMPORTANTE**: Se mencionar "Horário de chegada" (ex: 05H40), este é o horário que o passageiro DEVE CHEGAR no destino
   - Para "horário de chegada", colocar em "arrival_time", e calcular pickup_time como: arrival_time - 30 minutos
   - NUNCA calcule mais que 30 minutos de diferença entre pickup e arrival
   - Se não houver "horário de chegada", usar o horário mencionado como pickup_time direto

6. **TELEFONES**:
   - Remover caracteres especiais, manter apenas números com DDD
   - Se não houver telefone explícito, deixar campo vazio ''
   - Telefones adicionais vão em notes

7. **RETORNO**: 
   - Se mencionar "RETORNO" ou "Horário de retorno", marcar has_return=true
   - Extrair horário de retorno em return_time (ISO 8601)
   - Sistema criará 2 viagens: IDA e VOLTA

8. **FORMATO DE SAÍDA**: 
   - Retorne APENAS JSON válido, sem texto adicional, markdown ou comentários
   - Use aspas duplas (")
   - NÃO inclua vírgulas pendentes no final de arrays ou objetos
   - NÃO adicione comentários dentro do JSON
   - Valide a estrutura antes de retornar
   - Se um campo for null, use null (não string vazia para campos nullable)

9. **EXEMPLO DE JSON VÁLIDO**:
```json
{{
  "passenger_name": "João Silva",
  "phone": "31988888888",
  "pickup_address": "CSN Mineração, Congonhas, MG",
  "dropoff_address": "Belo Horizonte, MG",
  "pickup_time": "2026-01-04T14:00:00-03:00",
  "notes": "CC: 20086",
  "passengers": [],
  "has_return": false,
  "return_time": null,
  "arrival_time": null
}}
```

Data/hora de referência: {reference_datetime}"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Inicializa o extrator LLM.
        
        Args:
            api_key: Chave da API OpenAI.
            model: Modelo a ser usado (default: gpt-4o).
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.timezone = pytz.timezone('America/Sao_Paulo')
    
    def extract_order_data(self, email_body: str) -> Optional[Dict]:
        """
        Extrai dados estruturados do corpo do e-mail.
        
        Args:
            email_body: Texto do corpo do e-mail.
            
        Returns:
            Dicionário com os dados extraídos ou None se falhar.
        """
        try:
            # Data/hora de referência para conversões relativas
            ref_datetime = datetime.now(self.timezone).isoformat()
            
            # Prepara o prompt
            system_prompt = self.SYSTEM_PROMPT.format(
                reference_datetime=ref_datetime
            )
            
            # Chama a API OpenAI
            logger.info(f"Calling OpenAI API with model {self.model}...")
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"E-mail do pedido:\n\n{email_body}"}
                    ],
                    temperature=0.1,  # Baixa temperatura para mais consistência
                    max_tokens=500
                )
            except Exception as api_error:
                logger.error(f"OpenAI API call failed: {api_error}")
                raise
            
            # Extrai o conteúdo da resposta
            content = response.choices[0].message.content.strip()
            logger.info(f"LLM raw response: {content[:200]}...")  # Log da resposta
            
            # Remove possíveis markdown code blocks e outros caracteres
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            content = content.strip()
            
            # Tenta encontrar JSON válido na resposta
            # Remove possíveis textos antes/depois do JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            logger.info(f"JSON after cleanup: {content[:200]}...")  # Log após limpeza

            # Parse JSON (tenta reparar se falhar)
            try:
                data = json.loads(content)
            except json.JSONDecodeError as jde:
                logger.warning(f"Initial JSON parse failed: {jde}. Attempting repair...")
                repaired = self._repair_json(content)
                try:
                    data = json.loads(repaired)
                    logger.info("JSON parsed after repair")
                except Exception as e2:
                    logger.error(f"JSON repair failed: {e2}")
                    # Tenta fallback por regex no corpo do e-mail
                    fallback = self._fallback_parse(email_body)
                    if fallback:
                        logger.info("Fallback regex parser returned data")
                        return fallback
                    raise
            
            # Validação básica
            if not self._validate_extracted_data(data):
                logger.warning("Extracted data failed validation")
                return None
            
            # Normaliza o horário se necessário
            if data.get('pickup_time'):
                data['pickup_time'] = self._normalize_datetime(data['pickup_time'])
            
            # Se tem arrival_time mas pickup_time está muito longe, ajusta para 30min antes
            if data.get('arrival_time') and data.get('pickup_time'):
                arrival_dt = parser.parse(data['arrival_time'])
                pickup_dt = parser.parse(data['pickup_time'])
                
                # Calcula diferença
                diff = arrival_dt - pickup_dt
                diff_minutes = diff.total_seconds() / 60
                
                # Se diferença > 30 minutos, ajusta para 30 minutos antes
                if diff_minutes > 30:
                    from datetime import timedelta
                    pickup_dt = arrival_dt - timedelta(minutes=30)
                    data['pickup_time'] = pickup_dt.isoformat()
                    logger.info(f"Adjusted pickup_time to 30 minutes before arrival: {data['pickup_time']}")
            
            # Normaliza horário de retorno se existir
            if data.get('return_time'):
                data['return_time'] = self._normalize_datetime(data['return_time'])
            
            # Normaliza nome do campo de destino (LLM pode retornar dropoff ou destination)
            if 'dropoff_address' in data and 'destination_address' not in data:
                data['destination_address'] = data['dropoff_address']
            
            logger.info(f"Successfully extracted data: {data.get('passenger_name')}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"LLM response was: {content[:500]}")  # Mostra primeiros 500 chars
            return None
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            if 'content' in locals():
                logger.error(f"LLM response was: {content[:500]}")
            return None
    
    def _validate_extracted_data(self, data: Dict) -> bool:
        """
        Valida se os dados extraídos têm estrutura mínima esperada.
        
        Args:
            data: Dicionário com dados extraídos.
            
        Returns:
            True se válido, False caso contrário.
        """
        # Campos obrigatórios
        required_fields = ['passenger_name', 'pickup_address', 'pickup_time']
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                logger.warning(f"Missing or empty required field: {field}")
                return False
        
        # Phone é opcional, mas logga warning se não tiver
        if 'phone' not in data or not data['phone']:
            logger.warning("Phone field is missing or empty - ordem pode falhar no dispatch")
        
        return True
    
    def _normalize_datetime(self, dt_string: str) -> str:
        """
        Normaliza string de data/hora para formato ISO 8601.
        
        Args:
            dt_string: String de data/hora.
            
        Returns:
            String no formato ISO 8601.
        """
        try:
            # Tenta fazer parse da string
            dt = parser.parse(dt_string)
            
            # Se não tem timezone, adiciona o de Brasília
            if dt.tzinfo is None:
                dt = self.timezone.localize(dt)
            
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Failed to normalize datetime '{dt_string}': {e}")
            return dt_string
    
    def extract_with_fallback(self, email_body: str, max_retries: int = 2) -> Optional[Dict]:
        """
        Extrai dados com tentativas de retry em caso de falha.
        
        Args:
            email_body: Corpo do e-mail.
            max_retries: Número máximo de tentativas.
            
        Returns:
            Dados extraídos ou None.
        """
        for attempt in range(max_retries + 1):
            result = self.extract_order_data(email_body)
            if result:
                return result
            
            if attempt < max_retries:
                logger.warning(f"Extraction failed, retrying... (attempt {attempt + 1}/{max_retries})")
        
        logger.error(f"Failed to extract data after {max_retries + 1} attempts")
        return None

    def _repair_json(self, content: str) -> str:
        """
        Tenta reparar JSON truncado ou com vírgulas finais comuns.
        Estratégia simples e prática:
        - Remove caracteres de code fences restantes
        - Remove vírgulas finais antes de '}' ou ']' 
        - Tenta balancear chaves adicionando '}' ao final se necessário
        - Substitui aspas simples por aspas duplas quando for seguro
        """
        s = content.strip()
        # Remove backticks e markers
        s = re.sub(r'```+', '', s)
        # Substitui aspas simples por duplas (cuidado): só quando não houver aspas duplas
        if "'" in s and '"' not in s:
            s = s.replace("'", '"')

        # Remove vírgulas finais antes de fechamento
        s = re.sub(r',\s*(\}|\])', r'\1', s)

        # Balanceamento simples de chaves
        open_braces = s.count('{')
        close_braces = s.count('}')
        if close_braces < open_braces:
            s += '}' * (open_braces - close_braces)

        # Balanceamento de colchetes
        open_brackets = s.count('[')
        close_brackets = s.count(']')
        if close_brackets < open_brackets:
            s += ']' * (open_brackets - close_brackets)

        return s

    def _fallback_parse(self, email_body: str) -> Optional[Dict]:
        """
        Parseia o corpo do e-mail por heurísticas (regex) para extrair campos essenciais
        quando o LLM não retorna JSON válido. Retorna um dict parcial que segue o
        formato mínimo necessário para inserção no pipeline.
        """
        try:
            text = email_body
            # Phones: pega o primeiro número com 8-13 dígitos
            phones = re.findall(r'\b(55)?\s*\(?0?\d{2}\)?\s*\d{4,9}\b', text)
            # Melhor forma: extrair sequências de dígitos com 10-13 caracteres
            phones_alt = re.findall(r'(?:\+?55)?\D*(\d{10,13})', text)
            phone = phones_alt[0] if phones_alt else ''

            # Names: linhas que começam com Nome: or Passageiro:
            name_match = re.search(r'(?:Nome|Passageiro)[:\s-]+([A-ZÀ-Ÿa-zà-ÿ\s]+)', text)
            name = name_match.group(1).strip() if name_match else ''

            # Pickup: procurar 'Origem' ou 'Pickup' ou linhas com 'Rua'/'Av.'
            pickup_match = re.search(r'(?:Origem|Pickup|Pickup:|Pickup )[:\s-]*(.+)', text)
            if not pickup_match:
                pickup_match = re.search(r'((?:Rua|Av(?:enida)?|Avenida|RUA|AVENIDA)[^\n,]+)', text)
            pickup = pickup_match.group(1).strip() if pickup_match else ''

            # Dropoff: procurar 'Destino' ou 'Delp' etc.
            drop_match = re.search(r'(?:Destino|Dropoff|Destino:)[:\s-]*(.+)', text)
            if not drop_match:
                drop_match = re.search(r'(Delp Engenharia[^\n]+|Aeroporto[^\n]+)', text)
            dropoff = drop_match.group(1).strip() if drop_match else ''

            # Horário: data aproximada
            date_match = re.search(r'(\d{2}/\d{2}/\d{2,4})', text)
            time_match = re.search(r'(\d{1,2}:\d{2})', text)
            pickup_time = None
            if date_match and time_match:
                # tenta formar ISO
                try:
                    dt = parser.parse(f"{date_match.group(1)} {time_match.group(1)}")
                    pickup_time = self._normalize_datetime(dt.isoformat())
                except Exception:
                    pickup_time = None

            result = {
                'passenger_name': name or 'Multiple passengers',
                'phone': phone or '',
                'pickup_address': pickup or '',
                'dropoff_address': dropoff or '',
                'pickup_time': pickup_time or '',
                'notes': 'Parsed by fallback regex',
                'passengers': [],
                'has_return': False,
                'return_time': None,
                'arrival_time': None
            }
            # validação mínima
            if not result['passenger_name'] or not result['pickup_address']:
                return None
            return result
        except Exception as e:
            logger.error(f"Fallback parse error: {e}")
            return None
