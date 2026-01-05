"""
MinasTaxi API Client - Original Software Integration
Documentação completa em: docs/API_MINASTAXI.md
"""
import re
import logging
import requests
import uuid
import urllib3
import ssl
from typing import Optional, Dict
from retry import retry
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from ..models.order import Order

logger = logging.getLogger(__name__)


class MinasTaxiAPIError(Exception):
    """Exceção customizada para erros da API MinasTaxi."""
    pass


class LegacyHTTPAdapter(HTTPAdapter):
    """
    Adapter HTTP ultra-compatível para APIs com SSL/TLS legacy.
    """
    def init_poolmanager(self, *args, **kwargs):
        import urllib3.util.ssl_
        
        # Cria contexto SSL ultra-permissivo
        try:
            # Método 1: Contexto default com configurações mínimas
            ctx = ssl.create_default_context()
            ctx.check_hostname = False  
            ctx.verify_mode = ssl.CERT_NONE
            
            # Remove restrições de segurança
            ctx.options = 0
            
            # Força protocolos legados
            try:
                ctx.minimum_version = ssl.TLSVersion.SSLv3
            except:
                pass
            
            try:
                ctx.maximum_version = ssl.TLSVersion.TLSv1_2  
            except:
                pass
            
            # Ciphers ultra-permissivos
            try:
                ctx.set_ciphers('ALL:@SECLEVEL=0')
            except:
                try:
                    ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
                except:
                    ctx.set_ciphers('ALL')
            
            kwargs['ssl_context'] = ctx
            
        except Exception as e:
            logger.warning(f"Fallback para poolmanager padrão: {e}")
            
        return super().init_poolmanager(*args, **kwargs)


