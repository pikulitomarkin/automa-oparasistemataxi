"""
Main processor orchestrating the entire taxi automation pipeline.
"""
import logging
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from .services.email_reader import EmailReader, EmailMessage
from .services.llm_extractor import LLMExtractor
from .services.geocoding_service import GeocodingService
from .services.minastaxi_client import MinasTaxiClient, MinasTaxiAPIError
from .services.whatsapp_notifier import WhatsAppNotifier
from .services.database import DatabaseManager
from .models import Order, OrderStatus

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'data/taxi_automation.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TaxiOrderProcessor:
    """
    Processador principal que orquestra todo o fluxo de automação.
    
    Pipeline:
    1. Lê e-mails novos
    2. Extrai dados com LLM
    3. Geocodifica endereços
    4. Envia para MinasTaxi API
    5. Atualiza banco de dados
    """
    
    def __init__(self):
        """Inicializa todos os serviços necessários."""
        logger.info("Initializing Taxi Order Processor...")
        
        # Database
        self.db = DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))
        
        # Email Reader
        self.email_reader = EmailReader(
            host=os.getenv('EMAIL_HOST', 'imap.gmail.com'),
            port=int(os.getenv('EMAIL_PORT', 993)),
            user=os.getenv('EMAIL_USER'),
            password=os.getenv('EMAIL_PASSWORD'),
            folder=os.getenv('EMAIL_FOLDER', 'INBOX'),
            subject_filter=os.getenv('EMAIL_SUBJECT_FILTER', 'Novo Agendamento')
        )
        
        # LLM Extractor
        self.llm_extractor = LLMExtractor(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        )
        
        # Geocoding Service
        use_google = os.getenv('USE_GOOGLE_MAPS', 'false').lower() == 'true'
        self.geocoder = GeocodingService(
            use_google=use_google,
            google_api_key=os.getenv('GOOGLE_MAPS_API_KEY')
        )
        
        # MinasTaxi Client
        self.minastaxi_client = MinasTaxiClient(
            api_url=os.getenv('MINASTAXI_API_URL', 'https://vm2c.taxifone.com.br:11048'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER', 'Basic Original'),
            timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30)),
            max_retries=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', 3))
        )
        
        # WhatsApp Notifier (opcional)
        self.whatsapp_enabled = os.getenv('ENABLE_WHATSAPP_NOTIFICATIONS', 'false').lower() == 'true'
        if self.whatsapp_enabled:
            self.whatsapp_notifier = WhatsAppNotifier(
                api_url=os.getenv('EVOLUTION_API_URL', ''),
                api_key=os.getenv('EVOLUTION_API_KEY', ''),
                instance_name=os.getenv('EVOLUTION_INSTANCE_NAME', 'taxi-bot'),
                timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30))
            )
            logger.info("WhatsApp notifications enabled")
        else:
            self.whatsapp_notifier = None
            logger.info("WhatsApp notifications disabled")
        
        logger.info("All services initialized successfully")
    
    def process_new_orders(self, days_back: int = 7) -> dict:
        """
        Processa todos os novos pedidos de e-mail.
        
        Args:
            days_back: Número de dias para trás na busca de e-mails.
            
        Returns:
            Dicionário com estatísticas do processamento.
        """
        stats = {
            'emails_fetched': 0,
            'orders_created': 0,
            'orders_dispatched': 0,
            'orders_failed': 0
        }
        
        try:
            # 1. Busca novos e-mails
            logger.info(f"Fetching new order emails (last {days_back} days)...")
            emails = self.email_reader.fetch_new_orders(days_back=days_back)
            stats['emails_fetched'] = len(emails)
            
            if not emails:
                logger.info("No new order emails found")
                return stats
            
            logger.info(f"Found {len(emails)} new order emails")
            
            # 2. Processa cada e-mail
            for email in emails:
                try:
                    order = self._process_single_email(email)
                    
                    if order:
                        stats['orders_created'] += 1
                        
                        if order.status == OrderStatus.DISPATCHED:
                            stats['orders_dispatched'] += 1
                        elif order.status == OrderStatus.FAILED or order.status == OrderStatus.MANUAL_REVIEW:
                            stats['orders_failed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing email {email.uid}: {e}")
                    stats['orders_failed'] += 1
            
            # Log final
            logger.info(
                f"Processing complete: {stats['orders_created']} orders created, "
                f"{stats['orders_dispatched']} dispatched, {stats['orders_failed']} failed"
            )
            
        except Exception as e:
            logger.error(f"Error in process_new_orders: {e}")
        
        return stats
    
    def _process_single_email(self, email: EmailMessage) -> Order:
        """
        Processa um único e-mail através de todo o pipeline.
        
        Args:
            email: EmailMessage a ser processado.
            
        Returns:
            Order object com status atualizado.
        """
        logger.info(f"Processing email UID={email.uid} from {email.from_}")
        
        # Verifica se já foi processado
        existing_order = self.db.get_order_by_email_id(email.uid)
        if existing_order:
            logger.info(f"Email {email.uid} already processed, skipping")
            return existing_order
        
        # Cria novo pedido
        order = Order(
            email_id=email.uid,
            raw_email_body=email.body,
            status=OrderStatus.RECEIVED
        )
        
        try:
            # FASE 2: Extração com LLM
            logger.info("Extracting data with LLM...")
            extracted_data = self.llm_extractor.extract_with_fallback(email.body)
            
            if not extracted_data:
                order.status = OrderStatus.MANUAL_REVIEW
                order.error_message = "Failed to extract data from email"
                order.id = self.db.create_order(order)
                logger.warning(f"Order {order.id} requires manual review - extraction failed")
                return order
            
            # Atualiza order com dados extraídos
            order.passenger_name = extracted_data.get('passenger_name')
            order.phone = extracted_data.get('phone')
            order.pickup_address = extracted_data.get('pickup_address')
            order.dropoff_address = extracted_data.get('dropoff_address')
            
            # Parse pickup_time
            if extracted_data.get('pickup_time'):
                try:
                    from dateutil import parser
                    order.pickup_time = parser.parse(extracted_data['pickup_time'])
                except:
                    logger.warning("Failed to parse pickup_time")
            
            order.status = OrderStatus.EXTRACTED
            
            # FASE 2.5: Geocoding
            logger.info("Geocoding pickup address...")
            pickup_coords = self.geocoder.geocode_address(order.pickup_address)
            
            if not pickup_coords:
                order.status = OrderStatus.MANUAL_REVIEW
                order.error_message = "Failed to geocode pickup address"
                order.id = self.db.create_order(order)
                logger.warning(f"Order {order.id} requires manual review - geocoding failed")
                return order
            
            order.pickup_lat, order.pickup_lng = pickup_coords
            
            # Geocode dropoff se fornecido
            if order.dropoff_address:
                dropoff_coords = self.geocoder.geocode_address(order.dropoff_address)
                if dropoff_coords:
                    order.dropoff_lat, order.dropoff_lng = dropoff_coords
            
            order.status = OrderStatus.GEOCODED
            
            # Salva no banco antes de dispatch
            order.id = self.db.create_order(order)
            logger.info(f"Order {order.id} created in database")
            
            # FASE 3: Dispatch para MinasTaxi
            logger.info(f"Dispatching order {order.id} to MinasTaxi...")
            
            try:
                response = self.minastaxi_client.dispatch_order(order)
                
                # Sucesso
                order.status = OrderStatus.DISPATCHED
                order.minastaxi_order_id = response.get('order_id')
                self.db.update_order(order)
                
                logger.info(f"Order {order.id} successfully dispatched to MinasTaxi")
                
                # FASE 4: Notificação WhatsApp (se habilitada)
                if self.whatsapp_enabled and self.whatsapp_notifier and order.phone:
                    try:
                        whatsapp_response = self.whatsapp_notifier.send_message(
                            name=order.passenger_name or "Cliente",
                            phone=order.phone,
                            destination=order.dropoff_address or order.pickup_address or "destino",
                            status="Sucesso"
                        )
                        order.whatsapp_sent = True
                        order.whatsapp_message_id = whatsapp_response.get('message_id')
                        self.db.update_order(order)
                        logger.info(f"WhatsApp notification sent for order {order.id}")
                    except Exception as whatsapp_error:
                        logger.warning(f"Failed to send WhatsApp for order {order.id}: {whatsapp_error}")
                        # Não falha o pedido por erro no WhatsApp
                
            except MinasTaxiAPIError as e:
                order.status = OrderStatus.FAILED
                order.error_message = f"MinasTaxi API error: {str(e)}"
                self.db.update_order(order)
                logger.error(f"Failed to dispatch order {order.id}: {e}")
                
                # Notifica erro via WhatsApp (se habilitado)
                if self.whatsapp_enabled and self.whatsapp_notifier and order.phone:
                    try:
                        self.whatsapp_notifier.send_message(
                            name=order.passenger_name or "Cliente",
                            phone=order.phone,
                            destination=order.dropoff_address or order.pickup_address or "destino",
                            status="Erro"
                        )
                        logger.info(f"Error notification sent via WhatsApp for order {order.id}")
                    except Exception as whatsapp_error:
                        logger.warning(f"Failed to send error WhatsApp: {whatsapp_error}")
            
        except Exception as e:
            order.status = OrderStatus.FAILED
            order.error_message = f"Processing error: {str(e)}"
            
            if order.id:
                self.db.update_order(order)
            else:
                order.id = self.db.create_order(order)
            
            logger.error(f"Error processing order: {e}")
        
        return order
    
    def reprocess_failed_orders(self):
        """
        Tenta reprocessar pedidos que falharam.
        """
        logger.info("Reprocessing failed orders...")
        
        failed_orders = self.db.get_orders_by_status(OrderStatus.FAILED)
        
        for order in failed_orders:
            logger.info(f"Retrying order {order.id}...")
            
            try:
                # Tenta dispatch novamente se já tem coordenadas
                if order.pickup_lat and order.pickup_lng:
                    response = self.minastaxi_client.dispatch_order(order)
                    
                    order.status = OrderStatus.DISPATCHED
                    order.minastaxi_order_id = response.get('order_id')
                    order.error_message = None
                    self.db.update_order(order)
                    
                    logger.info(f"Order {order.id} successfully retried")
                    
            except Exception as e:
                logger.error(f"Retry failed for order {order.id}: {e}")
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do sistema.
        
        Returns:
            Dicionário com estatísticas.
        """
        return self.db.get_statistics()


def main():
    """Função principal para execução standalone."""
    logger.info("=" * 60)
    logger.info("Starting Taxi Order Processor")
    logger.info("=" * 60)
    
    processor = TaxiOrderProcessor()
    
    # Processa novos pedidos
    stats = processor.process_new_orders(days_back=7)
    
    logger.info(f"Processing Statistics: {stats}")
    
    # Estatísticas finais
    db_stats = processor.get_statistics()
    logger.info(f"Database Statistics: {db_stats}")


if __name__ == "__main__":
    main()
