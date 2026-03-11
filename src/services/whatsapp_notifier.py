"""
WhatsApp notification service using Evolution API.
"""
import logging
import re
import time
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
        auth_header_name: str = 'apikey',
        timeout: int = 60
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
        self.auth_header_name = auth_header_name
        self.timeout = timeout
        
        # Headers padrão para todas as requisições.
        # O nome do header de autenticação é configurável porque
        # versões diferentes da Evolution usam chaves distintas
        # (ex: 'apikey' ou 'authentication_api_key').
        self.headers = {
            'Content-Type': 'application/json'
        }

        # Define o header principal de autenticação conforme informado.
        # Também mantém 'apikey' presente para compatibilidade reversa
        # caso a API aceite ambos.
        if self.auth_header_name:
            self.headers[self.auth_header_name] = api_key
        if self.auth_header_name.lower() != 'apikey':
            # incluir 'apikey' como fallback compatível
            self.headers['apikey'] = api_key
        
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
    
    def generate_success_message(self, name: str, destination: str, pickup_time: str = None) -> str:
        """
        Gera mensagem de confirmação de agendamento bem-sucedido.
        
        Args:
            name: Nome do passageiro.
            destination: Endereço de destino.
            pickup_time: Data e hora do agendamento formatada (ex: "Segunda-feira, 04/01/2026 às 14:00").
            
        Returns:
            Texto da mensagem formatado.
        """
        if pickup_time:
            return (
                f"Olá, {name}! 🚖\n\n"
                f"Seu táxi para *{destination}* foi agendado com sucesso pela nossa central.\n\n"
                f"📅 *Data/Hora:* {pickup_time}\n\n"
                f"O motorista chegará em breve. Tenha uma ótima viagem! ✨"
            )
        else:
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
    
    def _validate_phone_exists(self, phone: str) -> bool:
        """
        Valida se o número de telefone existe no WhatsApp antes de enviar.
        
        Args:
            phone: Telefone normalizado (formato: 5531999999999)
            
        Returns:
            True se o número existe no WhatsApp, False caso contrário.
        """
        endpoint = f"{self.api_url}/chat/whatsappNumbers/{self.instance_name}"
        
        try:
            response = requests.post(
                endpoint,
                json={"numbers": [phone]},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Verifica se o número existe
                if isinstance(data, list) and len(data) > 0:
                    exists = data[0].get('exists', False)
                    if not exists:
                        logger.warning(f"Phone {phone} does not exist on WhatsApp")
                    return exists
            return False
        except Exception as e:
            logger.warning(f"Phone validation failed: {e}, assuming valid")
            return True  # Em caso de erro na validação, assume válido para não bloquear
    
    @retry(
        exceptions=requests.exceptions.RequestException,
        tries=5,
        delay=2,
        backoff=2,
        logger=logger
    )
    def send_message(
        self,
        name: str,
        phone: str,
        destination: str,
        status: str,
        pickup_time: str = None
    ) -> Dict:
        """
        Envia mensagem de confirmação via WhatsApp.
        
        Args:
            name: Nome do passageiro.
            phone: Telefone do passageiro.
            destination: Endereço de destino.
            status: Status do agendamento ("Sucesso" ou "Erro").
            pickup_time: Data e hora do agendamento formatada (opcional).
            
        Returns:
            Resposta da API Evolution.
            
        Raises:
            requests.exceptions.RequestException: Em caso de erro na API.
        """
        # Valida se o telefone não está vazio
        if not phone or phone.strip() == '':
            logger.warning(f"Empty phone number for {name}, skipping WhatsApp")
            return {'success': False, 'error': 'Empty phone number'}
        
        # Normaliza telefone
        normalized_phone = self.normalize_phone(phone)
        
        # Valida se o número existe no WhatsApp
        if not self._validate_phone_exists(normalized_phone):
            logger.warning(f"Phone {phone} ({normalized_phone}) not found on WhatsApp, skipping")
            return {'success': False, 'error': 'Phone not found on WhatsApp'}
        
        # Gera mensagem baseada no status
        if status.lower() in ['sucesso', 'success', 'dispatched']:
            message = self.generate_success_message(name, destination, pickup_time)
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
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error sending WhatsApp to {name}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp to {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp: {e}")
            raise
    
    def is_connected(self) -> bool:
        """
        Verifica se a instância Evolution está conectada ao WhatsApp.

        Consulta o endpoint /instance/connectionState e verifica se o
        estado retornado é 'open'.

        Returns:
            True se conectada, False caso contrário ou em caso de erro.
        """
        endpoint = f"{self.api_url}/instance/connectionState/{self.instance_name}"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                state = (
                    data.get('instance', {}).get('state')
                    or data.get('state')
                    or ''
                )
                connected = state.lower() == 'open'
                if not connected:
                    logger.warning(
                        f"Instance '{self.instance_name}' state: '{state}' (not connected)"
                    )
                return connected
        except Exception as e:
            logger.warning(f"Could not check connection state for '{self.instance_name}': {e}")
        return False

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


class WhatsAppNotifierWithFallback:
    """
    Wrapper que gerencia instância principal e de backup do WhatsApp.

    Verifica automaticamente a conexão da instância principal antes de
    enviar. Se ela estiver desconectada, ou se o envio falhar, utiliza
    a instância de backup sem nenhuma intervenção manual.

    O estado de conexão é verificado no máximo uma vez a cada
    ``connection_check_interval`` segundos para evitar sobrecarga na API.
    """

    def __init__(
        self,
        primary: WhatsAppNotifier,
        backup: WhatsAppNotifier,
        connection_check_interval: int = 60
    ):
        """
        Args:
            primary: Notificador principal.
            backup: Notificador de backup (ativado automaticamente se o
                    principal cair).
            connection_check_interval: Segundos entre re-verificações de
                    conexão (padrão 60 s).
        """
        self.primary = primary
        self.backup = backup
        self.connection_check_interval = connection_check_interval

        # Cache do último estado verificado de cada instância
        self._last_check: Dict[str, float] = {}
        self._last_state: Dict[str, bool] = {}

        logger.info(
            f"WhatsAppNotifierWithFallback: primary='{primary.instance_name}', "
            f"backup='{backup.instance_name}'"
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _is_connected_cached(self, notifier: WhatsAppNotifier) -> bool:
        """Retorna o estado de conexão usando cache com TTL."""
        now = time.monotonic()
        key = notifier.instance_name
        elapsed = now - self._last_check.get(key, 0)

        if elapsed >= self.connection_check_interval:
            state = notifier.is_connected()
            self._last_check[key] = now
            self._last_state[key] = state
            return state

        return self._last_state.get(key, True)  # assume ok se nunca checou

    def _get_active_notifier(self) -> WhatsAppNotifier:
        """Retorna a instância ativa (principal ou backup)."""
        if self._is_connected_cached(self.primary):
            return self.primary

        logger.warning(
            f"[Fallback] Instância principal '{self.primary.instance_name}' desconectada. "
            f"Usando backup '{self.backup.instance_name}'."
        )
        return self.backup

    def _try_with_fallback(self, method_name: str, *args, **kwargs) -> Dict:
        """
        Chama ``method_name`` na instância ativa; se falhar, tenta no backup.
        """
        active = self._get_active_notifier()
        try:
            return getattr(active, method_name)(*args, **kwargs)
        except Exception as primary_exc:
            if active is self.primary:
                logger.warning(
                    f"[Fallback] Falha na instância principal '{self.primary.instance_name}': "
                    f"{primary_exc}. Tentando backup '{self.backup.instance_name}'."
                )
                # Invalida cache para forçar nova verificação depois
                self._last_check[self.primary.instance_name] = 0
                try:
                    return getattr(self.backup, method_name)(*args, **kwargs)
                except Exception as backup_exc:
                    logger.error(
                        f"[Fallback] Falha também no backup '{self.backup.instance_name}': "
                        f"{backup_exc}."
                    )
                    return {'success': False, 'error': str(backup_exc)}
            raise  # já estava no backup, propaga

    # ------------------------------------------------------------------
    # Interface pública (mesma assinatura do WhatsAppNotifier)
    # ------------------------------------------------------------------

    def send_message(
        self,
        name: str,
        phone: str,
        destination: str,
        status: str,
        pickup_time: str = None
    ) -> Dict:
        """Envia mensagem com fallback automático para a instância de backup."""
        return self._try_with_fallback(
            'send_message', name, phone, destination, status, pickup_time
        )

    def send_manual_review_alert(self, phone: str, name: str, reason: str) -> Dict:
        """Envia alerta de revisão manual com fallback automático."""
        return self._try_with_fallback(
            'send_manual_review_alert', phone, name, reason
        )

