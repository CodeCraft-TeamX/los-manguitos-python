"""Funcionalidad 6: seguimiento de operaciones.

Log append-only, índice por tipo de evento y árbol binario de búsqueda por
timestamp para consultas por rango con recorrido recursivo in-order.
"""

from __future__ import annotations

from datetime import datetime

from src.errores import ValidacionError
from src.modelos import Evento, ahora
from src.utils import texto_requerido

TIPOS_EVENTO = ("inventario", "venta", "pedido", "despacho", "transferencia")


class _Nodo:
    """Nodo del ABB; la clave es (timestamp, id) para desempatar."""

    __slots__ = ("evento", "izquierdo", "derecho")

    def __init__(self, evento: Evento) -> None:
        self.evento = evento
        self.izquierdo: _Nodo | None = None
        self.derecho: _Nodo | None = None

    @property
    def clave(self) -> tuple[datetime, int]:
        return (self.evento.timestamp, self.evento.id)


class RegistroOperaciones:
    """Registro inmutable de eventos con índices para consultas rápidas."""

    def __init__(self) -> None:
        self._eventos: list[Evento] = []
        self._por_tipo: dict[str, list[int]] = {tipo: [] for tipo in TIPOS_EVENTO}
        self._raiz: _Nodo | None = None
        self._siguiente_id = 1

    def registrar_evento(
        self, tipo: str, operacion_id: str, descripcion: str
    ) -> Evento:
        """Agrega un evento al log, al índice y al árbol por fecha."""
        if tipo not in TIPOS_EVENTO:
            raise ValidacionError(f"Tipo de evento inválido: '{tipo}'")
        evento = Evento(
            id=self._siguiente_id,
            timestamp=ahora(),
            tipo=tipo,
            operacion_id=texto_requerido(operacion_id, "ID de operación"),
            descripcion=texto_requerido(descripcion, "Descripción"),
        )
        self._siguiente_id += 1
        posicion = len(self._eventos)
        self._eventos.append(evento)
        self._por_tipo.setdefault(tipo, []).append(posicion)
        self._raiz = self._insertar(self._raiz, evento)
        return evento

    def _insertar(self, nodo: _Nodo | None, evento: Evento) -> _Nodo:
        """Inserta recursivamente en el ABB y devuelve la raíz resultante."""
        if nodo is None:
            return _Nodo(evento)
        clave = (evento.timestamp, evento.id)
        if clave < nodo.clave:
            nodo.izquierdo = self._insertar(nodo.izquierdo, evento)
        else:
            nodo.derecho = self._insertar(nodo.derecho, evento)
        return nodo

    def eventos_por_tipo(self, tipo: str) -> list[Evento]:
        """Eventos de un tipo usando el índice (sin recorrer todo el log)."""
        return [self._eventos[i] for i in self._por_tipo.get(tipo, [])]

    def eventos_entre(self, desde: datetime, hasta: datetime) -> list[Evento]:
        """Eventos en un rango temporal, recorriendo el ABB en orden."""
        if desde > hasta:
            raise ValidacionError("La fecha 'desde' no puede ser mayor que 'hasta'")
        encontrados: list[Evento] = []
        self._rango(self._raiz, desde, hasta, encontrados)
        return encontrados

    def _rango(
        self,
        nodo: _Nodo | None,
        desde: datetime,
        hasta: datetime,
        salida: list[Evento],
    ) -> None:
        """Recorrido recursivo con poda de ramas fuera del rango."""
        if nodo is None:
            return
        timestamp = nodo.evento.timestamp
        if timestamp >= desde:
            self._rango(nodo.izquierdo, desde, hasta, salida)
        if desde <= timestamp <= hasta:
            salida.append(nodo.evento)
        if timestamp <= hasta:
            self._rango(nodo.derecho, desde, hasta, salida)

    def ultimos_eventos(self, cantidad: int = 10) -> list[Evento]:
        """Los últimos ``cantidad`` eventos registrados."""
        if cantidad < 1:
            raise ValidacionError("La cantidad debe ser mayor que cero")
        return self._eventos[-cantidad:]

    def todos_los_eventos(self) -> list[Evento]:
        """Copia completa del log."""
        return list(self._eventos)

    def resumen_por_tipo(self) -> dict[str, int]:
        """Cantidad de eventos por tipo."""
        return {tipo: len(posiciones) for tipo, posiciones in self._por_tipo.items()}
