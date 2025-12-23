#!/bin/bash

# Criar diretório de dados se não existir
mkdir -p data

# Executar processador em background
python run_processor.py &

# Executar Streamlit
streamlit run app_liquid.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
