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
            
            # Verifica se a tabela já existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # Cria tabela com schema completo
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
                        whatsapp_message_id TEXT,
                        notes TEXT,
                        cost_center TEXT,
                        company_code TEXT
                    )
                """)
                logger.info(f"Created new orders table at {self.db_path}")
            
            # Índices para melhorar performance de queries (safe - IF NOT EXISTS)
            try:
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
            except sqlite3.OperationalError as e:
                logger.warning(f"Could not create index (column may not exist yet): {e}")
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
            
            # Executa migrações automáticas
            self._run_migrations()
    
    def _run_migrations(self):
        """
        Executa migrações automáticas do banco de dados.
        Adiciona colunas que não existem sem perder dados.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verifica colunas existentes
                cursor.execute("PRAGMA table_info(orders)")
                existing_columns = [col[1] for col in cursor.fetchall()]
                
                # Lista de colunas necessárias (novas migrações)
                required_columns = {
                    'notes': 'TEXT',
                    'cost_center': 'TEXT',
                    'company_code': 'TEXT',
                    'company_cnpj': 'TEXT'
                }
                
                # Adiciona colunas que faltam
                migrations_applied = []
                for col_name, col_type in required_columns.items():
                    if col_name not in existing_columns:
                        logger.info(f"Running migration: Adding column '{col_name}'")
                        cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}")
                        migrations_applied.append(col_name)
                
                if migrations_applied:
                    conn.commit()
                    logger.info(f"✅ Migrations completed: {', '.join(migrations_applied)}")
                    
                    # Se adicionou company_cnpj, popula baseado em company_code existente
                    if 'company_cnpj' in migrations_applied:
                        self._populate_company_cnpj(cursor)
                        conn.commit()
                else:
                    logger.debug("Database schema is up to date")
                    
        except Exception as e:
            logger.error(f"Migration error: {e}")
            # Não falha a inicialização se migração falhar
            # (tabela pode já ter as colunas ou ser primeira execução)
    
    def _populate_company_cnpj(self, cursor):
        """
        Popula o campo company_cnpj baseado no company_code existente.
        Chamado automaticamente após adicionar a coluna company_cnpj.
        
        Args:
            cursor: Cursor SQLite ativo.
        """
        try:
            from ..config.company_mapping import get_cnpj_from_company_code
            
            # Busca orders com company_code mas sem company_cnpj
            cursor.execute("""
                SELECT id, company_code 
                FROM orders 
                WHERE company_code IS NOT NULL 
                AND (company_cnpj IS NULL OR company_cnpj = '')
            """)
            orders_to_update = cursor.fetchall()
            
            if not orders_to_update:
                logger.info("No orders need company_cnpj population")
                return
            
            updated_count = 0
            for order_id, company_code in orders_to_update:
                cnpj = get_cnpj_from_company_code(company_code)
                cursor.execute(
                    "UPDATE orders SET company_cnpj = ? WHERE id = ?",
                    (cnpj, order_id)
                )
                updated_count += 1
            
            logger.info(f"✅ Populated company_cnpj for {updated_count} existing orders")
            
        except Exception as e:
            logger.warning(f"Could not populate company_cnpj: {e}")
    
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
                    whatsapp_sent, whatsapp_message_id, notes, cost_center, company_code, company_cnpj
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                order.cluster_id,
                1 if order.whatsapp_sent else 0,
                order.whatsapp_message_id,
                order.notes,
                order.cost_center,
                order.company_code,
                order.company_cnpj
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
                    cluster_id = ?,
                    notes = ?,
                    cost_center = ?,
                    company_code = ?,
                    company_cnpj = ?
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
                order.notes,
                order.cost_center,
                order.company_code,
                order.company_cnpj,
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
    
    def check_duplicate_order(self, passenger_name: str, pickup_address: str, 
                             pickup_time: datetime, tolerance_minutes: int = 30) -> bool:
        """
        Verifica se já existe um pedido similar (mesmo passageiro, endereço) 
        no mesmo horário (com tolerância).
        
        Args:
            passenger_name: Nome do passageiro.
            pickup_address: Endereço de coleta.
            pickup_time: Horário de coleta.
            tolerance_minutes: Tolerância em minutos para considerar duplicado.
            
        Returns:
            True se existe pedido duplicado, False caso contrário.
        """
        if not passenger_name or not pickup_address or not pickup_time:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calcula janela de tempo
                from datetime import timedelta
                time_min = (pickup_time - timedelta(minutes=tolerance_minutes)).isoformat()
                time_max = (pickup_time + timedelta(minutes=tolerance_minutes)).isoformat()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM orders 
                    WHERE LOWER(passenger_name) = LOWER(?)
                    AND LOWER(pickup_address) = LOWER(?)
                    AND pickup_time >= ?
                    AND pickup_time <= ?
                    AND status != 'failed'
                """, (passenger_name, pickup_address, time_min, time_max))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            logger.error(f"Error checking duplicate order: {e}")
            return False
    
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
    
    def cleanup_old_orders(self, days_to_keep: int = 30) -> int:
        """
        Remove pedidos com mais de X dias do banco de dados para otimizar espaço.
        Mantém apenas pedidos criados nos últimos {days_to_keep} dias.
        
        Args:
            days_to_keep: Número de dias de histórico a manter (padrão: 30).
            
        Returns:
            Número de pedidos deletados.
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conta quantos serão deletados
            cursor.execute(
                'SELECT COUNT(*) FROM orders WHERE created_at < ?',
                (cutoff_str,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Deleta pedidos antigos
                cursor.execute(
                    'DELETE FROM orders WHERE created_at < ?',
                    (cutoff_str,)
                )
                conn.commit()
                
                # Executa VACUUM para liberar espaço físico
                cursor.execute('VACUUM')
                
                logger.info(f"Database cleanup: removed {count} orders older than {days_to_keep} days")
            else:
                logger.info(f"Database cleanup: no orders older than {days_to_keep} days found")
            
            return count
    
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
            cluster_id=row['cluster_id'],
            notes=row.get('notes'),
            cost_center=row.get('cost_center'),
            company_code=row.get('company_code'),
            company_cnpj=row.get('company_cnpj')
        )
