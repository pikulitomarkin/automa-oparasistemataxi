#!/usr/bin/env python3
"""
Reprocessador de orders falhadas no banco de dados.
Pega orders com status FAILED e tenta reenviar para API MinasTaxi
usando as correções SSL implementadas.
"""
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

from src.services.database import DatabaseManager
from src.services.minastaxi_client import MinasTaxiClient, MinasTaxiAPIError
from src.services.whatsapp_notifier import WhatsAppNotifier
from src.models import Order, OrderStatus

# Carrega .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class OrderReprocessor:
    """
    Reprocessa orders falhadas no banco de dados.
    """
    
    def __init__(self):
        """Inicializa serviços necessários."""
        logger.info("Inicializando reprocessador de orders...")
        
        # Database
        self.db = DatabaseManager()
        
        # MinasTaxi Client (com correções SSL)
        self.minastaxi_client = MinasTaxiClient(
            api_url=os.getenv('MINASTAXI_API_URL', 'https://vm2c.taxifone.com.br:11048'),
            user_id=os.getenv('MINASTAXI_USER_ID'),
            password=os.getenv('MINASTAXI_PASSWORD'),
            auth_header=os.getenv('MINASTAXI_AUTH_HEADER', 'Basic Original'),
            timeout=int(os.getenv('MINASTAXI_TIMEOUT', 30)),
            max_retries=int(os.getenv('MINASTAXI_RETRY_ATTEMPTS', 3))
        )
        
        # WhatsApp (opcional)
        self.whatsapp_enabled = os.getenv('ENABLE_WHATSAPP_NOTIFICATIONS', 'false').lower() == 'true'
        if self.whatsapp_enabled:
            self.whatsapp_notifier = WhatsAppNotifier(
                api_url=os.getenv('EVOLUTION_API_URL'),
                instance_name=os.getenv('EVOLUTION_INSTANCE_NAME'),
                api_key=os.getenv('EVOLUTION_API_KEY')
            )
            logger.info("WhatsApp notifications enabled")
        else:
            self.whatsapp_notifier = None
            logger.info("WhatsApp notifications disabled")
    
    def get_failed_orders(self):
        """
        Busca todas as orders com status FAILED no banco.
        
        Returns:
            List[Order]: Lista de orders falhadas.
        """
        logger.info("Buscando orders falhadas no banco...")
        
        try:
            # Query direta no banco
            import sqlite3
            db_path = os.getenv('DATABASE_PATH', 'data/taxi_orders.db')
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Busca orders com status FAILED
                cursor.execute("""
                    SELECT * FROM orders 
                    WHERE status = ? 
                    ORDER BY created_at DESC
                """, (OrderStatus.FAILED.value,))
                
                rows = cursor.fetchall()
                
                orders = []
                for row in rows:
                    # Converte row para Order object
                    order = Order(
                        email_id=row['email_id'],
                        passenger_name=row['passenger_name'],
                        phone=row['phone'],
                        pickup_address=row['pickup_address'],
                        pickup_lat=row['pickup_lat'],
                        pickup_lng=row['pickup_lng'],
                        dropoff_address=row['dropoff_address'],
                        dropoff_lat=row['dropoff_lat'],
                        dropoff_lng=row['dropoff_lng'],
                        pickup_time=datetime.fromisoformat(row['pickup_time']) if row['pickup_time'] else None,
                        raw_email_body=row['raw_email_body'],
                        status=OrderStatus(row['status'])
                    )
                    order.id = row['id']
                    order.error_message = row['error_message']
                    order.created_at = datetime.fromisoformat(row['created_at'])
                    
                    # Decodifica passengers JSON se existir
                    if row['passengers_data']:
                        import json
                        order.passengers = json.loads(row['passengers_data'])
                    
                    orders.append(order)
                
                logger.info(f"Encontradas {len(orders)} orders falhadas")
                return orders
                
        except Exception as e:
            logger.error(f"Erro ao buscar orders falhadas: {e}")
            return []
    
    def reprocess_order(self, order: Order):
        """
        Reprocessa uma order falhada.
        
        Args:
            order: Order para reprocessar.
            
        Returns:
            bool: True se reprocessamento foi bem-sucedido.
        """
        logger.info(f"Reprocessando order {order.id}: {order.passenger_name}")
        
        try:
            # Tenta dispatch para MinasTaxi com SSL corrigido
            response = self.minastaxi_client.dispatch_order(order)
            
            # Sucesso - atualiza status
            order.status = OrderStatus.DISPATCHED
            order.minastaxi_order_id = response.get('order_id')
            order.error_message = None  # Limpa erro anterior
            
            # Atualiza no banco
            self.db.update_order(order)
            
            logger.info(f"✅ Order {order.id} reprocessada com sucesso! Ride ID: {response.get('ride_id')}")
            
            # Envia WhatsApp se habilitado
            if self.whatsapp_enabled and self.whatsapp_notifier and order.phone:
                try:
                    whatsapp_response = self.whatsapp_notifier.send_message(
                        name=order.passenger_name or "Cliente",
                        phone=order.phone,
                        destination=order.dropoff_address or order.pickup_address or "destino",
                        status="Sucesso - Reprocessado"
                    )
                    order.whatsapp_sent = True
                    order.whatsapp_message_id = whatsapp_response.get('message_id')
                    self.db.update_order(order)
                    logger.info(f"📱 WhatsApp enviado para order {order.id}")
                except Exception as e:
                    logger.warning(f"Falha ao enviar WhatsApp para order {order.id}: {e}")
            
            return True
            
        except MinasTaxiAPIError as e:
            logger.error(f"❌ Falha API MinasTaxi para order {order.id}: {e}")
            
            # Atualiza erro no banco
            order.error_message = f"Reprocessamento falhou: {str(e)}"
            self.db.update_order(order)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro geral reprocessando order {order.id}: {e}")
            
            # Atualiza erro no banco
            order.error_message = f"Erro reprocessamento: {str(e)}"
            self.db.update_order(order)
            
            return False
    
    def reprocess_all_failed(self):
        """
        Reprocessa todas as orders falhadas.
        
        Returns:
            Dict: Estatísticas do reprocessamento.
        """
        logger.info("🔄 INICIANDO REPROCESSAMENTO DE ORDERS FALHADAS")
        logger.info("=" * 60)
        
        # Busca orders falhadas
        failed_orders = self.get_failed_orders()
        
        if not failed_orders:
            logger.info("✅ Nenhuma order falhada encontrada")
            return {'total': 0, 'success': 0, 'failed': 0}
        
        success_count = 0
        failed_count = 0
        
        # Reprocessa cada order
        for i, order in enumerate(failed_orders, 1):
            logger.info(f"🔄 Reprocessando {i}/{len(failed_orders)}: Order {order.id}")
            logger.info(f"📧 Email ID: {order.email_id}")
            logger.info(f"👤 Passageiro: {order.passenger_name}")
            logger.info(f"📞 Telefone: {order.phone}")
            logger.info(f"📍 Origem: {order.pickup_address}")
            logger.info(f"🎯 Destino: {order.dropoff_address}")
            logger.info(f"❌ Erro anterior: {order.error_message}")
            
            success = self.reprocess_order(order)
            
            if success:
                success_count += 1
                logger.info(f"✅ Order {order.id} reprocessada com sucesso!")
            else:
                failed_count += 1
                logger.info(f"❌ Falha ao reprocessar order {order.id}")
            
            logger.info("-" * 40)
        
        # Estatísticas finais
        stats = {
            'total': len(failed_orders),
            'success': success_count,
            'failed': failed_count
        }
        
        logger.info("=" * 60)
        logger.info("📊 RESULTADO DO REPROCESSAMENTO:")
        logger.info("=" * 60)
        logger.info(f"📋 Total orders: {stats['total']}")
        logger.info(f"✅ Sucessos: {stats['success']}")
        logger.info(f"❌ Falhas: {stats['failed']}")
        logger.info(f"🎯 Taxa sucesso: {(stats['success']/stats['total']*100):.1f}%" if stats['total'] > 0 else "🎯 Taxa sucesso: 0%")
        
        if stats['success'] > 0:
            logger.info("\n🎉 REPROCESSAMENTO CONCLUÍDO COM SUCESSOS!")
            logger.info("🚕 Orders enviadas para MinasTaxi API")
            logger.info("💾 Status atualizado no banco para DISPATCHED")
        else:
            logger.warning("\n⚠️ NENHUMA ORDER REPROCESSADA COM SUCESSO")
            logger.warning("🔧 Verificar configurações SSL e credenciais")
        
        return stats


def main():
    """
    Função principal para executar reprocessamento.
    """
    print("🔄 REPROCESSADOR DE ORDERS FALHADAS")
    print("=" * 60)
    print("🎯 Reprocessando orders com correções SSL implementadas")
    print()
    
    try:
        reprocessor = OrderReprocessor()
        stats = reprocessor.reprocess_all_failed()
        
        print(f"\n🎯 RESULTADO: {stats['success']}/{stats['total']} orders reprocessadas com sucesso")
        
        if stats['success'] > 0:
            print("🎉 Sistema funcionando com correções SSL!")
        
    except Exception as e:
        print(f"❌ ERRO NO REPROCESSAMENTO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()