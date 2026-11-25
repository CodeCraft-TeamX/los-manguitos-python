"""Entidades del dominio compartidas por todos los módulos."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def ahora() -> datetime:
    """Devuelve la hora actual en UTC (útil para los eventos)."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Producto:
    """Producto del catálogo. El stock vive en ``GestorUbicaciones``."""

    sku: str
    nombre: str
    categoria: str
    proveedor_id: str


@dataclass(frozen=True, slots=True)
class Movimiento:
    """Entrada o salida registrada de un producto."""

    sku: str
    tipo: str
    cantidad: int
    timestamp: datetime
    descripcion: str = ""


@dataclass(frozen=True, slots=True)
class Ubicacion:
    """Central, bodega o sucursal."""

    id: str
    nombre: str
    tipo: str


@dataclass(frozen=True, slots=True)
class Transferencia:
    """Solicitud de movimiento de stock entre dos ubicaciones."""

    id: str
    origen: str
    destino: str
    sku: str
    cantidad: int
    solicitada_en: datetime


@dataclass(frozen=True, slots=True)
class Cliente:
    """Cliente registrado."""

    id: str
    nombre: str
    tipo: str


@dataclass(frozen=True, slots=True)
class Item:
    """Línea de una venta o pedido."""

    sku: str
    cantidad: int
    precio_unitario: int


@dataclass(slots=True)
class Venta:
    """Operación de venta. ``cancelada`` permite conservar el historial."""

    id: str
    cliente_id: str
    items: list[Item]
    total: int
    timestamp: datetime
    cancelada: bool = False


@dataclass(slots=True)
class Pedido:
    """Pedido a atender y despachar hacia una ubicación destino."""

    id: str
    cliente_id: str
    destino: str
    items: list[Item]
    estado: str = "RECIBIDO"
    creado_en: datetime = field(default_factory=ahora)


@dataclass(frozen=True, slots=True)
class Entrega:
    """Despacho de un pedido por una ruta de la red logística."""

    id: str
    pedido_id: str
    ruta: tuple[str, ...]
    registrada_en: datetime


@dataclass(frozen=True, slots=True)
class Evento:
    """Registro inmutable de una operación, usado para auditoría."""

    id: int
    timestamp: datetime
    tipo: str
    operacion_id: str
    descripcion: str
