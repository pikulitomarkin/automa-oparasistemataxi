#!/bin/bash

# Criar diretório de dados se não existir
mkdir -p data

echo "Starting Taxi Automation System..."

# Executar processador em loop contínuo em background
echo "Starting continuous email processor (checking every ${PROCESSOR_INTERVAL_MINUTES:-5} minutes)..."
# Redireciona para arquivo E mantém cópia no stdout para Railway ver
python run_processor.py 2>&1 | tee data/processor.log &
PROCESSOR_PID=$!
echo "Processor started with PID: $PROCESSOR_PID"

# Aguardar alguns segundos para garantir inicialização
sleep 5

# Mostrar primeiras linhas do log para confirmar funcionamento
echo "Initial processor logs:"
if [ -f data/processor.log ]; then
    tail -10 data/processor.log
fi

echo ""
echo "Processor is running in background. Logs are in data/processor.log"
echo ""

# Executar Streamlit
echo "Starting Streamlit dashboard on port ${PORT:-8501}..."
streamlit run app_liquid.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
