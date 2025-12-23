"""
Script auxiliar para execução agendada do processador.
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processor import main

if __name__ == "__main__":
    main()
