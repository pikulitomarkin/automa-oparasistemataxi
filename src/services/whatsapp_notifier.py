"""
WhatsApp notification service using Evolution API.
"""
import logging
import re
import requests
from typing import Dict, Optional
from retry import retry

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """
    Serviço de notificação via WhatsApp usando Evolution API.
    Envia confirmações de agendamento para clientes.
    """
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        instance_name: str,
        timeout: int = 30
    ):
        """
        Inicializa o notificador WhatsApp.
        
        Args:
            api_url: URL base da Evolution API (ex: https://evolution.example.com).
            api_key: Chave de autenticação da Evolution API.
            instance_name: Nome da instância WhatsApp na Evolution.
            timeout: Timeout para requisições em segundos.
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.timeout = timeout
        
        # Headers padrão para todas as requisições
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"WhatsApp notifier initialized for instance {instance_name}")
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normaliza telefone para formato E.164 internacional.
        
        Formato esperado: 55 + DDD (2 dígitos) + Número (8-9 dígitos)
        
        Args:
            phone: Telefone em qualquer formato.
            
        Returns:
            Telefone normalizado (apenas dígitos com prefixo 55).
            
        Examples:
            "(31) 98888-8888" -> "5531988888888"
            "31 977776666" -> "5531977776666"
            "5531988887777" -> "5531988887777"
        """
        # Remove todos os caracteres não numéricos
        digits_only = re.sub(r'\D', '', phone)
        
        # Se não começar com 55, adiciona
        if not digits_only.startswith('55'):
            digits_only = '55' + digits_only
        
        # Validação básica: 55 + 2 dígitos DDD + 8-9 dígitos número
        if len(digits_only) < 12 or len(digits_only) > 13:
            logger.warning(f"Phone number {phone} may be invalid: {digits_only}")
        
        return digits_only
    
    def generate_success_message(self, name: str, destination: str) -> str:
        """
        Gera mensagem de confirmação de agendamento bem-sucedido.
        
        Args:
            name: Nome do passageiro.
            destination: Endereço de destino.
            
        Returns:
            Texto da mensagem formatado.
        """
        return (
            f"Olá, {name}! 🚖\n\n"
            f"Seu táxi para *{destination}* foi agendado com sucesso pela nossa central.\n\n"
            f"O motorista chegará em breve. Tenha uma ótima viagem! ✨"
        )
    
    def generate_error_message(self, name: str, destination: str) -> str:
        """
        Gera mensagem de erro com suporte humano.
        
        Args:
            name: Nome do passageiro.
            destination: Endereço de destino.
            
        Returns:
            Texto da mensagem formatado.
        """
        return (
            f"Olá, {name}.\n\n"
            f"Tivemos uma instabilidade ao processar seu pedido para *{destination}*.\n\n"
            f"Nossa equipe humana já foi acionada e entrará em contato em instantes "
            f"para confirmar seu táxi. 🕐\n\n"
            f"Agradecemos a compreensão!"
        )
    
    def build_message_payload(
        self,
        phone: str,
        message: str
    ) -> Dict[str, str]:
        """
        Constrói o payload JSON para Evolution API.
        
        Args:
            phone: Telefone do destinatário (será normalizado).
            message: Texto da mensagem.
            
        Returns:
            Payload JSON pronto para envio.
        """
        normalized_phone = self.normalize_phone(phone)
        
        payload = {
            "number": normalized_phone,
            "text": message
        }
        
        return payload
    
    @retry(
        exceptions=requests.exceptions.RequestException,
        tries=3,
        delay=2,
        backoff=2,
        logger=logger
    )
    def send_message(
        self,
        name: str,
        phone: str,
        destination: str,
        status: str
    ) -> Dict:
        """
        Envia mensagem de confirmação via WhatsApp.
        
        Args:
            name: Nome do passageiro.
            phone: Telefone do passageiro.
            destination: Endereço de destino.
            status: Status do agendamento ("Sucesso" ou "Erro").
            
        Returns:
            Resposta da API Evolution.
            
        Raises:
            requests.exceptions.RequestException: Em caso de erro na API.
        """
        # Gera mensagem baseada no status
        if status.lower() in ['sucesso', 'success', 'dispatched']:
            message = self.generate_success_message(name, destination)
        else:
            message = self.generate_error_message(name, destination)
        
        # Constrói payload
        payload = self.build_message_payload(phone, message)
        
        # URL do endpoint
        endpoint = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        try:
            logger.info(f"Sending WhatsApp to {payload['number']}: {name}")
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Log da resposta
            logger.debug(f"Request to {endpoint}: {payload}")
            logger.debug(f"Response status: {response.status_code}")
            
            # Verifica sucesso
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"WhatsApp sent successfully to {name}")
                return {
                    'success': True,
                    'message_id': data.get('key', {}).get('id'),
                    'payload': payload
                }
            else:
                error_msg = f"Evolution API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise requests.exceptions.RequestException(error_msg)
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending WhatsApp to {name}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp to {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp: {e}")
            raise
    
    def send_manual_review_alert(
        self,
        phone: str,
        name: str,
        reason: str
    ) -> Dict:
        """
        Envia alerta de pedido em revisão manual.
        
        Args:
            phone: Telefone do cliente.
            name: Nome do cliente.
            reason: Motivo da revisão manual.
            
        Returns:
            Resposta da API Evolution.
        """
        message = (
            f"Olá, {name}.\n\n"
            f"Seu pedido de táxi está em análise pela nossa equipe.\n\n"
            f"Entraremos em contato em breve para confirmar todos os detalhes. "
            f"Agradecemos a paciência! 🙏"
        )
        
        payload = self.build_message_payload(phone, message)
        endpoint = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Manual review alert sent to {name}")
                return {'success': True, 'payload': payload}
            else:
                logger.error(f"Failed to send manual review alert: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error sending manual review alert: {e}")
            return {'success': False, 'error': str(e)}
