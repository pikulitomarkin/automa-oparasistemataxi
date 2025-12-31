#!/bin/bash

# Criar diretório de dados se não existir
mkdir -p data

echo "Starting Taxi Automation System..."

# Executar processador em loop contínuo em background
echo "Starting continuous email processor (checking every ${PROCESSOR_INTERVAL_MINUTES:-5} minutes)..."
python run_processor.py > data/processor.log 2>&1 &
PROCESSOR_PID=$!
echo "Processor started with PID: $PROCESSOR_PID"

# Aguardar alguns segundos para garantir inicialização
sleep 3

# Executar Streamlit
echo "Starting Streamlit dashboard on port ${PORT:-8501}..."
streamlit run app_liquid.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
