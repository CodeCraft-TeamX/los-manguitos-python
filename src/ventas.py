"""Funcionalidad 3: clientes y ventas.

Estructuras: diccionario de clientes, registro append-only de ventas, índice
por cliente y pila LIFO para deshacer la última venta registrada.
"""

from __future__ import annotations

from src.errores import ErrorDeNegocio, NoEncontrado, ValidacionError
from src.modelos import Cliente, Item, Venta, ahora
from src.utils import entero_requerido, texto_requerido

TIPOS_CLIENTE = ("natural", "empresa")


class GestorVentas:
    """Administra clientes, ventas y cancelaciones de la última venta."""

    def __init__(self) -> None:
        self._clientes: dict[str, Cliente] = {}
        self._ventas: list[Venta] = []
        self._por_cliente: dict[str, list[str]] = {}
        self._pila_activas: list[Venta] = []

    def registrar_cliente(self, id_cliente: str, nombre: str, tipo: str) -> Cliente:
        """Da de alta un cliente con ID único."""
        id_cliente = texto_requerido(id_cliente, "ID de cliente")
        if id_cliente in self._clientes:
            raise ValidacionError(f"Cliente '{id_cliente}' ya registrado")
        if tipo not in TIPOS_CLIENTE:
            raise ValidacionError(f"Tipo de cliente inválido: '{tipo}'")
        cliente = Cliente(id_cliente, texto_requerido(nombre, "Nombre"), tipo)
        self._clientes[id_cliente] = cliente
        self._por_cliente[id_cliente] = []
        return cliente

    def consultar_cliente(self, id_cliente: str) -> Cliente:
        """Devuelve un cliente existente."""
        try:
            return self._clientes[id_cliente]
        except KeyError as exc:
            raise NoEncontrado(f"Cliente '{id_cliente}' no encontrado") from exc

    def listar_clientes(self) -> list[Cliente]:
        """Copia de los clientes registrados."""
        return list(self._clientes.values())

    @staticmethod
    def validar_items(items: list[Item]) -> int:
        """Valida los ítems de una venta/pedido y devuelve el total."""
        if not items:
            raise ValidacionError("La operación debe tener al menos un ítem")
        total = 0
        for item in items:
            texto_requerido(item.sku, "SKU")
            entero_requerido(item.cantidad, "Cantidad")
            entero_requerido(item.precio_unitario, "Precio unitario")
            total += item.cantidad * item.precio_unitario
        return total

    def registrar_venta(
        self, id_venta: str, id_cliente: str, items: list[Item]
    ) -> Venta:
        """Registra una venta y la apila para permitir cancelarla."""
        id_venta = texto_requerido(id_venta, "ID de venta")
        if any(venta.id == id_venta for venta in self._ventas):
            raise ValidacionError(f"Venta '{id_venta}' ya registrada")
        self.consultar_cliente(id_cliente)
        total = self.validar_items(items)
        venta = Venta(id_venta, id_cliente, list(items), total, ahora())
        self._ventas.append(venta)
        self._por_cliente[id_cliente].append(id_venta)
        self._pila_activas.append(venta)
        return venta

    def cancelar_ultima_venta(self) -> Venta:
        """Saca la última venta de la pila, la marca cancelada y la devuelve."""
        if not self._pila_activas:
            raise ErrorDeNegocio("No hay ventas activas para cancelar")
        venta = self._pila_activas.pop()
        venta.cancelada = True
        return venta

    def ventas_cliente(self, id_cliente: str, incluir_canceladas: bool = True) -> list[Venta]:
        """Ventas de un cliente usando el índice por cliente."""
        self.consultar_cliente(id_cliente)
        ids = self._por_cliente[id_cliente]
        ventas = [v for v in self._ventas if v.id in ids]
        return ventas if incluir_canceladas else [v for v in ventas if not v.cancelada]

    def todas_las_ventas(self) -> list[Venta]:
        """Copia del registro cronológico de ventas."""
        return list(self._ventas)

    def total_vendido(self) -> int:
        """Suma de las ventas no canceladas."""
        return sum(v.total for v in self._ventas if not v.cancelada)
