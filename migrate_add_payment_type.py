"""Script de migração para adicionar coluna payment_type no banco de dados.
Este script pode ser executado manualmente em ambientes locais ou em Railway caso queira aplicar antes da
primeira execução do processor.

Uso:
    python migrate_add_payment_type.py

Ele adiciona a coluna e, se houver pedidos existentes, inicializa com valor padrão
'ONLINE_PAYMENT' ou valor lido de MINASTAXI_PAYMENT_TYPE.
"""
import sqlite3
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    db_path = os.getenv('DATABASE_PATH', 'data/taxi_orders.db')
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'payment_type' in cols:
            logger.info('Coluna payment_type já existe, nada a fazer.')
            return

        logger.info('Adicionando coluna payment_type...')
        cursor.execute("ALTER TABLE orders ADD COLUMN payment_type TEXT")
        default = os.getenv('MINASTAXI_PAYMENT_TYPE', 'ONLINE_PAYMENT')
        cursor.execute("UPDATE orders SET payment_type = ? WHERE payment_type IS NULL", (default,))
        conn.commit()
        logger.info('Migração concluída, valores default aplicados.')

if __name__ == '__main__':
    main()
