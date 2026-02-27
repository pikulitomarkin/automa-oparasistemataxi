import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processor import TaxiOrderProcessor
from src.models.order import OrderStatus


def test_solicitante_name_override(tmp_path, monkeypatch):
    # create minimal environment
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'db.sqlite'))
    processor = TaxiOrderProcessor()

    class DummyEmail:
        def __init__(self):
            self.uid = 'u1'
            self.body = (
                "Solicitante: Maria Silva\n"
                "Passageiro: Joao Pereira\n"
                "Origem: A\nDest: B\n"
                "Pagamento: Voucher\n"
                "Horário: 10:00\n"
            )
    # stub extractor to return passenger_name from body erroneously
    monkeypatch.setattr(processor.llm_extractor, 'extract_with_fallback', lambda x: {
        'passenger_name': 'Joao Pereira',
        'phone': '',
        'pickup_address': 'A',
        'dropoff_address': 'B',
        'pickup_time': datetime.now().isoformat()
    })
    email = DummyEmail()
    order = processor._process_single_email(email)
    # passenger_name should have been overridden bySolicitante
    assert order.passenger_name == 'Maria Silva'
    # payment_type should be voucher (regex fallback)
    assert order.payment_type == 'VOUCHER'
    assert order.status != OrderStatus.MANUAL_REVIEW
