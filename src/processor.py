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
from .services.route_optimizer import RouteOptimizer
from .models import Order, OrderStatus
from .config.company_mapping import get_cnpj_from_company_code

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
            payment_type=os.getenv('MINASTAXI_PAYMENT_TYPE', 'ONLINE_PAYMENT'),
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
                auth_header_name=os.getenv('EVOLUTION_AUTH_HEADER_NAME', 'apikey'),
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
        
        # Verifica se já foi processado (mesmo email UID)
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
            order.notes = extracted_data.get('notes')  # Observações gerais
            order.company_code = extracted_data.get('company_code')  # Código da empresa extraído do email
            order.cost_center = extracted_data.get('cost_center')  # Centro de custo extraído diretamente
            
            # Converte código da empresa para CNPJ
            if order.company_code:
                order.company_cnpj = get_cnpj_from_company_code(order.company_code)
                logger.info(f"Company code {order.company_code} mapped to CNPJ {order.company_cnpj}")
            else:
                logger.warning("No company code found in email - will use default CNPJ")
            
            # Múltiplos passageiros (novo)
            order.passengers = extracted_data.get('passengers', [])
            order.has_return = extracted_data.get('has_return', False)
            
            # Parse pickup_time
            if extracted_data.get('pickup_time'):
                try:
                    from dateutil import parser
                    order.pickup_time = parser.parse(extracted_data['pickup_time'])
                except:
                    logger.warning("Failed to parse pickup_time")
            
            # Verifica duplicata por conteúdo (mesmo passageiro/endereço/horário)
            if order.pickup_time:
                is_duplicate = self.db.check_duplicate_order(
                    passenger_name=order.passenger_name,
                    pickup_address=order.pickup_address,
                    pickup_time=order.pickup_time,
                    tolerance_minutes=30  # Considera duplicado se horário difere em menos de 30min
                )
                
                if is_duplicate:
                    logger.warning(
                        f"Duplicate order detected: {order.passenger_name} at "
                        f"{order.pickup_address} around {order.pickup_time.strftime('%Y-%m-%d %H:%M')}"
                    )
                    order.status = OrderStatus.MANUAL_REVIEW
                    order.error_message = "Possível pedido duplicado (mesmo passageiro, endereço e horário similar)"
                    order.id = self.db.create_order(order)
                    logger.info(f"Order {order.id} marked for manual review - possible duplicate")
                    return order
            
            # Parse return_time se houver
            if extracted_data.get('return_time'):
                try:
                    from dateutil import parser
                    order.return_time = parser.parse(extracted_data['return_time'])
                except:
                    logger.warning("Failed to parse return_time")
            
            order.status = OrderStatus.EXTRACTED
            
            # VERIFICA SE TEM RETORNO - CRIA 2 ORDERS (IDA + VOLTA)
            if order.has_return and order.return_time:
                logger.info("Order has return trip - will create 2 orders (outbound + return)")
                return self._process_round_trip(email, order, extracted_data)
            
            # Continua processamento normal (sem retorno)
            
            # FASE 2.5: Geocoding
            logger.info("Geocoding addresses...")
            
            # Geocode destino primeiro
            destination_coords = None
            if order.dropoff_address:
                dropoff_coords = self.geocoder.geocode_address(order.dropoff_address)
                if dropoff_coords:
                    order.dropoff_lat, order.dropoff_lng = dropoff_coords
                    destination_coords = dropoff_coords
                    logger.info(f"Destination geocoded: {order.dropoff_lat}, {order.dropoff_lng}")
            
            # Geocode endereços de múltiplos passageiros se houver
            if order.passengers:
                logger.info(f"Geocoding {len(order.passengers)} passenger addresses...")
                for idx, passenger in enumerate(order.passengers):
                    coords = self.geocoder.geocode_address(passenger.get('address', ''))
                    if coords:
                        passenger['lat'] = coords[0]
                        passenger['lng'] = coords[1]
                        logger.debug(f"Passenger {passenger.get('name')} geocoded: {coords}")
                
                # Otimizar rota de coleta
                logger.info("Optimizing pickup route...")
                optimized_passengers = RouteOptimizer.optimize_pickup_sequence(
                    order.passengers, destination_coords
                )
                order.passengers = optimized_passengers
                
                # Usar primeiro passageiro como referência
                if order.passengers and 'lat' in order.passengers[0]:
                    order.pickup_lat = order.passengers[0]['lat']
                    order.pickup_lng = order.passengers[0]['lng']
                    # Atualizar pickup_address para múltiplas paradas
                    addresses = [p['address'] for p in order.passengers[:2]]
                    order.pickup_address = f"Múltiplas paradas: {' → '.join(addresses)}" + ("..." if len(order.passengers) > 2 else "")
                    logger.info(f"Route optimized: {len(order.passengers)} stops")
                else:
                    # Fallback para geocoding do endereço original
                    pickup_coords = self.geocoder.geocode_address(order.pickup_address)
                    if not pickup_coords:
                        order.status = OrderStatus.MANUAL_REVIEW
                        order.error_message = "Failed to geocode pickup address"
                        order.id = self.db.create_order(order)
                        logger.warning(f"Order {order.id} requires manual review - geocoding failed")
                        return order
                    order.pickup_lat, order.pickup_lng = pickup_coords
            else:
                # Passageiro único - geocoding tradicional
                pickup_coords = self.geocoder.geocode_address(order.pickup_address)
                if not pickup_coords:
                    order.status = OrderStatus.MANUAL_REVIEW
                    order.error_message = "Failed to geocode pickup address"
                    order.id = self.db.create_order(order)
                    logger.warning(f"Order {order.id} requires manual review - geocoding failed")
                    return order
                order.pickup_lat, order.pickup_lng = pickup_coords
            
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
                if self.whatsapp_enabled and self.whatsapp_notifier:
                    # Lista de passageiros para notificar
                    passengers_to_notify = []
                    
                    # Se houver múltiplos passageiros, usa APENAS a lista individualizada
                    if order.passengers:
                        for passenger in order.passengers:
                            if passenger.get('phone'):
                                passengers_to_notify.append({
                                    'name': passenger.get('name', 'Cliente'),
                                    'phone': passenger['phone']
                                })
                    # Senão, usa o passageiro principal (passageiro único)
                    elif order.phone:
                        passengers_to_notify.append({
                            'name': order.passenger_name or "Cliente",
                            'phone': order.phone
                        })
                    
                    # Envia mensagem para cada passageiro
                    whatsapp_sent_count = 0
                    
                    # Formata data/hora do agendamento
                    pickup_time_formatted = None
                    if order.pickup_time:
                        try:
                            # Converte para timezone de Brasília
                            import pytz
                            from datetime import datetime
                            
                            if isinstance(order.pickup_time, str):
                                pickup_dt = datetime.fromisoformat(order.pickup_time.replace('Z', '+00:00'))
                            else:
                                pickup_dt = order.pickup_time
                            
                            # Garante timezone Brasil
                            br_tz = pytz.timezone('America/Sao_Paulo')
                            if pickup_dt.tzinfo is None:
                                pickup_dt = br_tz.localize(pickup_dt)
                            else:
                                pickup_dt = pickup_dt.astimezone(br_tz)
                            
                            # Formata: "Segunda-feira, 06/01/2026 às 14:00"
                            dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                                          'Sexta-feira', 'Sábado', 'Domingo']
                            dia_semana = dias_semana[pickup_dt.weekday()]
                            pickup_time_formatted = f"{dia_semana}, {pickup_dt.strftime('%d/%m/%Y às %H:%M')}"
                        except Exception as e:
                            logger.warning(f"Failed to format pickup_time: {e}")
                    
                    for passenger in passengers_to_notify:
                        try:
                            whatsapp_response = self.whatsapp_notifier.send_message(
                                name=passenger['name'],
                                phone=passenger['phone'],
                                destination=order.dropoff_address or order.pickup_address or "destino",
                                status="Sucesso",
                                pickup_time=pickup_time_formatted
                            )
                            whatsapp_sent_count += 1
                            
                            # Armazena o message_id do primeiro envio
                            if whatsapp_sent_count == 1:
                                order.whatsapp_message_id = whatsapp_response.get('message_id')
                            
                        except Exception as whatsapp_error:
                            logger.warning(f"Failed to send WhatsApp to {passenger['name']} ({passenger['phone']}): {whatsapp_error}")
                    
                    # Marca como enviado se pelo menos uma mensagem foi enviada
                    if whatsapp_sent_count > 0:
                        order.whatsapp_sent = True
                        self.db.update_order(order)
                        logger.info(f"✅ WhatsApp sent to {whatsapp_sent_count}/{len(passengers_to_notify)} passengers for order {order.id}")
                    else:
                        logger.warning(f"⚠️ No WhatsApp messages sent for order {order.id}")
                
            except MinasTaxiAPIError as e:
                order.status = OrderStatus.FAILED
                order.error_message = f"MinasTaxi API error: {str(e)}"
                self.db.update_order(order)
                logger.error(f"Failed to dispatch order {order.id}: {e}")
                
                # Notifica erro via WhatsApp (se habilitado)
                if self.whatsapp_enabled and self.whatsapp_notifier:
                    # Lista de passageiros para notificar
                    passengers_to_notify = []
                    
                    # Se houver múltiplos passageiros, usa APENAS a lista individualizada
                    if order.passengers:
                        for passenger in order.passengers:
                            if passenger.get('phone'):
                                passengers_to_notify.append({
                                    'name': passenger.get('name', 'Cliente'),
                                    'phone': passenger['phone']
                                })
                    # Senão, usa o passageiro principal (passageiro único)
                    elif order.phone:
                        passengers_to_notify.append({
                            'name': order.passenger_name or "Cliente",
                            'phone': order.phone
                        })
                    
                    # Envia notificação de erro para cada passageiro
                    for passenger in passengers_to_notify:
                        try:
                            self.whatsapp_notifier.send_message(
                                name=passenger['name'],
                                phone=passenger['phone'],
                                destination=order.dropoff_address or order.pickup_address or "destino",
                                status="Erro"
                            )
                        except Exception as whatsapp_error:
                            logger.warning(f"Failed to send error WhatsApp to {passenger['name']}: {whatsapp_error}")
                    
                    if passengers_to_notify:
                        logger.info(f"Error notifications sent via WhatsApp for order {order.id}")
            
        except Exception as e:
            order.status = OrderStatus.FAILED
            order.error_message = f"Processing error: {str(e)}"
            
            if order.id:
                self.db.update_order(order)
            else:
                order.id = self.db.create_order(order)
            
            logger.error(f"Error processing order: {e}")
        
        return order
    
    def _process_round_trip(self, email: EmailMessage, base_order: Order, extracted_data: dict) -> Order:
        """
        Processa viagem de ida e volta (2 orders).
        
        Args:
            email: Email original
            base_order: Order base com dados extraídos
            extracted_data: Dados do LLM
            
        Returns:
            Order da viagem de IDA (a de VOLTA é criada separadamente)
        """
        logger.info("Processing round trip - creating 2 orders")
        
        # ========== ORDER 1: IDA ==========
        outbound_order = base_order
        outbound_order.raw_email_body = f"{outbound_order.raw_email_body}\n[VIAGEM: IDA]"
        
        logger.info("Processing OUTBOUND trip...")
        
        # Geocoding e otimização para IDA
        destination_coords = None
        if outbound_order.dropoff_address:
            dropoff_coords = self.geocoder.geocode_address(outbound_order.dropoff_address)
            if dropoff_coords:
                outbound_order.dropoff_lat, outbound_order.dropoff_lng = dropoff_coords
                destination_coords = dropoff_coords
        
        # Geocoding múltiplos passageiros se houver
        if outbound_order.passengers:
            for passenger in outbound_order.passengers:
                coords = self.geocoder.geocode_address(passenger.get('address', ''))
                if coords:
                    passenger['lat'] = coords[0]
                    passenger['lng'] = coords[1]
            
            # Otimizar rota para IDA
            optimized_passengers = RouteOptimizer.optimize_pickup_sequence(
                outbound_order.passengers, destination_coords
            )
            outbound_order.passengers = optimized_passengers
            
            if outbound_order.passengers and 'lat' in outbound_order.passengers[0]:
                outbound_order.pickup_lat = outbound_order.passengers[0]['lat']
                outbound_order.pickup_lng = outbound_order.passengers[0]['lng']
            else:
                pickup_coords = self.geocoder.geocode_address(outbound_order.pickup_address)
                if not pickup_coords:
                    outbound_order.status = OrderStatus.MANUAL_REVIEW
                    outbound_order.error_message = "Failed to geocode pickup address (outbound)"
                    outbound_order.id = self.db.create_order(outbound_order)
                    logger.warning(f"Outbound order {outbound_order.id} requires manual review")
                    return outbound_order
                outbound_order.pickup_lat, outbound_order.pickup_lng = pickup_coords
        else:
            # Passageiro único
            pickup_coords = self.geocoder.geocode_address(outbound_order.pickup_address)
            if not pickup_coords:
                outbound_order.status = OrderStatus.MANUAL_REVIEW
                outbound_order.error_message = "Failed to geocode pickup address (outbound)"
                outbound_order.id = self.db.create_order(outbound_order)
                logger.warning(f"Outbound order {outbound_order.id} requires manual review")
                return outbound_order
            outbound_order.pickup_lat, outbound_order.pickup_lng = pickup_coords
            outbound_order.status = OrderStatus.MANUAL_REVIEW
            outbound_order.error_message = "Failed to geocode pickup address (outbound)"
            outbound_order.id = self.db.create_order(outbound_order)
            logger.warning(f"Outbound order {outbound_order.id} requires manual review")
            return outbound_order
        
        outbound_order.pickup_lat, outbound_order.pickup_lng = pickup_coords
        
        # Geocoding dropoff (destino - DELP, etc)
        if outbound_order.dropoff_address:
            dropoff_coords = self.geocoder.geocode_address(outbound_order.dropoff_address)
            if dropoff_coords:
                outbound_order.dropoff_lat, outbound_order.dropoff_lng = dropoff_coords
        
        outbound_order.status = OrderStatus.GEOCODED
        outbound_order.id = self.db.create_order(outbound_order)
        logger.info(f"Outbound order {outbound_order.id} created")
        
        # Dispatch IDA
        try:
            response = self.minastaxi_client.dispatch_order(outbound_order)
            outbound_order.status = OrderStatus.DISPATCHED
            outbound_order.minastaxi_order_id = response.get('order_id')
            self.db.update_order(outbound_order)
            logger.info(f"Outbound order {outbound_order.id} dispatched successfully")
        except Exception as e:
            outbound_order.status = OrderStatus.FAILED
            outbound_order.error_message = f"Dispatch failed (outbound): {str(e)}"
            self.db.update_order(outbound_order)
            logger.error(f"Failed to dispatch outbound order: {e}")
        
        # ========== ORDER 2: VOLTA ==========
        return_order = Order(
            email_id=f"{email.uid}_return",
            raw_email_body=f"{base_order.raw_email_body}\n[VIAGEM: VOLTA]",
            passenger_name=base_order.passenger_name,
            phone=base_order.phone,
            passengers=base_order.passengers,
            pickup_time=base_order.return_time,
            status=OrderStatus.EXTRACTED
        )
        
        # VOLTA: origem = destino da IDA, destino = origem da IDA
        return_order.pickup_address = outbound_order.dropoff_address
        return_order.dropoff_address = outbound_order.pickup_address
        return_order.pickup_lat = outbound_order.dropoff_lat
        return_order.pickup_lng = outbound_order.dropoff_lng
        return_order.dropoff_lat = outbound_order.pickup_lat
        return_order.dropoff_lng = outbound_order.pickup_lng
        
        logger.info("Processing RETURN trip...")
        
        return_order.status = OrderStatus.GEOCODED
        return_order.id = self.db.create_order(return_order)
        logger.info(f"Return order {return_order.id} created")
        
        # Dispatch VOLTA
        try:
            response = self.minastaxi_client.dispatch_order(return_order)
            return_order.status = OrderStatus.DISPATCHED
            return_order.minastaxi_order_id = response.get('order_id')
            self.db.update_order(return_order)
            logger.info(f"Return order {return_order.id} dispatched successfully")
        except Exception as e:
            return_order.status = OrderStatus.FAILED
            return_order.error_message = f"Dispatch failed (return): {str(e)}"
            self.db.update_order(return_order)
            logger.error(f"Failed to dispatch return order: {e}")
        
        # Notificação WhatsApp para ambas as viagens
        if self.whatsapp_enabled and self.whatsapp_notifier and base_order.phone:
            try:
                self.whatsapp_notifier.send_message(
                    name=base_order.passenger_name or "Cliente",
                    phone=base_order.phone,
                    destination=f"IDA: {outbound_order.dropoff_address}, VOLTA: {return_order.dropoff_address}",
                    status="Sucesso (Ida e Volta)"
                )
                logger.info("WhatsApp notification sent for round trip")
            except Exception as whatsapp_error:
                logger.warning(f"Failed to send WhatsApp notification: {whatsapp_error}")
        
        logger.info(f"Round trip processed: Outbound={outbound_order.id}, Return={return_order.id}")
        return outbound_order
    
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
