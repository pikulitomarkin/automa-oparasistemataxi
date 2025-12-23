#!/bin/bash
# Script para rodar o processador no Linux/Mac

cd "$(dirname "$0")"
source venv/bin/activate
python -m src.processor