class MinasTaxiClient:
    """
    Cliente para integração com a API MinasTaxi (Original Software).
    Implementa retry logic, tratamento de erros e formato correto de payload.
    """
    
    def __init__(
        self,
        api_url: str,
        user_id: str,
        password: str,
        auth_header: str = None,
        payment_type: str = "ONLINE_PAYMENT",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Inicializa o cliente da API MinasTaxi.
        
        Args:
            api_url: URL base da API (ex: https://vm2c.taxifone.com.br:11048).
            user_id: ID do contrato/empresa (ex: "02572696000156").
            password: Senha de acesso (ex: "0104").
            auth_header: Header de autenticação completo (ex: "Basic Original.#2024").
            payment_type: Tipo de pagamento (ex: "ONLINE_PAYMENT", "BE", "BOLETO", "VOUCHER").
            timeout: Timeout para requisições em segundos.
            max_retries: Número máximo de tentativas de retry.
        """
        self.api_url = api_url.rstrip('/')
        self.user_id = user_id
        self.password = password
        self.payment_type = payment_type
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Headers padrão (Basic Auth)
        self.headers = {
            'authorization': auth_header or 'Basic Original',
            'Content-Type': 'application/json',
            'User-Agent': 'TaxiAutomationSystem/1.0'
        }
        
        # Cria sessão HTTP com adapter customizado para SSL legado
        self.session = requests.Session()
        self.session.mount('https://', LegacyHTTPAdapter())
        
        # Desabilita warnings de SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        logger.info(f"MinasTaxi client initialized for {api_url} (User: {user_id})")
        logger.warning("Using legacy SSL/TLS adapter for compatibility with old APIs")
    
    def _datetime_to_unix(self, dt: datetime) -> str:
        """
        Converte datetime para UNIX Time (segundos desde epoch).
        
        Args:
            dt: Objeto datetime.
            
        Returns:
            String com timestamp UNIX.
        """
        if isinstance(dt, str):
            # Se já é string ISO, tenta converter para datetime
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except:
                # Se falhar, assume que já é UNIX time
                return dt
        
        return str(int(dt.timestamp()))
    
    def _generate_request_id(self) -> str:
        """
        Gera ID único para a requisição.
        
        Returns:
            ID único no formato timestamp + UUID curto.
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        short_uuid = str(uuid.uuid4())[:8].upper()
        return f"{timestamp}{short_uuid}"
    
    def _extract_cost_center(self, notes: str) -> Optional[str]:
        """
        Extrai o centro de custo das observações.
        
        Args:
            notes: Campo de observações com possível CC.
            
        Returns:
            Código do centro de custo ou None.
            
        Examples:
            "CC: 20086" -> "20086"
            "CENTRO DE CUSTO 1.07002.07.001" -> "1.07002.07.001"
        """
        if not notes:
            return None
        
        # Padrão: CC: 12345 ou CC:12345
        match = re.search(r'CC\s*:\s*(\d+)', notes, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Padrão: CENTRO DE CUSTO 1.07002.07.001
        match = re.search(r'CENTRO DE CUSTO\s*([\d.]+)', notes, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Padrão: sequência numérica com pontos (ex: 1.07002.07.001)
        match = re.search(r'\b(\d+\.\d+\.\d+\.\d+)\b', notes)
        if match:
            return match.group(1)
        
        return None
    
    def _detect_company(self, destination: str) -> Optional[str]:
        """
        Detecta o código da empresa com base no destino.
        
        Args:
            destination: Endereço de destino.
            
        Returns:
            Código da empresa ou None.
        """
        if not destination:
            return None
        
        destination_upper = destination.upper()
        
        # DELP - Delegacia Especializada
        if "DELP" in destination_upper or "DELEGACIA" in destination_upper:
            return "DELP"
        
        # Outros padrões podem ser adicionados aqui
        # Por exemplo: CSN, TECNOKOR, etc.
        
        return None
    
    def _remove_country_code(self, phone: str) -> str:
        """
        Remove DDI (55) do telefone brasileiro para envio ao MinasTaxi.
        
        MinasTaxi espera apenas DDD + número (ex: 31999999926).
        WhatsApp precisa do formato completo com DDI (ex: 5531999999926).
        
        Args:
            phone: Telefone com ou sem DDI.
            
        Returns:
            Telefone sem DDI (apenas DDD + número).
            
        Examples:
            "5531999999926" -> "31999999926"
            "31999999926" -> "31999999926"
            "+5531999999926" -> "31999999926"
        """
        if not phone:
            return ""
        
        # Remove todos os caracteres não numéricos
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Se começa com 55 e tem 12-13 dígitos, remove o 55
        if digits_only.startswith('55') and len(digits_only) in [12, 13]:
            return digits_only[2:]  # Remove os 2 primeiros dígitos (55)
        
        return digits_only
    
    @retry(
        exceptions=requests.exceptions.RequestException,
        tries=3,
        delay=2,
        backoff=2,
        logger=logger
    )
    def dispatch_order(self, order: Order) -> Dict:
        """
        Envia um pedido de táxi para a API MinasTaxi usando rideCreate.
        
        Args:
            order: Objeto Order com todos os dados do pedido.
            
        Returns:
            Resposta da API com ride_id e status.
            
        Raises:
            MinasTaxiAPIError: Em caso de erro na API.
        """
        # Gera request_id único
        request_id = self._generate_request_id()
        
        # Converte pickup_time para UNIX timestamp
        unix_time = self._datetime_to_unix(order.pickup_time)
        
        # Determina quantidade de passageiros
        passengers_count = len(order.passengers) if order.passengers else 1
        
        # Monta array de users
        users = []
        if order.passengers:
            # Múltiplos passageiros - usa coordenadas individuais se disponíveis
            for idx, passenger in enumerate(order.passengers, 1):
                # Usa coordenadas específicas do passageiro se disponível, senão usa do order
                passenger_lat = passenger.get('lat', order.pickup_lat)
                passenger_lng = passenger.get('lng', order.pickup_lng)
                
                # Obtém telefone do passageiro, senão usa telefone principal do order
                passenger_phone = passenger.get('phone', '') or order.phone or ""
                passenger_phone_clean = self._remove_country_code(passenger_phone) if passenger_phone else ""
                
                # Validação: MinasTaxi requer telefone não vazio
                if not passenger_phone_clean:
                    logger.warning(f"Passenger {passenger.get('name')} has no phone, using order phone as fallback")
                    passenger_phone_clean = self._remove_country_code(order.phone) if order.phone else ""
                
                users.append({
                    "id": idx,
                    "sequence": idx,
                    "name": passenger.get('name', order.passenger_name),
                    "phone": passenger_phone_clean,
                    "pickup": {
                        "address": passenger.get('address', order.pickup_address),
                        "city": self._extract_city(passenger.get('address', order.pickup_address)),
                        "state": self._extract_state(passenger.get('address', order.pickup_address)),
                        "postal_code": "",
                        "lat": str(passenger_lat),  # Coordenada específica do passageiro
                        "lng": str(passenger_lng)   # Coordenada específica do passageiro
                    }
                })
        else:
            # Passageiro único (formato antigo)
            users.append({
                "id": 1,
                "sequence": 1,
                "name": order.passenger_name,
                "phone": self._remove_country_code(order.phone),
                "pickup": {
                    "address": order.pickup_address,
                    "city": self._extract_city(order.pickup_address),
                    "state": self._extract_state(order.pickup_address),
                    "postal_code": "",
                    "lat": str(order.pickup_lat),
                    "lng": str(order.pickup_lng)
                }
            })
        
        # Determina telefone principal (fallback para primeiro passageiro se necessário)
        main_phone = order.phone or ""
        if not main_phone and users:
            main_phone = users[0].get('phone', "")
        
        # Centro de custo: usa o extraído diretamente pelo LLM ou tenta extrair das notes
        cost_center = order.cost_center if order.cost_center else self._extract_cost_center(order.notes or "")
        
        # Determina código da empresa: prioriza company_code extraído do email
        company_code = order.company_code if order.company_code else None
        
        # Se não foi extraído do email, tenta detectar pelo destino
        if not company_code:
            company_code = self._detect_company(order.dropoff_address or "")
        
        # CNPJ da empresa: usa o do order (já convertido) ou o padrão do cliente
        # O CNPJ é passado no campo 'user' da API MinasTaxi
        company_cnpj = order.company_cnpj if order.company_cnpj else self.user_id
        logger.info(f"Using CNPJ in 'user' field: {company_cnpj}")
        
        # Monta observação com centro de custo
        passenger_note = ""
        if cost_center:
            passenger_note = f"C.Custo: {cost_center}"
        if order.notes:
            if passenger_note:
                passenger_note += f" | {order.notes}"
            else:
                passenger_note = order.notes
        if not passenger_note and order.raw_email_body:
            passenger_note = order.raw_email_body
        
        # Monta payload no formato Original Software
        payload = {
            "partner": "1",  # Fixo como "1" conforme padrão
            "user": company_cnpj,  # CNPJ da empresa (identifica qual empresa está fazendo o pedido)
            "password": self.password,
            "request_id": request_id,
            "pickup_time": unix_time,
            "category": "taxi",  # Pode ser parametrizado depois
            "passengers_no": passengers_count,
            "suitcases_no": 0,
            "passenger_note": passenger_note,
            "passenger_name": order.passenger_name,
            "passenger_phone_number": self._remove_country_code(main_phone) if main_phone else "",
            "payment_type": self.payment_type,  # Configurável via .env
            "users": users
        }
        
        logger.info(f"💳 Tipo de pagamento: {self.payment_type}")
        
        # Adiciona código de empresa (extra1) para referência
        # NOTA: centro de custo será adicionado quando a API suportar
        if company_code:
            payload["extra1"] = company_code
            logger.info(f"✅ Código da empresa (extra1): {company_code}")
        else:
            logger.warning("⚠️ Código da empresa não encontrado")
        
        # Centro de custo: aguardando implementação de campo específico na API
        # Por enquanto, incluído apenas no passenger_note
        if cost_center:
            logger.info(f"✅ Centro de custo (incluído em passenger_note): {cost_center}")
        else:
            logger.warning("⚠️ Centro de custo não encontrado")
        
        # Adiciona destino se fornecido
        if order.dropoff_address and order.dropoff_lat and order.dropoff_lng:
            payload["destinations"] = [
                {
                    "passengerId": 1,
                    "sequence": 2,
                    "location": {
                        "address": order.dropoff_address,
                        "city": self._extract_city(order.dropoff_address),
                        "state": self._extract_state(order.dropoff_address),
                        "postal_code": "",
                        "lat": str(order.dropoff_lat),
                        "lng": str(order.dropoff_lng)
                    }
                }
            ]
        
        # Valida payload
        self._validate_payload(payload)
        
        # URL do endpoint
        endpoint = f"{self.api_url}/rideCreate"
        
        try:
            logger.info(f"Dispatching order for {order.passenger_name} to MinasTaxi API")
            logger.debug(f"Request ID: {request_id}")
            
            # Usa a sessão com adapter SSL customizado
            response = self.session.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
                verify=False  # Desabilita verificação SSL
            )
            
            # Log da requisição
            logger.debug(f"Request to {endpoint}")
            logger.debug(f"Response status: {response.status_code}")
            
            # Trata resposta
            if response.status_code == 200:
                data = response.json()

                if data.get('accepted_and_looking_for_driver'):
                    ride_id = data.get('ride_id')
                    logger.info(f"Order dispatched successfully. Ride ID: {ride_id}")

                    return {
                        'success': True,
                        'order_id': ride_id,
                        'request_id': request_id,
                        'status': 'dispatched',
                        'message': 'Pedido aceito, procurando motorista',
                        'ride_id': ride_id
                    }
                else:
                    logger.error("Order was not accepted by MinasTaxi")
                    # Log completo para investigação
                    try:
                        logger.debug(f"Response headers: {response.headers}")
                        logger.debug(f"Response body: {response.text}")
                    except Exception:
                        pass
                    raise MinasTaxiAPIError("Order not accepted")

            elif response.status_code == 500:
                # Internal error
                try:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get('error', 'Internal server error')
                except Exception:
                    error_msg = response.text or 'Internal server error'

                logger.error(f"MinasTaxi API error: {error_msg}")
                logger.debug(f"Response headers: {response.headers}")
                logger.debug(f"Response body: {response.text}")
                raise MinasTaxiAPIError(f"API error: {error_msg}")

            else:
                # Log detalhado para debug de códigos como 403
                logger.error(f"Unexpected response code: {response.status_code}")
                try:
                    logger.error(f"Response headers: {response.headers}")
                    logger.error(f"Response body: {response.text}")
                except Exception:
                    pass
                raise MinasTaxiAPIError(f"Unexpected response: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            raise MinasTaxiAPIError("Request timeout")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise MinasTaxiAPIError(f"Connection error: {e}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            raise
    
    def _extract_city(self, address: str) -> str:
        """
        Extrai cidade do endereço.
        Assume padrão brasileiro: "Rua X, Bairro, Cidade, Estado"
        
        Args:
            address: Endereço completo.
            
        Returns:
            Nome da cidade ou "Belo Horizonte" como padrão.
        """
        if not address:
            return "Belo Horizonte"
        
        # Tenta extrair cidade (penúltimo item antes do estado)
        parts = [p.strip() for p in address.split(',')]
        
        if len(parts) >= 2:
            # Verifica se o último é um estado (2 letras)
            if len(parts[-1]) == 2:
                return parts[-2] if len(parts) >= 2 else "Belo Horizonte"
        
        return "Belo Horizonte"
    
    def _extract_state(self, address: str) -> str:
        """
        Extrai estado do endereço.
        
        Args:
            address: Endereço completo.
            
        Returns:
            Sigla do estado ou "MG" como padrão.
        """
        if not address:
            return "MG"
        
        # Busca por padrão de estado (2 letras maiúsculas no final)
        parts = [p.strip() for p in address.split(',')]
        
        if parts:
            last_part = parts[-1].strip()
            if len(last_part) == 2 and last_part.isupper():
                return last_part
        
        return "MG"
    
    def _validate_payload(self, payload: Dict):
        """
        Valida o payload antes de enviar para a API.
        
        Args:
            payload: Dicionário com dados do pedido.
            
        Raises:
            ValueError: Se o payload for inválido.
        """
        required_fields = [
            'partner', 'user', 'password', 'request_id', 
            'pickup_time', 'category', 'passenger_name', 
            'users'  # Removido passenger_phone_number pois pode ser vazio (múltiplos passageiros)
        ]
        
        for field in required_fields:
            if field not in payload or not payload[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Valida passenger_phone_number - pode ser vazio mas deve existir
        if 'passenger_phone_number' not in payload:
            raise ValueError("Missing required field: passenger_phone_number (can be empty)")
        
        # Valida users array
        if not isinstance(payload['users'], list) or len(payload['users']) == 0:
            raise ValueError("users array must contain at least one passenger")
        
        # Valida primeiro user
        first_user = payload['users'][0]
        if not first_user.get('pickup'):
            raise ValueError("First user must have pickup location")
    
    def get_ride_details(self, ride_id: str) -> Dict:
        """
        Consulta detalhes e status de uma corrida (rideDetails).
        
        Args:
            ride_id: ID da corrida retornado por rideCreate.
            
        Returns:
            Dados completos da corrida incluindo status, motorista, preço, etc.
        """
        request_id = self._generate_request_id()
        
        payload = {
            "partner": "1",
            "user": self.user_id,
            "password": self.password,
            "request_id": request_id,
            "ride_id": ride_id
        }
        
        endpoint = f"{self.api_url}/rideDetails"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get ride details: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting ride details: {e}")
            return {}
    
    def cancel_ride(self, ride_id: str, reason: str = "Cliente solicitou cancelamento") -> bool:
        """
        Cancela uma corrida (rideCancel).
        
        Args:
            ride_id: ID da corrida a cancelar.
            reason: Motivo do cancelamento.
            
        Returns:
            True se cancelamento foi aceito.
        """
        request_id = self._generate_request_id()
        
        payload = {
            "partner": "1",
            "user": self.user_id,
            "password": self.password,
            "request_id": request_id,
            "ride_id": ride_id,
            "cancel_reason": reason
        }
        
        endpoint = f"{self.api_url}/rideCancel"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('cancel_accepted', False)
            else:
                logger.error(f"Failed to cancel ride: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error canceling ride: {e}")
            return False
    
    def send_driver_message(self, ride_id: str, message: str) -> bool:
        """
        Envia mensagem para o motorista (driverMessage).
        
        Args:
            ride_id: ID da corrida.
            message: Mensagem a enviar.
            
        Returns:
            True se mensagem foi enviada.
        """
        request_id = self._generate_request_id()
        
        payload = {
            "partner": "1",
            "user": self.user_id,
            "password": self.password,
            "request_id": request_id,
            "ride_id": ride_id,
            "msg": message
        }
        
        endpoint = f"{self.api_url}/driverMessage"
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            else:
                logger.error(f"Failed to send message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API MinasTaxi.
        
        Returns:
            True se a conexão for bem-sucedida.
        """
        try:
            logger.info("Testando conexão com API MinasTaxi...")
            
            # Usa a sessão já configurada com adapter SSL
            response = self.session.get(
                self.api_url,
                headers=self.headers,
                timeout=10,
                verify=False
            )
            
            logger.info(f"✅ API respondeu com status: {response.status_code}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Falha na conexão: {e}")
            return False
