"""
API Mock do MinasTaxi - Simula recebimento de pedidos e gera planilha Excel.
"""
from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Arquivo Excel para salvar os agendamentos
EXCEL_FILE = "data/agendamentos_minastaxi.xlsx"

def ensure_data_directory():
    """Garante que o diretório data existe."""
    os.makedirs("data", exist_ok=True)

def save_to_excel(order_data):
    """
    Salva dados do agendamento na planilha Excel.
    
    Args:
        order_data: Dicionário com dados do pedido
    """
    ensure_data_directory()
    
    # Prepara dados para a planilha
    row_data = {
        'Data/Hora Recebimento': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'Nome Cliente': [order_data.get('passenger_name', 'N/A')],
        'Telefone': [order_data.get('passenger_phone', 'N/A')],
        'Email': [order_data.get('passenger_email', 'N/A')],
        'Origem': [order_data.get('pickup_address', 'N/A')],
        'Destino': [order_data.get('destination_address', 'N/A')],
        'Horário Agendado': [order_data.get('pickup_time', 'N/A')],
        'Lat Origem': [order_data.get('pickup_latitude', 'N/A')],
        'Lng Origem': [order_data.get('pickup_longitude', 'N/A')],
        'Lat Destino': [order_data.get('destination_latitude', 'N/A')],
        'Lng Destino': [order_data.get('destination_longitude', 'N/A')],
        'Observações': [order_data.get('notes', 'N/A')],
        'Status API': ['RECEBIDO']
    }
    
    new_df = pd.DataFrame(row_data)
    
    # Se arquivo existe, append; senão cria novo
    if os.path.exists(EXCEL_FILE):
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            logger.warning(f"Erro ao ler arquivo existente: {e}. Criando novo...")
            updated_df = new_df
    else:
        updated_df = new_df
    
    # Salva no Excel
    updated_df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    logger.info(f"✅ Agendamento salvo na planilha: {EXCEL_FILE}")

@app.route('/', methods=['GET'])
def home():
    """Endpoint raiz."""
    return jsonify({
        'service': 'MinasTaxi API Mock',
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            '/dispatch': 'POST - Receber agendamento',
            '/agendamentos': 'GET - Total de agendamentos'
        }
    })

@app.route('/dispatch', methods=['POST'])
def dispatch_order():
    """
    Recebe pedido de táxi e salva na planilha.
    
    Expected JSON:
    {
        "passenger_name": "João Silva",
        "passenger_phone": "31988888888",
        "passenger_email": "joao@email.com",
        "pickup_address": "Rua A, 123",
        "destination_address": "Rua B, 456",
        "pickup_time": "2025-12-27T14:30:00",
        "pickup_latitude": -19.9191,
        "pickup_longitude": -43.9387,
        "destination_latitude": -19.8157,
        "destination_longitude": -43.9542,
        "notes": "Preferência por motorista experiente"
    }
    """
    try:
        order_data = request.get_json()
        
        # Validação básica
        required_fields = ['passenger_name', 'passenger_phone', 'pickup_address', 'destination_address']
        missing_fields = [field for field in required_fields if not order_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Campos obrigatórios faltando: {", ".join(missing_fields)}'
            }), 400
        
        # Salva na planilha
        save_to_excel(order_data)
        
        # Log no console
        logger.info("=" * 60)
        logger.info("🚖 NOVO AGENDAMENTO RECEBIDO")
        logger.info(f"Nome: {order_data.get('passenger_name')}")
        logger.info(f"Telefone: {order_data.get('passenger_phone')}")
        logger.info(f"Origem: {order_data.get('pickup_address')}")
        logger.info(f"Destino: {order_data.get('destination_address')}")
        logger.info(f"Horário: {order_data.get('pickup_time')}")
        logger.info("=" * 60)
        
        # Retorna sucesso (simula resposta real do MinasTaxi)
        return jsonify({
            'success': True,
            'order_id': f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'status': 'dispatched',
            'message': 'Pedido recebido com sucesso',
            'estimated_arrival': '15-20 minutos',
            'driver': {
                'name': 'Motorista Simulado',
                'vehicle': 'Mock Taxi - ABC-1234'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar pedido: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/agendamentos', methods=['GET'])
def get_agendamentos():
    """Retorna total de agendamentos recebidos."""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            return jsonify({
                'total_agendamentos': len(df),
                'arquivo': EXCEL_FILE,
                'ultimo_agendamento': df.iloc[-1].to_dict() if len(df) > 0 else None
            })
        else:
            return jsonify({
                'total_agendamentos': 0,
                'arquivo': EXCEL_FILE,
                'status': 'Nenhum agendamento recebido ainda'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ensure_data_directory()
    print("\n" + "=" * 60)
    print("🚖 MinasTaxi API Mock - INICIADA")
    print("=" * 60)
    print(f"📊 Planilha: {EXCEL_FILE}")
    print("🌐 Endpoints disponíveis:")
    print("   GET  /               - Status da API")
    print("   POST /dispatch       - Receber agendamento")
    print("   GET  /agendamentos   - Ver total de agendamentos")
    print("=" * 60)
    print("\n🚀 Servidor rodando em http://localhost:5000\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
