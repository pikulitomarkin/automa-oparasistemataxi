"""
Database manager for SQLite operations.
"""
import sqlite3
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..models import Order, OrderStatus

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerencia todas as operações de banco de dados SQLite."""
    
    def __init__(self, db_path: str = "data/taxi_orders.db"):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite.
        """
        self.db_path = db_path
        # Garante que o diretório existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Cria as tabelas necessárias se não existirem."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT UNIQUE,
                    passenger_name TEXT,
                    phone TEXT,
                    pickup_address TEXT,
                    dropoff_address TEXT,
                    pickup_lat REAL,
                    pickup_lng REAL,
                    dropoff_lat REAL,
                    dropoff_lng REAL,
                    pickup_time TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    raw_email_body TEXT,
                    error_message TEXT,
                    minastaxi_order_id TEXT,
                    cluster_id INTEGER,
                    whatsapp_sent INTEGER DEFAULT 0,
                    whatsapp_message_id TEXT
                )
            """)
            
            # Índices para melhorar performance de queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON orders(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pickup_time 
                ON orders(pickup_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON orders(created_at DESC)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def create_order(self, order: Order) -> int:
        """
        Cria um novo pedido no banco de dados.
        
        Args:
            order: Objeto Order a ser salvo.
            
        Returns:
            ID do pedido criado.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (
                    email_id, passenger_name, phone, pickup_address, 
                    dropoff_address, pickup_lat, pickup_lng, dropoff_lat, 
                    dropoff_lng, pickup_time, status, created_at, updated_at,
                    raw_email_body, error_message, minastaxi_order_id, cluster_id,
                    whatsapp_sent, whatsapp_message_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.email_id,
                order.passenger_name,
                order.phone,
                order.pickup_address,
                order.dropoff_address,
                order.pickup_lat,
                order.pickup_lng,
                order.dropoff_lat,
                order.dropoff_lng,
                order.pickup_time.isoformat() if order.pickup_time else None,
                order.status.value,
                order.created_at.isoformat(),
                order.updated_at.isoformat(),
                order.raw_email_body,
                order.error_message,
                order.minastaxi_order_id,
                1 if order.whatsapp_sent else 0,
                order.whatsapp_message_id,
                order.cluster_id
            ))
            conn.commit()
            order_id = cursor.lastrowid
            logger.info(f"Order created with ID: {order_id}")
            return order_id
    
    def update_order(self, order: Order):
        """
        Atualiza um pedido existente.
        
        Args:
            order: Objeto Order com dados atualizados (deve ter ID).
        """
        if not order.id:
            raise ValueError("Order must have an ID to be updated")
        
        order.updated_at = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders SET
                    passenger_name = ?,
                    phone = ?,
                    pickup_address = ?,
                    dropoff_address = ?,
                    pickup_lat = ?,
                    pickup_lng = ?,
                    dropoff_lat = ?,
                    dropoff_lng = ?,
                    pickup_time = ?,
                    status = ?,
                    updated_at = ?,
                    error_message = ?,
                    minastaxi_order_id = ?,
                    cluster_id = ?
                WHERE id = ?
            """, (
                order.passenger_name,
                order.phone,
                order.pickup_address,
                order.dropoff_address,
                order.pickup_lat,
                order.pickup_lng,
                order.dropoff_lat,
                order.dropoff_lng,
                order.pickup_time.isoformat() if order.pickup_time else None,
                order.status.value,
                order.updated_at.isoformat(),
                order.error_message,
                order.minastaxi_order_id,
                order.cluster_id,
                order.id
            ))
            conn.commit()
            logger.info(f"Order {order.id} updated with status {order.status.value}")
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Busca um pedido pelo ID.
        
        Args:
            order_id: ID do pedido.
            
        Returns:
            Objeto Order ou None se não encontrado.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_order(row)
            return None
    
    def get_order_by_email_id(self, email_id: str) -> Optional[Order]:
        """
        Busca um pedido pelo ID do e-mail.
        
        Args:
            email_id: ID único do e-mail.
            
        Returns:
            Objeto Order ou None se não encontrado.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE email_id = ?", (email_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_order(row)
            return None
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """
        Busca todos os pedidos com determinado status.
        
        Args:
            status: Status dos pedidos a buscar.
            
        Returns:
            Lista de objetos Order.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC",
                (status.value,)
            )
            rows = cursor.fetchall()
            return [self._row_to_order(row) for row in rows]
    
    def get_all_orders(self, limit: int = 100) -> List[Order]:
        """
        Busca todos os pedidos, ordenados por data de criação.
        
        Args:
            limit: Número máximo de pedidos a retornar.
            
        Returns:
            Lista de objetos Order.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [self._row_to_order(row) for row in rows]
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas sobre os pedidos.
        
        Returns:
            Dicionário com contagens por status.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM orders 
                GROUP BY status
            """)
            rows = cursor.fetchall()
            
            stats = {status.value: 0 for status in OrderStatus}
            for row in rows:
                stats[row[0]] = row[1]
            
            # Total
            stats['total'] = sum(stats.values())
            
            return stats
    
    def delete_order(self, order_id: int) -> bool:
        """
        Deleta um pedido do banco de dados.
        
        Args:
            order_id: ID do pedido a deletar.
            
        Returns:
            True se deletado com sucesso.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_order(self, row: sqlite3.Row) -> Order:
        """Converte uma linha do banco em objeto Order."""
        return Order(
            id=row['id'],
            email_id=row['email_id'],
            passenger_name=row['passenger_name'],
            phone=row['phone'],
            pickup_address=row['pickup_address'],
            dropoff_address=row['dropoff_address'],
            pickup_lat=row['pickup_lat'],
            pickup_lng=row['pickup_lng'],
            dropoff_lat=row['dropoff_lat'],
            dropoff_lng=row['dropoff_lng'],
            pickup_time=datetime.fromisoformat(row['pickup_time']) if row['pickup_time'] else None,
            status=OrderStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            raw_email_body=row['raw_email_body'],
            error_message=row['error_message'],
            minastaxi_order_id=row['minastaxi_order_id'],
            cluster_id=row['cluster_id']
        )
