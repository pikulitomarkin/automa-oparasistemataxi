import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.order import Order
from src.services.minastaxi_client import MinasTaxiClient


class _FakeResponse:
    status_code = 200
    headers = {}
    text = '{"accepted_and_looking_for_driver": true, "ride_id": "RIDE123"}'

    @staticmethod
    def json():
        return {
            "accepted_and_looking_for_driver": True,
            "ride_id": "RIDE123",
        }


def _build_client():
    return MinasTaxiClient(
        api_url="https://example.com",
        user_id="02572696000156",
        password="0104",
        auth_header="Basic Original",
        timeout=5,
    )


def test_dispatch_includes_passenger_re_single(monkeypatch):
    client = _build_client()
    captured = {}

    def fake_post(endpoint, json, headers, timeout, verify):
        captured["payload"] = json
        return _FakeResponse()

    monkeypatch.setattr(client.session, "post", fake_post)

    order = Order(
        passenger_name="Joao Silva",
        phone="31999999999",
        passenger_re="222222",
        pickup_address="Rua A, Belo Horizonte, MG",
        dropoff_address="Rua B, Belo Horizonte, MG",
        pickup_time=datetime.now() + timedelta(hours=1),
        pickup_lat=-19.9,
        pickup_lng=-43.9,
        dropoff_lat=-19.8,
        dropoff_lng=-43.8,
    )

    result = client.dispatch_order(order)

    assert result["success"] is True
    payload = captured["payload"]
    assert payload["users"][0]["passenger_re"] == "222222"


def test_dispatch_includes_passenger_re_multiple(monkeypatch):
    client = _build_client()
    captured = {}

    def fake_post(endpoint, json, headers, timeout, verify):
        captured["payload"] = json
        return _FakeResponse()

    monkeypatch.setattr(client.session, "post", fake_post)

    order = Order(
        passenger_name="Equipe",
        phone="31999999999",
        pickup_address="Rua A, Belo Horizonte, MG",
        dropoff_address="Rua B, Belo Horizonte, MG",
        pickup_time=datetime.now() + timedelta(hours=1),
        pickup_lat=-19.9,
        pickup_lng=-43.9,
        dropoff_lat=-19.8,
        dropoff_lng=-43.8,
        passengers=[
            {
                "name": "Passageiro 1",
                "phone": "31911111111",
                "passenger_re": "222222",
                "address": "Rua A, Belo Horizonte, MG",
                "lat": -19.91,
                "lng": -43.91,
            },
            {
                "name": "Passageiro 2",
                "phone": "31922222222",
                "passenger_re": "333333",
                "address": "Rua C, Belo Horizonte, MG",
                "lat": -19.92,
                "lng": -43.92,
            },
        ],
    )

    result = client.dispatch_order(order)

    assert result["success"] is True
    payload = captured["payload"]
    assert payload["users"][0]["passenger_re"] == "222222"
    assert payload["users"][1]["passenger_re"] == "333333"
