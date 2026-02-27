import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processor import TaxiOrderProcessor
from src.models.order import Order, OrderStatus


def test_disable_geocoding_flag(tmp_path, monkeypatch):
    # setup environment variable to disable geocoding
    monkeypatch.setenv('DISABLE_GEOCODING', 'true')
    # use temp database to avoid collisions
    db_path = tmp_path / 'test.db'
    monkeypatch.setenv('DATABASE_PATH', str(db_path))

    processor = TaxiOrderProcessor()
    # craft fake email object with minimal fields
    class DummyEmail:
        def __init__(self):
            self.uid = 'dummy'
            self.body = 'Origem: A\nDest: B\n'

    email = DummyEmail()
    # inject extraction to produce a dropoff_address and pickup_address
    monkeypatch.setattr(processor.llm_extractor, 'extract_with_fallback', lambda x: {
        'pickup_address': 'A',
        'dropoff_address': 'B',
        'passenger_name': 'Test',
        'phone': '31999999999',
        'pickup_time': datetime.now().isoformat()
    })

    order = processor._process_single_email(email)
    # when geocoding disabled, coordinates should remain None
    assert order.pickup_lat is None
    assert order.dropoff_lat is None
    assert order.status == OrderStatus.DISPATCHED or order.status == OrderStatus.GEOCODED
