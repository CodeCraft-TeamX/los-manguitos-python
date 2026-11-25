"""Conjunto de datos de ejemplo para la demostración del prototipo."""

from __future__ import annotations

from src.modelos import Item
from src.sistema import Sistema


def cargar_datos_demo(sistema: Sistema) -> Sistema:
    """Carga categorías, productos, stock, clientes, ventas, pedidos y red."""
    # Funcionalidad 1: árbol de categorías y catálogo.
    sistema.productos.registrar_categoria("Indumentaria")
    sistema.productos.registrar_categoria("Mangas", "Indumentaria")
    sistema.productos.registrar_categoria("Manos", "Indumentaria")
    sistema.productos.registrar_categoria("Térmicas", "Mangas")
    sistema.productos.registrar_producto("MANG-01", "Manga térmica", "Térmicas", "PROV-01")
    sistema.productos.registrar_producto("MANG-02", "Manga clásica", "Mangas", "PROV-01")
    sistema.productos.registrar_producto("GUAN-01", "Guante de trabajo", "Manos", "PROV-02")

    # Funcionalidad 2: ubicaciones y stock inicial.
    for id_ubicacion, nombre, tipo in (
        ("CENTRAL", "Casa central", "central"),
        ("BODEGA-NORTE", "Bodega norte", "bodega"),
        ("BODEGA-SUR", "Bodega sur", "bodega"),
        ("SUC-01", "Sucursal Centro", "sucursal"),
        ("SUC-02", "Sucursal Norte", "sucursal"),
    ):
        sistema.ubicaciones.registrar_ubicacion(id_ubicacion, nombre, tipo)
    for id_ubicacion, sku, cantidad in (
        ("CENTRAL", "MANG-01", 40),
        ("CENTRAL", "MANG-02", 20),
        ("CENTRAL", "GUAN-01", 15),
        ("BODEGA-NORTE", "MANG-01", 10),
        ("SUC-01", "MANG-01", 8),
        ("SUC-02", "GUAN-01", 4),
    ):
        sistema.ubicaciones.ajustar_stock(id_ubicacion, sku, cantidad)
    for sku, tipo, cantidad in (
        ("MANG-01", "entrada", 40),
        ("MANG-01", "salida", 5),
        ("MANG-02", "entrada", 20),
    ):
        sistema.productos.registrar_movimiento(sku, tipo, cantidad, "Datos de ejemplo")

    # Funcionalidad 3: clientes y ventas (descuentan stock y emiten eventos).
    sistema.ventas.registrar_cliente("CLI-01", "Juan Pérez", "natural")
    sistema.ventas.registrar_cliente("CLI-02", "Distribuidora Sur", "empresa")
    sistema.registrar_venta("VEN-001", "CLI-01", [Item("MANG-01", 2, 25000)])
    sistema.registrar_venta("VEN-002", "CLI-02", [Item("GUAN-01", 1, 18000)])

    # Funcionalidad 4: pedidos pendientes en la cola de atención.
    sistema.crear_pedido("PED-001", "CLI-01", "SUC-01", [Item("MANG-01", 2, 25000)])
    sistema.crear_pedido("PED-002", "CLI-02", "SUC-02", [Item("GUAN-01", 1, 18000)])
    sistema.crear_pedido("PED-003", "CLI-01", "SUC-01", [Item("MANG-02", 3, 19000)])

    # Funcionalidad 5: red logística y una transferencia pendiente.
    for nodo in ("CENTRAL", "BODEGA-NORTE", "BODEGA-SUR", "SUC-01", "SUC-02"):
        sistema.logistica.agregar_nodo(nodo)
    for origen, destino, distancia in (
        ("CENTRAL", "BODEGA-NORTE", 12),
        ("CENTRAL", "BODEGA-SUR", 8),
        ("BODEGA-NORTE", "SUC-01", 7),
        ("BODEGA-SUR", "SUC-02", 9),
        ("BODEGA-NORTE", "SUC-02", 15),
    ):
        sistema.logistica.agregar_conexion(origen, destino, distancia)
    sistema.solicitar_transferencia("TR-001", "CENTRAL", "SUC-02", "MANG-01", 5)
    return sistema


def crear_sistema_con_datos() -> Sistema:
    """Crea un sistema nuevo ya cargado con los datos de demostración."""
    return cargar_datos_demo(Sistema())
