"""
Script de migração para adicionar campos notes e cost_center.
Atualiza banco de dados existente sem perder dados.
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database(db_path: str = "data/taxi_orders.db"):
    """
    Adiciona colunas notes e cost_center na tabela orders.
    
    Args:
        db_path: Caminho para o banco de dados.
    """
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verifica se as colunas já existem
            cursor.execute("PRAGMA table_info(orders)")
            columns = [col[1] for col in cursor.fetchall()]
            
            migrations_needed = []
            if 'notes' not in columns:
                migrations_needed.append('notes')
            if 'cost_center' not in columns:
                migrations_needed.append('cost_center')
            
            if not migrations_needed:
                logger.info("✅ Database already up to date!")
                return True
            
            # Adiciona colunas que faltam
            for col_name in migrations_needed:
                logger.info(f"Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} TEXT")
            
            conn.commit()
            logger.info(f"✅ Migration completed! Added columns: {', '.join(migrations_needed)}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Permite especificar caminho do banco via argumento
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/taxi_orders.db"
    
    logger.info(f"🔄 Starting database migration for: {db_path}")
    logger.info("=" * 60)
    
    success = migrate_database(db_path)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Deploy changes to Railway")
        logger.info("2. Run this script on Railway to update production DB")
        logger.info("")
        logger.info("Railway command:")
        logger.info("  railway run python migrate_add_notes_cost_center.py")
    else:
        logger.error("❌ Migration failed! Check logs above.")
        sys.exit(1)
