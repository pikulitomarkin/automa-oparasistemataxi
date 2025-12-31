"""
Script auxiliar para execução contínua do processador.
Lê e-mails periodicamente conforme intervalo configurado.
"""
import sys
import os
import time
import logging
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processor import TaxiOrderProcessor
from dotenv import load_dotenv

load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'data/taxi_automation.log')),
        logging.StreamHandler(sys.stdout)  # Explicitamente usa stdout
    ]
)

# Força unbuffered output para Railway ver logs em tempo real
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

logger = logging.getLogger(__name__)

def main_loop():
    """
    Executa processador em loop contínuo com intervalo configurável.
    """
    # Intervalo entre execuções (em minutos)
    interval_minutes = int(os.getenv('PROCESSOR_INTERVAL_MINUTES', 5))
    interval_seconds = interval_minutes * 60
    
    # Dias para buscar e-mails
    days_back = int(os.getenv('EMAIL_DAYS_BACK', 7))
    
    logger.info("=" * 80)
    logger.info("CONTINUOUS TAXI ORDER PROCESSOR STARTED")
    logger.info(f"Checking for new emails every {interval_minutes} minutes")
    logger.info(f"Email search window: last {days_back} days")
    logger.info("=" * 80)
    
    # Inicializa processador uma vez
    try:
        processor = TaxiOrderProcessor()
        logger.info("Processor initialized successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize processor: {e}")
        return
    
    # Loop infinito
    cycle_count = 0
    while True:
        cycle_count += 1
        
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"PROCESSING CYCLE #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Processa novos pedidos
            stats = processor.process_new_orders(days_back=days_back)
            
            logger.info(f"Processing Statistics: {stats}")
            
            # Estatísticas do banco
            db_stats = processor.get_statistics()
            logger.info(f"Database Statistics: {db_stats}")
            
            # Próxima execução
            next_run = datetime.now().timestamp() + interval_seconds
            next_run_str = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"\nCycle #{cycle_count} complete. Next check at {next_run_str}")
            logger.info(f"Sleeping for {interval_minutes} minutes...\n")
            
            # Aguarda intervalo
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            logger.info("\nProcessor stopped by user (Ctrl+C)")
            break
        except Exception as e:
            logger.error(f"Error in processing cycle #{cycle_count}: {e}", exc_info=True)
            logger.warning(f"Waiting {interval_minutes} minutes before retry...")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("\nProcessor terminated by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
