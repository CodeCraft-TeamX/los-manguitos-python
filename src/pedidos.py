"""Funcionalidad 4: administración de pedidos.

Estructuras: ``deque`` FIFO de atención, diccionario índice por ID y pila de
historial de estados para deshacer el último cambio.
"""

from __future__ import annotations

from collections import deque

from src.errores import (
    ErrorDeNegocio,
    NoEncontrado,
    TransicionInvalida,
    ValidacionError,
)
from src.modelos import Item, Pedido
from src.utils import texto_requerido
from src.ventas import GestorVentas

ESTADOS = ("RECIBIDO", "PREPARANDO", "LISTO", "DESPACHADO", "CANCELADO")
TRANSICIONES: dict[str, set[str]] = {
    "RECIBIDO": {"PREPARANDO", "CANCELADO"},
    "PREPARANDO": {"LISTO", "CANCELADO"},
    "LISTO": {"DESPACHADO", "CANCELADO"},
    "DESPACHADO": set(),
    "CANCELADO": set(),
}


class GestorPedidos:
    """Administra la cola de atención y los estados de los pedidos."""

    def __init__(self) -> None:
        self._cola: deque[Pedido] = deque()
        self._pedidos: dict[str, Pedido] = {}
        self._historial: dict[str, list[str]] = {}

    def crear_pedido(
        self, id_pedido: str, id_cliente: str, destino: str, items: list[Item]
    ) -> Pedido:
        """Registra un pedido y lo encola para atención."""
        id_pedido = texto_requerido(id_pedido, "ID de pedido")
        if id_pedido in self._pedidos:
            raise ValidacionError(f"Pedido '{id_pedido}' ya registrado")
        GestorVentas.validar_items(items)
        pedido = Pedido(
            id=id_pedido,
            cliente_id=texto_requerido(id_cliente, "ID de cliente"),
            destino=texto_requerido(destino, "Destino"),
            items=list(items),
        )
        self._pedidos[id_pedido] = pedido
        self._historial[id_pedido] = []
        self._cola.append(pedido)
        return pedido

    def consultar_pedido(self, id_pedido: str) -> Pedido:
        """Devuelve un pedido por ID para consultar su estado."""
        try:
            return self._pedidos[id_pedido]
        except KeyError as exc:
            raise NoEncontrado(f"Pedido '{id_pedido}' no encontrado") from exc

    def consultar_estado(self, id_pedido: str) -> str:
        """Estado actual de un pedido."""
        return self.consultar_pedido(id_pedido).estado

    def atender_siguiente(self) -> Pedido:
        """Saca el primer pedido de la cola y lo pasa a PREPARANDO."""
        if not self._cola:
            raise ErrorDeNegocio("No hay pedidos pendientes de atención")
        pedido = self._cola.popleft()
        self.cambiar_estado(pedido.id, "PREPARANDO")
        return pedido

    def cambiar_estado(self, id_pedido: str, nuevo_estado: str) -> Pedido:
        """Aplica una transición válida y apila el estado anterior."""
        pedido = self.consultar_pedido(id_pedido)
        if nuevo_estado not in ESTADOS:
            raise ValidacionError(f"Estado inválido: '{nuevo_estado}'")
        if nuevo_estado not in TRANSICIONES[pedido.estado]:
            raise TransicionInvalida(
                f"No se puede pasar de {pedido.estado} a {nuevo_estado}"
            )
        self._historial[id_pedido].append(pedido.estado)
        pedido.estado = nuevo_estado
        return pedido

    def deshacer_ultimo_cambio(self, id_pedido: str) -> Pedido:
        """Restaura el estado anterior (no reinserta el pedido en la cola)."""
        pedido = self.consultar_pedido(id_pedido)
        historial = self._historial[id_pedido]
        if not historial:
            raise ErrorDeNegocio(f"Pedido '{id_pedido}' no tiene cambios para deshacer")
        pedido.estado = historial.pop()
        return pedido

    def pedidos_pendientes(self) -> list[Pedido]:
        """Copia de los pedidos que aún esperan atención."""
        return list(self._cola)

    def todos_los_pedidos(self) -> list[Pedido]:
        """Copia de todos los pedidos registrados."""
        return list(self._pedidos.values())
