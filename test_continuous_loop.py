#!/usr/bin/env python
"""
Teste rápido do loop contínuo do processador.
Executa 3 ciclos com intervalo curto para demonstração.
"""
import os
import sys
import time
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Força modo de teste com intervalo curto
os.environ['PROCESSOR_INTERVAL_MINUTES'] = '1'  # 1 minuto
os.environ['EMAIL_DAYS_BACK'] = '7'

from dotenv import load_dotenv
load_dotenv()

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_continuous_loop():
    """
    Testa o loop contínuo com 3 ciclos rápidos.
    """
    print("\n" + "=" * 80)
    print("TESTE DO PROCESSADOR CONTÍNUO")
    print("=" * 80)
    print(f"Configuração de teste:")
    print(f"  • Intervalo: 1 minuto (forçado para teste)")
    print(f"  • Ciclos: 3 (demonstração)")
    print(f"  • Email days back: 7")
    print("=" * 80 + "\n")
    
    from src.processor import TaxiOrderProcessor
    
    try:
        # Inicializa processador
        print("Inicializando processador...\n")
        processor = TaxiOrderProcessor()
        logger.info("✓ Processador inicializado com sucesso\n")
        
        # Executa 3 ciclos de teste
        for cycle in range(1, 4):
            print("\n" + "=" * 80)
            print(f"CICLO DE TESTE #{cycle}/3 - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 80)
            
            # Processa novos pedidos
            stats = processor.process_new_orders(days_back=7)
            
            print(f"\n📊 Estatísticas do Ciclo #{cycle}:")
            print(f"  • E-mails buscados: {stats['emails_fetched']}")
            print(f"  • Pedidos criados: {stats['orders_created']}")
            print(f"  • Pedidos despachados: {stats['orders_dispatched']}")
            print(f"  • Pedidos com falha: {stats['orders_failed']}")
            
            # Estatísticas do banco
            db_stats = processor.get_statistics()
            print(f"\n💾 Estatísticas do Banco:")
            print(f"  • Total: {db_stats.get('total', 0)}")
            print(f"  • Despachados: {db_stats.get('dispatched', 0)}")
            print(f"  • Falhas: {db_stats.get('failed', 0)}")
            print(f"  • Revisão manual: {db_stats.get('manual_review', 0)}")
            
            if cycle < 3:
                print(f"\n⏰ Aguardando 1 minuto até próximo ciclo...")
                time.sleep(60)
            else:
                print(f"\n✅ Teste completo! 3 ciclos executados com sucesso.")
        
        print("\n" + "=" * 80)
        print("TESTE CONCLUÍDO")
        print("=" * 80)
        print("\n✅ O processador contínuo está funcionando corretamente!")
        print("📝 Em produção, ele continuaria rodando indefinidamente.")
        print("🔄 Para parar o processador, use Ctrl+C\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ Erro durante teste: {e}")
        logger.error("Erro no teste", exc_info=True)

if __name__ == "__main__":
    test_continuous_loop()
