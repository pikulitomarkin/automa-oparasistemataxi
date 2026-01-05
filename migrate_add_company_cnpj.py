"""
Migração para adicionar o campo company_cnpj na tabela orders.
Este campo armazena o CNPJ da empresa correspondente ao company_code.

⚠️ NOTA: Esta migração é OPCIONAL para uso local.
No Railway e em produção, a migração roda AUTOMATICAMENTE via DatabaseManager._run_migrations()
Só execute este script se quiser migrar manualmente um banco local.
"""
import sqlite3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_company_cnpj(db_path: str = 'data/taxi_orders.db'):
    """
    Adiciona a coluna company_cnpj na tabela orders.
    
    Args:
        db_path: Caminho para o banco de dados SQLite.
    """
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'company_cnpj' in columns:
            logger.info("✅ Column 'company_cnpj' already exists")
            conn.close()
            return True
        
        # Adiciona a coluna
        logger.info("Adding column 'company_cnpj' to orders table...")
        cursor.execute("""
            ALTER TABLE orders 
            ADD COLUMN company_cnpj TEXT
        """)
        
        conn.commit()
        logger.info("✅ Column 'company_cnpj' added successfully")
        
        # Popula o campo company_cnpj baseado no company_code existente
        logger.info("Populating company_cnpj from company_code...")
        
        # Importa a função de mapeamento
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.config.company_mapping import get_cnpj_from_company_code
        
        cursor.execute("SELECT id, company_code FROM orders WHERE company_code IS NOT NULL")
        orders_with_company = cursor.fetchall()
        
        updated_count = 0
        for order_id, company_code in orders_with_company:
            cnpj = get_cnpj_from_company_code(company_code)
            cursor.execute(
                "UPDATE orders SET company_cnpj = ? WHERE id = ?",
                (cnpj, order_id)
            )
            updated_count += 1
        
        conn.commit()
        logger.info(f"✅ Updated {updated_count} orders with company_cnpj")
        
        # Mostra estatísticas
        cursor.execute("SELECT COUNT(*) FROM orders")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE company_cnpj IS NOT NULL")
        with_cnpj = cursor.fetchone()[0]
        
        logger.info(f"📊 Statistics: {with_cnpj}/{total} orders have company_cnpj")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == '__main__':
    # Executa a migração
    success = migrate_add_company_cnpj()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        exit(1)
