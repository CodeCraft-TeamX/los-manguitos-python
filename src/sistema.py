"""Fachada del sistema: coordina los módulos y mantiene el flujo de eventos.

El CLI habla solo con esta clase; cada operación de negocio se ejecuta en los
gestores correspondientes y se reporta al módulo de seguimiento.
"""

from __future__ import annotations

from src.errores import StockInsuficiente, TransicionInvalida
from src.logistica import RedLogistica
from src.modelos import Entrega, Item, Pedido, Transferencia, Venta
from src.pedidos import GestorPedidos
from src.productos import GestorProductos
from src.seguimiento import RegistroOperaciones
from src.ubicaciones import GestorUbicaciones
from src.ventas import GestorVentas


class Sistema:
    """Punto de integración de las seis funcionalidades."""

    def __init__(self) -> None:
        self.productos = GestorProductos()
        self.ubicaciones = GestorUbicaciones()
        self.ventas = GestorVentas()
        self.pedidos = GestorPedidos()
        self.logistica = RedLogistica()
        self.seguimiento = RegistroOperaciones()

    # --- Funcionalidad 1: inventario -------------------------------------

    def registrar_entrada(
        self, sku: str, cantidad: int, ubicacion: str, descripcion: str = "Entrada"
    ) -> int:
        """Aumenta el stock y deja constancia del movimiento y del evento."""
        self.productos.consultar_producto(sku)
        stock = self.ubicaciones.ajustar_stock(ubicacion, sku, cantidad)
        self.productos.registrar_movimiento(sku, "entrada", cantidad, descripcion)
        self.seguimiento.registrar_evento(
            "inventario", sku, f"Entrada de {cantidad} en {ubicacion}"
        )
        return stock

    def registrar_salida(
        self, sku: str, cantidad: int, ubicacion: str, descripcion: str = "Salida"
    ) -> int:
        """Disminuye el stock; falla si no hay unidades suficientes."""
        self.productos.consultar_producto(sku)
        stock = self.ubicaciones.ajustar_stock(ubicacion, sku, -cantidad)
        self.productos.registrar_movimiento(sku, "salida", cantidad, descripcion)
        self.seguimiento.registrar_evento(
            "inventario", sku, f"Salida de {cantidad} en {ubicacion}"
        )
        return stock

    def consultar_stock_total(self, sku: str) -> int:
        """Stock total del SKU sumando todas las ubicaciones."""
        self.productos.consultar_producto(sku)
        return self.ubicaciones.stock_total(sku)

    # --- Funcionalidad 2: transferencias ---------------------------------

    def solicitar_transferencia(
        self, id_transferencia: str, origen: str, destino: str, sku: str, cantidad: int
    ) -> Transferencia:
        """Encola una transferencia si hay stock en el origen."""
        transferencia = self.ubicaciones.solicitar_transferencia(
            id_transferencia, origen, destino, sku, cantidad
        )
        self.seguimiento.registrar_evento(
            "transferencia",
            id_transferencia,
            f"Solicitud {origen} -> {destino}: {cantidad} x {sku}",
        )
        return transferencia

    def procesar_siguiente_transferencia(self) -> Transferencia:
        """Atiende la transferencia FIFO y registra el evento."""
        transferencia = self.ubicaciones.procesar_siguiente_transferencia()
        self.seguimiento.registrar_evento(
            "transferencia",
            transferencia.id,
            f"Transferencia completada {transferencia.origen} -> "
            f"{transferencia.destino}: {transferencia.cantidad} x {transferencia.sku}",
        )
        return transferencia

    # --- Funcionalidad 3: ventas -----------------------------------------

    def registrar_venta(
        self, id_venta: str, id_cliente: str, items: list[Item], ubicacion: str = "CENTRAL"
    ) -> Venta:
        """Venta atómica: valida todo el stock antes de descontarlo."""
        self.ventas.consultar_cliente(id_cliente)
        self.ventas.validar_items(items)
        for item in items:
            self.productos.consultar_producto(item.sku)
            disponible = self.ubicaciones.consultar_stock(ubicacion, item.sku)
            if disponible < item.cantidad:
                raise StockInsuficiente(
                    f"Stock insuficiente de '{item.sku}' en '{ubicacion}' "
                    f"(disponible: {disponible})"
                )
        for item in items:
            self.ubicaciones.ajustar_stock(ubicacion, item.sku, -item.cantidad)
            self.productos.registrar_movimiento(
                item.sku, "salida", item.cantidad, f"Venta {id_venta}"
            )
        venta = self.ventas.registrar_venta(id_venta, id_cliente, items)
        self.seguimiento.registrar_evento(
            "venta", id_venta, f"Venta registrada por {venta.total}"
        )
        return venta

    def cancelar_ultima_venta(self, ubicacion: str = "CENTRAL") -> Venta:
        """Cancela la última venta y devuelve las unidades al stock."""
        venta = self.ventas.cancelar_ultima_venta()
        for item in venta.items:
            self.ubicaciones.ajustar_stock(ubicacion, item.sku, item.cantidad)
            self.productos.registrar_movimiento(
                item.sku, "entrada", item.cantidad, f"Cancelación {venta.id}"
            )
        self.seguimiento.registrar_evento(
            "venta", venta.id, "Última venta cancelada y stock restaurado"
        )
        return venta

    # --- Funcionalidad 4: pedidos ----------------------------------------

    def crear_pedido(self, id_pedido: str, id_cliente: str, destino: str, items: list[Item]) -> Pedido:
        """Crea un pedido verificando cliente, ítems y stock disponible."""
        self.ventas.consultar_cliente(id_cliente)
        self.ubicaciones.consultar_ubicacion(destino)
        self.ventas.validar_items(items)
        for item in items:
            self.productos.consultar_producto(item.sku)
            if self.ubicaciones.stock_total(item.sku) < item.cantidad:
                raise StockInsuficiente(f"Stock total insuficiente de '{item.sku}'")
        pedido = self.pedidos.crear_pedido(id_pedido, id_cliente, destino, items)
        self.seguimiento.registrar_evento(
            "pedido", id_pedido, f"Pedido creado para {destino}"
        )
        return pedido

    def atender_siguiente_pedido(self) -> Pedido:
        """Atiende el pedido más antiguo de la cola."""
        pedido = self.pedidos.atender_siguiente()
        self.seguimiento.registrar_evento(
            "pedido", pedido.id, "Pedido en preparación"
        )
        return pedido

    def cambiar_estado_pedido(self, id_pedido: str, nuevo_estado: str) -> Pedido:
        """Cambia el estado de un pedido respetando las transiciones."""
        pedido = self.pedidos.cambiar_estado(id_pedido, nuevo_estado)
        self.seguimiento.registrar_evento(
            "pedido", id_pedido, f"Estado cambiado a {nuevo_estado}"
        )
        return pedido

    def deshacer_cambio_pedido(self, id_pedido: str) -> Pedido:
        """Restaura el estado anterior del pedido."""
        pedido = self.pedidos.deshacer_ultimo_cambio(id_pedido)
        self.seguimiento.registrar_evento(
            "pedido", id_pedido, f"Cambio deshecho; estado actual {pedido.estado}"
        )
        return pedido

    def _ubicacion_para_despacho(self, items: list[Item]) -> str:
        """Elige una ubicación con stock suficiente para todos los ítems."""
        ubicaciones = sorted(
            self.ubicaciones.listar_ubicaciones(),
            key=lambda ubicacion: 0 if ubicacion.id == "CENTRAL" else 1,
        )
        for ubicacion in ubicaciones:
            if all(
                self.ubicaciones.consultar_stock(ubicacion.id, item.sku) >= item.cantidad
                for item in items
            ):
                return ubicacion.id
        raise StockInsuficiente("No hay una ubicación con stock para todo el pedido")

    def despachar_pedido(self, id_pedido: str, id_entrega: str) -> Entrega:
        """Calcula la ruta, descuenta stock y registra la entrega."""
        pedido = self.pedidos.consultar_pedido(id_pedido)
        if pedido.estado != "LISTO":
            raise TransicionInvalida(
                f"El pedido debe estar LISTO para despachar (estado: {pedido.estado})"
            )
        ruta = self.logistica.ruta_mas_corta("CENTRAL", pedido.destino)
        origen = self._ubicacion_para_despacho(pedido.items)
        for item in pedido.items:
            self.ubicaciones.ajustar_stock(origen, item.sku, -item.cantidad)
            self.productos.registrar_movimiento(
                item.sku, "salida", item.cantidad, f"Despacho {id_pedido}"
            )
        self.pedidos.cambiar_estado(id_pedido, "DESPACHADO")
        entrega = self.logistica.registrar_entrega(id_entrega, id_pedido, ruta)
        self.seguimiento.registrar_evento(
            "despacho", id_entrega, f"Pedido {id_pedido} en ruta {' -> '.join(ruta)}"
        )
        return entrega

    # --- Funcionalidad 5: logística --------------------------------------

    def ruta_mas_corta(self, origen: str, destino: str) -> list[str]:
        """Ruta de menor distancia entre dos nodos de la red."""
        return self.logistica.ruta_mas_corta(origen, destino)

    def rutas_posibles(self, origen: str, destino: str) -> list[list[str]]:
        """Rutas alternativas mediante DFS recursivo."""
        return self.logistica.rutas_posibles(origen, destino)
