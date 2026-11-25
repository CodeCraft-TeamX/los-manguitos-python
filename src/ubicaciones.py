"""Funcionalidad 2: bodegas, sucursales y transferencias.

Estructuras: diccionario anidado ``ubicación -> sku -> stock`` para consultas
``O(1)`` y ``deque`` FIFO para atender las transferencias por orden de llegada.
"""

from __future__ import annotations

from collections import deque

from src.errores import (
    ErrorDeNegocio,
    NoEncontrado,
    StockInsuficiente,
    ValidacionError,
)
from src.modelos import Transferencia, Ubicacion, ahora
from src.utils import entero_requerido, texto_requerido

TIPOS_UBICACION = ("central", "bodega", "sucursal")


class GestorUbicaciones:
    """Administra el stock por ubicación y la cola de transferencias."""

    def __init__(self) -> None:
        self._ubicaciones: dict[str, Ubicacion] = {}
        self._stock: dict[str, dict[str, int]] = {}
        self._transferencias: deque[Transferencia] = deque()

    def registrar_ubicacion(self, id_ubicacion: str, nombre: str, tipo: str) -> Ubicacion:
        """Da de alta una central, bodega o sucursal."""
        id_ubicacion = texto_requerido(id_ubicacion, "ID de ubicación")
        if id_ubicacion in self._ubicaciones:
            raise ValidacionError(f"Ubicación '{id_ubicacion}' ya registrada")
        if tipo not in TIPOS_UBICACION:
            raise ValidacionError(f"Tipo de ubicación inválido: '{tipo}'")
        ubicacion = Ubicacion(id_ubicacion, texto_requerido(nombre, "Nombre"), tipo)
        self._ubicaciones[id_ubicacion] = ubicacion
        self._stock[id_ubicacion] = {}
        return ubicacion

    def consultar_ubicacion(self, id_ubicacion: str) -> Ubicacion:
        """Devuelve los datos de una ubicación existente."""
        try:
            return self._ubicaciones[id_ubicacion]
        except KeyError as exc:
            raise NoEncontrado(f"Ubicación '{id_ubicacion}' no encontrada") from exc

    def listar_ubicaciones(self) -> list[Ubicacion]:
        """Copia de las ubicaciones registradas."""
        return list(self._ubicaciones.values())

    def consultar_stock(self, id_ubicacion: str, sku: str) -> int:
        """Unidades de un SKU en una ubicación (0 si nunca se registraron)."""
        self.consultar_ubicacion(id_ubicacion)
        return self._stock[id_ubicacion].get(sku, 0)

    def ajustar_stock(self, id_ubicacion: str, sku: str, delta: int) -> int:
        """Suma ``delta`` al stock y devuelve el nuevo valor."""
        self.consultar_ubicacion(id_ubicacion)
        sku = texto_requerido(sku, "SKU")
        if not isinstance(delta, int) or isinstance(delta, bool):
            raise ValidacionError("El ajuste de stock debe ser un entero")
        nuevo = self.consultar_stock(id_ubicacion, sku) + delta
        if nuevo < 0:
            raise StockInsuficiente(
                f"Stock insuficiente de '{sku}' en '{id_ubicacion}' "
                f"(disponible: {self.consultar_stock(id_ubicacion, sku)})"
            )
        self._stock[id_ubicacion][sku] = nuevo
        return nuevo

    def stock_total(self, sku: str) -> int:
        """Suma de unidades del SKU en todas las ubicaciones."""
        return sum(unidades.get(sku, 0) for unidades in self._stock.values())

    def stock_por_ubicacion(self, sku: str) -> dict[str, int]:
        """Devuelve {ubicación: cantidad} para un SKU."""
        return {
            id_ubicacion: unidades[sku]
            for id_ubicacion, unidades in self._stock.items()
            if sku in unidades and unidades[sku] > 0
        }

    def solicitar_transferencia(
        self, id_transferencia: str, origen: str, destino: str, sku: str, cantidad: int
    ) -> Transferencia:
        """Valida stock y encola una transferencia FIFO."""
        id_transferencia = texto_requerido(id_transferencia, "ID de transferencia")
        self.consultar_ubicacion(origen)
        self.consultar_ubicacion(destino)
        if origen == destino:
            raise ValidacionError("El origen y el destino deben ser distintos")
        cantidad = entero_requerido(cantidad, "Cantidad")
        disponible = self.consultar_stock(origen, sku)
        if disponible < cantidad:
            raise StockInsuficiente(
                f"Stock insuficiente de '{sku}' en '{origen}' (disponible: {disponible})"
            )
        transferencia = Transferencia(
            id_transferencia, origen, destino, sku, cantidad, ahora()
        )
        self._transferencias.append(transferencia)
        return transferencia

    def procesar_siguiente_transferencia(self) -> Transferencia:
        """Atiende la transferencia más antigua y mueve el stock."""
        if not self._transferencias:
            raise ErrorDeNegocio("No hay transferencias pendientes")
        transferencia = self._transferencias[0]
        if self.consultar_stock(transferencia.origen, transferencia.sku) < transferencia.cantidad:
            raise StockInsuficiente(
                f"Ya no hay stock suficiente para '{transferencia.id}' "
                f"en '{transferencia.origen}'"
            )
        self._transferencias.popleft()
        self.ajustar_stock(transferencia.origen, transferencia.sku, -transferencia.cantidad)
        self.ajustar_stock(transferencia.destino, transferencia.sku, transferencia.cantidad)
        return transferencia

    def transferencias_pendientes(self) -> list[Transferencia]:
        """Copia de la cola, sin modificarla."""
        return list(self._transferencias)
