"""Conjunto de datos de ejemplo para la demostración del prototipo."""

from __future__ import annotations

from src.modelos import Item
from src.sistema import Sistema


def cargar_datos_demo(sistema: Sistema) -> Sistema:
    """Carga proveedores, categorías, productos, stock, clientes, ventas, pedidos y red."""
    # Funcionalidad 1: proveedores, árbol de categorías y catálogo (frutas y procesados).
    sistema.productos.registrar_proveedor("PROV-01", "Finca El Paraíso", "7890-1122")
    sistema.productos.registrar_proveedor("PROV-02", "Procesadora del Valle", "7890-3344")

    sistema.productos.registrar_categoria("Frutas frescas")
    sistema.productos.registrar_categoria("Cítricos", "Frutas frescas")
    sistema.productos.registrar_categoria("Procesados")
    sistema.productos.registrar_categoria("Néctares", "Procesados")

    sistema.productos.registrar_producto("PR-001", "Mango Tommy", "Frutas frescas", "PROV-01")
    sistema.productos.registrar_producto("PR-008", "Limón pérsico", "Cítricos", "PROV-01")
    sistema.productos.registrar_producto("PR-024", "Néctar de mango", "Néctares", "PROV-02")
    sistema.productos.registrar_producto("PR-015", "Aguacate nacional", "Frutas frescas", "PROV-01")
    sistema.productos.registrar_producto("PR-031", "Pulpa de mango", "Procesados", "PROV-02")

    # Funcionalidad 2: ubicaciones y stock inicial.
    for id_ubicacion, nombre, tipo in (
        ("CENTRAL", "Bodega central", "central"),
        ("SUC-CENTRO", "Sucursal Centro", "sucursal"),
        ("SUC-SANTA-ANA", "Sucursal Santa Ana", "sucursal"),
        ("SUC-SAN-MIGUEL", "Sucursal San Miguel", "sucursal"),
        ("PUERTO-LA-LIBERTAD", "Puerto La Libertad", "sucursal"),
    ):
        sistema.ubicaciones.registrar_ubicacion(id_ubicacion, nombre, tipo)
    for id_ubicacion, sku, cantidad in (
        ("CENTRAL", "PR-001", 14),
        ("CENTRAL", "PR-008", 24),
        ("CENTRAL", "PR-024", 19),
        ("CENTRAL", "PR-031", 48),
        ("SUC-CENTRO", "PR-008", 8),
        ("SUC-SANTA-ANA", "PR-015", 74),
    ):
        sistema.ubicaciones.ajustar_stock(id_ubicacion, sku, cantidad)
    for sku, tipo, cantidad, descripcion in (
        ("PR-001", "entrada", 40, "Finca El Paraíso"),
        ("PR-008", "salida", 24, "Transferencia a Santa Ana"),
        ("PR-024", "entrada", 20, "Producción semanal"),
    ):
        sistema.productos.registrar_movimiento(sku, tipo, cantidad, descripcion)

    # Funcionalidad 3: clientes y ventas (descuentan stock y emiten eventos).
    sistema.ventas.registrar_cliente("CLI-01", "Mercado La Ceiba", "frecuente")
    sistema.ventas.registrar_cliente("CLI-02", "Restaurante El Patio", "frecuente")
    sistema.ventas.registrar_cliente("CLI-03", "Rosa Hernández", "minorista")
    sistema.ventas.registrar_cliente("CLI-04", "Hotel Las Palmeras", "frecuente")
    sistema.ventas.registrar_cliente("CLI-05", "José Martínez", "minorista")
    sistema.registrar_venta("V-2026-0841", "CLI-02", [Item("PR-031", 2, 4.10)])
    sistema.registrar_venta(
        "V-2026-0842",
        "CLI-01",
        [Item("PR-001", 2, 2.40), Item("PR-024", 3, 1.50)],
    )

    # Funcionalidad 4: pedidos pendientes en la cola FIFO de atención.
    sistema.crear_pedido("P-2026-311", "CLI-01", "SUC-SANTA-ANA", [Item("PR-001", 5, 2.40)])
    sistema.crear_pedido("P-2026-312", "CLI-02", "SUC-CENTRO", [Item("PR-024", 4, 1.50)])
    sistema.crear_pedido("P-2026-313", "CLI-04", "PUERTO-LA-LIBERTAD", [Item("PR-031", 3, 4.10)])

    # Funcionalidad 5: red logística y una transferencia pendiente.
    for nodo in (
        "CENTRAL",
        "SUC-CENTRO",
        "SUC-SANTA-ANA",
        "SUC-SAN-MIGUEL",
        "PUERTO-LA-LIBERTAD",
    ):
        sistema.logistica.agregar_nodo(nodo)
    for origen, destino, distancia in (
        ("CENTRAL", "SUC-CENTRO", 12),
        ("CENTRAL", "SUC-SANTA-ANA", 26),
        ("CENTRAL", "SUC-SAN-MIGUEL", 48),
        ("CENTRAL", "PUERTO-LA-LIBERTAD", 18),
        ("SUC-CENTRO", "PUERTO-LA-LIBERTAD", 14),
    ):
        sistema.logistica.agregar_conexion(origen, destino, distancia)
    sistema.solicitar_transferencia("TR-2026-019", "CENTRAL", "SUC-SANTA-ANA", "PR-008", 24)
    return sistema


def crear_sistema_con_datos() -> Sistema:
    """Crea un sistema nuevo ya cargado con los datos de demostración."""
    return cargar_datos_demo(Sistema())
