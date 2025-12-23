"""
MinasTaxi API Client with retry logic and error handling.
"""
import logging
import requests
from typing import Optional, Dict
from retry import retry
from datetime import datetime

logger = logging.getLogger(__name__)


class MinasTaxiAPIError(Exception):
    """Exceção customizada para erros da API MinasTaxi."""
    pass


class MinasTaxiClient:
    """
    Cliente para integração com a API MinasTaxi.
    Implementa retry logic, tratamento de erros e validação de payload.
    """
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Inicializa o cliente da API MinasTaxi.
        
        Args:
            api_url: URL base da API (ex: https://api.minastaxi.com.br).
            api_key: Chave de autenticação da API.
            timeout: Timeout para requisições em segundos.
            max_retries: Número máximo de tentativas de retry.
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Headers padrão para todas as requisições
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'TaxiAutomationSystem/1.0'
        }
        
        logger.info(f"MinasTaxi client initialized for {api_url}")
    
    @retry(
        exceptions=requests.exceptions.RequestException,
        tries=3,
        delay=2,
        backoff=2,
        logger=logger
    )
    def dispatch_order(
        self,
        passenger_name: str,
        phone: str,
        pickup_address: str,
        pickup_lat: float,
        pickup_lng: float,
        pickup_time: datetime,
        dropoff_address: Optional[str] = None,
        dropoff_lat: Optional[float] = None,
        dropoff_lng: Optional[float] = None,
        **kwargs
    ) -> Dict:
        """
        Envia um pedido de táxi para a API MinasTaxi.
        
        Args:
            passenger_name: Nome do passageiro.
            phone: Telefone do passageiro.
            pickup_address: Endereço de coleta.
            pickup_lat: Latitude da coleta.
            pickup_lng: Longitude da coleta.
            pickup_time: Data/hora da coleta.
            dropoff_address: Endereço de destino (opcional).
            dropoff_lat: Latitude do destino (opcional).
            dropoff_lng: Longitude do destino (opcional).
            **kwargs: Parâmetros adicionais.
            
        Returns:
            Resposta da API com dados do pedido criado.
            
        Raises:
            MinasTaxiAPIError: Em caso de erro na API.
        """
        # Monta o payload
        payload = {
            'passenger': {
                'name': passenger_name,
                'phone': phone
            },
            'pickup': {
                'address': pickup_address,
                'coordinates': {
                    'latitude': pickup_lat,
                    'longitude': pickup_lng
                },
                'scheduled_time': pickup_time.isoformat()
            }
        }
        
        # Adiciona destino se fornecido
        if dropoff_address:
            payload['dropoff'] = {
                'address': dropoff_address
            }
            if dropoff_lat and dropoff_lng:
                payload['dropoff']['coordinates'] = {
                    'latitude': dropoff_lat,
                    'longitude': dropoff_lng
                }
        
        # Adiciona campos extras se fornecidos
        if kwargs:
            payload['metadata'] = kwargs
        
        # Valida payload
        self._validate_payload(payload)
        
        # URL do endpoint
        endpoint = f"{self.api_url}/dispatch"
        
        try:
            logger.info(f"Dispatching order for {passenger_name} to MinasTaxi API")
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Log da requisição
            logger.debug(f"Request to {endpoint}: {payload}")
            logger.debug(f"Response status: {response.status_code}")
            
            # Trata diferentes códigos de resposta
            if response.status_code == 201:
                # Sucesso - pedido criado
                data = response.json()
                order_id = data.get('order_id', 'UNKNOWN')
                logger.info(f"Order successfully dispatched. MinasTaxi Order ID: {order_id}")
                return data
                
            elif response.status_code == 200:
                # Sucesso alternativo
                data = response.json()
                logger.info("Order dispatched successfully")
                return data
                
            elif response.status_code == 400:
                # Bad Request - erro no payload
                error_msg = response.json().get('error', 'Bad request')
                logger.error(f"Bad request to MinasTaxi API: {error_msg}")
                raise MinasTaxiAPIError(f"Bad request: {error_msg}")
                
            elif response.status_code == 401:
                # Não autorizado - problema com API key
                logger.error("Unauthorized: Invalid API key")
                raise MinasTaxiAPIError("Unauthorized: Invalid API key")
                
            elif response.status_code == 429:
                # Rate limit excedido
                logger.warning("Rate limit exceeded, will retry...")
                raise requests.exceptions.RequestException("Rate limit exceeded")
                
            elif response.status_code >= 500:
                # Erro no servidor - tenta retry
                logger.warning(f"Server error ({response.status_code}), will retry...")
                raise requests.exceptions.RequestException(f"Server error: {response.status_code}")
                
            else:
                # Outro erro
                logger.error(f"Unexpected response code: {response.status_code}")
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
    
    def _validate_payload(self, payload: Dict):
        """
        Valida o payload antes de enviar para a API.
        
        Args:
            payload: Dicionário com dados do pedido.
            
        Raises:
            ValueError: Se o payload for inválido.
        """
        # Validações básicas
        if 'passenger' not in payload:
            raise ValueError("Missing 'passenger' in payload")
        
        if 'pickup' not in payload:
            raise ValueError("Missing 'pickup' in payload")
        
        passenger = payload['passenger']
        if not passenger.get('name') or not passenger.get('phone'):
            raise ValueError("Passenger must have 'name' and 'phone'")
        
        pickup = payload['pickup']
        if not pickup.get('address'):
            raise ValueError("Pickup must have 'address'")
        
        if 'coordinates' not in pickup:
            raise ValueError("Pickup must have 'coordinates'")
        
        coords = pickup['coordinates']
        if 'latitude' not in coords or 'longitude' not in coords:
            raise ValueError("Pickup coordinates must have 'latitude' and 'longitude'")
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Consulta o status de um pedido na API MinasTaxi.
        
        Args:
            order_id: ID do pedido retornado pela API.
            
        Returns:
            Dados do status do pedido.
        """
        endpoint = f"{self.api_url}/orders/{order_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get order status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API MinasTaxi.
        
        Returns:
            True se a conexão for bem-sucedida.
        """
        endpoint = f"{self.api_url}/health"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info("MinasTaxi API connection test successful")
                return True
            else:
                logger.warning(f"API health check returned: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
