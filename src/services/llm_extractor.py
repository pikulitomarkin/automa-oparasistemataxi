"""
LLM-based data extraction service using OpenAI.
"""
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz
import re

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMExtractor:
    """
    Serviço de extração de dados estruturados de e-mails usando LLM.
    Utiliza prompt engineering para garantir JSON estruturado.
    """
    
    # Prompt de sistema otimizado para extração de dados de pedidos de táxi
    SYSTEM_PROMPT = """Você é um assistente especializado em extrair dados estruturados de pedidos de táxi recebidos via e-mail.

Sua tarefa é analisar o corpo do e-mail e extrair APENAS os seguintes campos em formato JSON:

{{
  "passenger_name": "Nome completo do passageiro",
  "phone": "Telefone com DDD (formato: XX XXXXX-XXXX ou similar)",
  "pickup_address": "Endereço completo de coleta (rua, número, bairro, cidade)",
  "dropoff_address": "Endereço completo de destino (ou null se não mencionado)",
  "pickup_time": "Data e hora de coleta no formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
}}

REGRAS IMPORTANTES:
1. Para horários relativos ("amanhã às 14h", "hoje às 15h30", "dia 25 às 10h"), converta para formato ISO 8601 absoluto.
2. Se o ano não for mencionado, assuma o ano atual ou próximo (se a data já passou este ano).
3. Se apenas a hora for mencionada, assuma que é para hoje.
4. Use fuso horário de Brasília (America/Sao_Paulo).
5. Se um campo não puder ser extraído com confiança, use null.
6. Retorne APENAS o JSON, sem texto adicional antes ou depois.
7. Normalize endereços: capitalize corretamente e inclua cidade se não mencionada (assuma Belo Horizonte, MG).

Data/hora de referência para conversões: {reference_datetime}"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Inicializa o extrator LLM.
        
        Args:
            api_key: Chave da API OpenAI.
            model: Modelo a ser usado (default: gpt-4-turbo-preview).
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
            
            # Parse JSON
            data = json.loads(content)
            
            # Validação básica
            if not self._validate_extracted_data(data):
                logger.warning("Extracted data failed validation")
                return None
            
            # Normaliza o horário se necessário
            if data.get('pickup_time'):
                data['pickup_time'] = self._normalize_datetime(data['pickup_time'])
            
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
        required_fields = ['passenger_name', 'phone', 'pickup_address', 'pickup_time']
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                logger.warning(f"Missing or empty required field: {field}")
                return False
        
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
