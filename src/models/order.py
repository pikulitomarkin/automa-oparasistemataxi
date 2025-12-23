"""
Data models for taxi orders.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderStatus(Enum):
    """Status do pedido no pipeline de processamento."""
    RECEIVED = "received"  # E-mail recebido
    EXTRACTED = "extracted"  # Dados extraídos pela IA
    GEOCODED = "geocoded"  # Coordenadas obtidas
    DISPATCHED = "dispatched"  # Enviado para MinasTaxi
    FAILED = "failed"  # Falha no processamento
    MANUAL_REVIEW = "manual_review"  # Requer atenção manual


@dataclass
class Order:
    """
    Representa um pedido de táxi completo com todos os dados necessários.
    """
    # Identificação
    id: Optional[int] = None
    email_id: Optional[str] = None
    
    # Dados do passageiro
    passenger_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Endereços
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    
    # Coordenadas geográficas
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    
    # Horário
    pickup_time: Optional[datetime] = None
    
    # Status e controle
    status: OrderStatus = OrderStatus.RECEIVED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Informações adicionais
    raw_email_body: Optional[str] = None
    error_message: Optional[str] = None
    minastaxi_order_id: Optional[str] = None
    
    # Cluster para otimização geográfica
    cluster_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Converte o pedido para dicionário."""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'passenger_name': self.passenger_name,
            'phone': self.phone,
            'pickup_address': self.pickup_address,
            'dropoff_address': self.dropoff_address,
            'pickup_lat': self.pickup_lat,
            'pickup_lng': self.pickup_lng,
            'dropoff_lat': self.dropoff_lat,
            'dropoff_lng': self.dropoff_lng,
            'pickup_time': self.pickup_time.isoformat() if self.pickup_time else None,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'error_message': self.error_message,
            'minastaxi_order_id': self.minastaxi_order_id,
            'cluster_id': self.cluster_id
        }
    
    def is_complete(self) -> bool:
        """Verifica se o pedido tem todos os dados necessários."""
        return all([
            self.passenger_name,
            self.phone,
            self.pickup_address,
            self.pickup_time,
            self.pickup_lat,
            self.pickup_lng
        ])
    
    def __repr__(self) -> str:
        return (
            f"Order(id={self.id}, passenger={self.passenger_name}, "
            f"status={self.status.value}, pickup_time={self.pickup_time})"
        )
