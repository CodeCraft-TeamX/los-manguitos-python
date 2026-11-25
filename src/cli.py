"""Interfaz de línea de comandos del prototipo de Los Manguitos.

El menú solo presenta datos y captura entradas; toda la lógica de negocio está
en ``Sistema`` y en los gestores de cada funcionalidad.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from src.datos import crear_sistema_con_datos
from src.errores import ErrorDeNegocio
from src.modelos import Item
from src.sistema import Sistema
from src.utils import pausar, pedir_entero, pedir_texto

Opciones = dict[str, tuple[str, Callable[[Sistema], None]]]


def _titulo(texto: str) -> None:
    """Imprime un encabezado visible para cada menú."""
    print("\n" + "=" * 64)
    print(texto)
    print("=" * 64)


def _formatear_items(items: list[Item]) -> str:
    """Representa los ítems de una venta o pedido en una sola línea."""
    return ", ".join(f"{i.cantidad} x {i.sku} (@{i.precio_unitario})" for i in items)


def _leer_items() -> list[Item]:
    """Pide ítems como 'SKU,Cantidad,Precio'; línea vacía termina."""
    items: list[Item] = []
    print("Ítems (formato: SKU,Cantidad,Precio). Línea vacía para terminar:")
    while True:
        linea = pedir_texto("  > ")
        if not linea:
            break
        partes = [parte.strip() for parte in linea.split(",")]
        if len(partes) != 3:
            print("  Formato inválido. Ejemplo: MANG-01,2,25000")
            continue
        try:
            items.append(Item(partes[0], int(partes[1]), int(partes[2])))
        except ValueError:
            print("  Cantidad y precio deben ser enteros.")
    return items


def _submenu(titulo: str, opciones: Opciones, sistema: Sistema) -> None:
    """Muestra un submenú y despacha la acción elegida."""
    while True:
        _titulo(titulo)
        for clave, (etiqueta, _) in opciones.items():
            print(f"  {clave}. {etiqueta}")
        print("  0. Volver al menú principal")
        opcion = pedir_texto("Opción: ")
        if opcion == "0":
            return
        accion = opciones.get(opcion)
        if accion is None:
            print("Opción inválida.")
            pausar()
            continue
        try:
            accion[1](sistema)
        except ErrorDeNegocio as exc:
            print(f"Error: {exc}")
        pausar()


# --- Funcionalidad 1: productos e inventario -----------------------------


def _listar_productos(sistema: Sistema) -> None:
    productos = sistema.productos.listar_productos()
    if not productos:
        print("No hay productos registrados.")
        return
    for producto in productos:
        print(
            f"  {producto.sku:<10} {producto.nombre:<20} "
            f"cat={producto.categoria:<12} proveedor={producto.proveedor_id}"
        )


def _consultar_producto(sistema: Sistema) -> None:
    sku = pedir_texto("SKU: ")
    producto = sistema.productos.consultar_producto(sku)
    print(f"  {producto}")
    print(f"  Stock total: {sistema.consultar_stock_total(sku)}")
    print(f"  Stock por ubicación: {sistema.ubicaciones.stock_por_ubicacion(sku)}")


def _listar_categoria(sistema: Sistema) -> None:
    categoria = pedir_texto("Categoría (incluye subcategorías): ")
    productos = sistema.productos.listar_categoria(categoria)
    if not productos:
        print("No hay productos en esa categoría.")
        return
    for producto in productos:
        print(f"  {producto.sku} - {producto.nombre} ({producto.categoria})")


def _registrar_entrada(sistema: Sistema) -> None:
    sku = pedir_texto("SKU: ")
    cantidad = pedir_entero("Cantidad: ")
    ubicacion = pedir_texto("Ubicación: ")
    stock = sistema.registrar_entrada(sku, cantidad, ubicacion)
    print(f"Entrada registrada. Stock ahora en {ubicacion}: {stock}")


def _registrar_salida(sistema: Sistema) -> None:
    sku = pedir_texto("SKU: ")
    cantidad = pedir_entero("Cantidad: ")
    ubicacion = pedir_texto("Ubicación: ")
    stock = sistema.registrar_salida(sku, cantidad, ubicacion)
    print(f"Salida registrada. Stock ahora en {ubicacion}: {stock}")


def _ver_movimientos(sistema: Sistema) -> None:
    sku = pedir_texto("SKU: ")
    movimientos = sistema.productos.movimientos(sku)
    if not movimientos:
        print("El producto no tiene movimientos registrados.")
        return
    for movimiento in movimientos:
        print(
            f"  {movimiento.timestamp:%Y-%m-%d %H:%M}  {movimiento.tipo:<8} "
            f"{movimiento.cantidad:>4}  {movimiento.descripcion}"
        )


def menu_productos(sistema: Sistema) -> None:
    """Submenú de productos, categorías y movimientos."""
    opciones: Opciones = {
        "1": ("Listar productos", _listar_productos),
        "2": ("Consultar producto y stock", _consultar_producto),
        "3": ("Listar categoría (recursivo)", _listar_categoria),
        "4": ("Registrar entrada", _registrar_entrada),
        "5": ("Registrar salida", _registrar_salida),
        "6": ("Ver movimientos de un producto", _ver_movimientos),
    }
    _submenu("1. Productos e inventario", opciones, sistema)


# --- Funcionalidad 2: bodegas y sucursales -------------------------------


def _listar_ubicaciones(sistema: Sistema) -> None:
    ubicaciones = sistema.ubicaciones.listar_ubicaciones()
    if not ubicaciones:
        print("No hay ubicaciones registradas.")
        return
    for ubicacion in ubicaciones:
        print(f"  {ubicacion.id:<14} {ubicacion.nombre:<20} ({ubicacion.tipo})")


def _consultar_stock(sistema: Sistema) -> None:
    ubicacion = pedir_texto("Ubicación: ")
    sku = pedir_texto("SKU: ")
    cantidad = sistema.ubicaciones.consultar_stock(ubicacion, sku)
    print(f"  {sku} en {ubicacion}: {cantidad} unidades")


def _solicitar_transferencia(sistema: Sistema) -> None:
    id_transferencia = pedir_texto("ID de transferencia: ")
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    sku = pedir_texto("SKU: ")
    cantidad = pedir_entero("Cantidad: ")
    sistema.solicitar_transferencia(id_transferencia, origen, destino, sku, cantidad)
    print(f"Transferencia {id_transferencia} encolada.")


def _procesar_transferencia(sistema: Sistema) -> None:
    transferencia = sistema.procesar_siguiente_transferencia()
    print(
        f"Transferencia {transferencia.id}: {transferencia.cantidad} x "
        f"{transferencia.sku} de {transferencia.origen} a {transferencia.destino}"
    )


def _ver_transferencias(sistema: Sistema) -> None:
    pendientes = sistema.ubicaciones.transferencias_pendientes()
    if not pendientes:
        print("No hay transferencias pendientes.")
        return
    for transferencia in pendientes:
        print(
            f"  {transferencia.id}: {transferencia.origen} -> {transferencia.destino} "
            f"({transferencia.cantidad} x {transferencia.sku})"
        )


def menu_ubicaciones(sistema: Sistema) -> None:
    """Submenú de ubicaciones y transferencias."""
    opciones: Opciones = {
        "1": ("Listar ubicaciones", _listar_ubicaciones),
        "2": ("Consultar stock por ubicación", _consultar_stock),
        "3": ("Solicitar transferencia", _solicitar_transferencia),
        "4": ("Procesar siguiente transferencia (FIFO)", _procesar_transferencia),
        "5": ("Ver transferencias pendientes", _ver_transferencias),
    }
    _submenu("2. Bodegas y sucursales", opciones, sistema)


# --- Funcionalidad 3: clientes y ventas ----------------------------------


def _listar_clientes(sistema: Sistema) -> None:
    clientes = sistema.ventas.listar_clientes()
    if not clientes:
        print("No hay clientes registrados.")
        return
    for cliente in clientes:
        print(f"  {cliente.id:<8} {cliente.nombre:<24} ({cliente.tipo})")


def _registrar_cliente(sistema: Sistema) -> None:
    id_cliente = pedir_texto("ID de cliente: ")
    nombre = pedir_texto("Nombre: ")
    tipo = pedir_texto("Tipo (natural/empresa): ")
    sistema.ventas.registrar_cliente(id_cliente, nombre, tipo)
    print(f"Cliente {id_cliente} registrado.")


def _registrar_venta(sistema: Sistema) -> None:
    id_venta = pedir_texto("ID de venta: ")
    id_cliente = pedir_texto("ID de cliente: ")
    items = _leer_items()
    venta = sistema.registrar_venta(id_venta, id_cliente, items)
    print(f"Venta {venta.id} registrada por {venta.total}.")


def _listar_ventas(sistema: Sistema) -> None:
    ventas = sistema.ventas.todas_las_ventas()
    if not ventas:
        print("No hay ventas registradas.")
        return
    for venta in ventas:
        estado = "CANCELADA" if venta.cancelada else "ACTIVA"
        print(
            f"  {venta.id:<10} cliente={venta.cliente_id:<8} "
            f"total={venta.total:<8} {estado} [{_formatear_items(venta.items)}]"
        )


def _ventas_por_cliente(sistema: Sistema) -> None:
    id_cliente = pedir_texto("ID de cliente: ")
    ventas = sistema.ventas.ventas_cliente(id_cliente)
    if not ventas:
        print("El cliente no tiene ventas registradas.")
        return
    for venta in ventas:
        print(f"  {venta.id}: {venta.total} ({'cancelada' if venta.cancelada else 'activa'})")


def _cancelar_venta(sistema: Sistema) -> None:
    venta = sistema.cancelar_ultima_venta()
    print(f"Venta {venta.id} cancelada; stock devuelto.")


def _total_vendido(sistema: Sistema) -> None:
    print(f"Total vendido (sin cancelaciones): {sistema.ventas.total_vendido()}")


def menu_ventas(sistema: Sistema) -> None:
    """Submenú de clientes y ventas."""
    opciones: Opciones = {
        "1": ("Listar clientes", _listar_clientes),
        "2": ("Registrar cliente", _registrar_cliente),
        "3": ("Registrar venta", _registrar_venta),
        "4": ("Listar ventas", _listar_ventas),
        "5": ("Ventas de un cliente", _ventas_por_cliente),
        "6": ("Cancelar última venta (LIFO)", _cancelar_venta),
        "7": ("Total vendido", _total_vendido),
    }
    _submenu("3. Clientes y ventas", opciones, sistema)


# --- Funcionalidad 4: pedidos --------------------------------------------


def _listar_pedidos(sistema: Sistema) -> None:
    pedidos = sistema.pedidos.todos_los_pedidos()
    if not pedidos:
        print("No hay pedidos registrados.")
        return
    for pedido in pedidos:
        print(
            f"  {pedido.id:<10} cliente={pedido.cliente_id:<8} "
            f"destino={pedido.destino:<12} estado={pedido.estado:<12} "
            f"[{_formatear_items(pedido.items)}]"
        )


def _pedidos_pendientes(sistema: Sistema) -> None:
    pedidos = sistema.pedidos.pedidos_pendientes()
    if not pedidos:
        print("La cola de atención está vacía.")
        return
    for pedido in pedidos:
        print(f"  {pedido.id} - {pedido.cliente_id} -> {pedido.destino}")


def _crear_pedido(sistema: Sistema) -> None:
    id_pedido = pedir_texto("ID de pedido: ")
    id_cliente = pedir_texto("ID de cliente: ")
    destino = pedir_texto("Destino (ubicación): ")
    items = _leer_items()
    pedido = sistema.crear_pedido(id_pedido, id_cliente, destino, items)
    print(f"Pedido {pedido.id} encolado con estado {pedido.estado}.")


def _atender_pedido(sistema: Sistema) -> None:
    pedido = sistema.atender_siguiente_pedido()
    print(f"Pedido {pedido.id} en atención; estado: {pedido.estado}.")


def _cambiar_estado(sistema: Sistema) -> None:
    id_pedido = pedir_texto("ID de pedido: ")
    print("Estados: RECIBIDO, PREPARANDO, LISTO, DESPACHADO, CANCELADO")
    estado = pedir_texto("Nuevo estado: ").upper()
    pedido = sistema.cambiar_estado_pedido(id_pedido, estado)
    print(f"Pedido {pedido.id} ahora está {pedido.estado}.")


def _deshacer_cambio(sistema: Sistema) -> None:
    id_pedido = pedir_texto("ID de pedido: ")
    pedido = sistema.deshacer_cambio_pedido(id_pedido)
    print(f"Estado restaurado: {pedido.estado}.")


def _despachar_pedido(sistema: Sistema) -> None:
    id_pedido = pedir_texto("ID de pedido (debe estar LISTO): ")
    id_entrega = pedir_texto("ID de entrega: ")
    entrega = sistema.despachar_pedido(id_pedido, id_entrega)
    print(f"Entrega {entrega.id} registrada. Ruta: {' -> '.join(entrega.ruta)}")


def menu_pedidos(sistema: Sistema) -> None:
    """Submenú de pedidos, atención y estados."""
    opciones: Opciones = {
        "1": ("Listar todos los pedidos", _listar_pedidos),
        "2": ("Ver cola de pendientes", _pedidos_pendientes),
        "3": ("Crear pedido", _crear_pedido),
        "4": ("Atender siguiente (FIFO)", _atender_pedido),
        "5": ("Cambiar estado", _cambiar_estado),
        "6": ("Deshacer último cambio", _deshacer_cambio),
        "7": ("Despachar pedido", _despachar_pedido),
    }
    _submenu("4. Pedidos", opciones, sistema)


# --- Funcionalidad 5: logística ------------------------------------------


def _ver_red(sistema: Sistema) -> None:
    nodos = sistema.logistica.nodos()
    if not nodos:
        print("La red está vacía.")
        return
    for nodo in nodos:
        print(f"  {nodo}: {sistema.logistica.vecinos(nodo)}")


def _ruta_mas_corta(sistema: Sistema) -> None:
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    ruta = sistema.ruta_mas_corta(origen, destino)
    print("Ruta más corta: " + " -> ".join(ruta))


def _rutas_posibles(sistema: Sistema) -> None:
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    rutas = sistema.rutas_posibles(origen, destino)
    if not rutas:
        print("No hay rutas simples entre esos nodos.")
        return
    for ruta in rutas:
        print("  " + " -> ".join(ruta))


def _listar_entregas(sistema: Sistema) -> None:
    entregas = sistema.logistica.listar_entregas()
    if not entregas:
        print("No hay entregas registradas.")
        return
    for entrega in entregas:
        print(
            f"  {entrega.id}: pedido {entrega.pedido_id} | "
            + " -> ".join(entrega.ruta)
        )


def menu_logistica(sistema: Sistema) -> None:
    """Submenú de la red de distribución."""
    opciones: Opciones = {
        "1": ("Ver red (adyacencia)", _ver_red),
        "2": ("Ruta más corta (Dijkstra)", _ruta_mas_corta),
        "3": ("Rutas posibles (DFS recursivo)", _rutas_posibles),
        "4": ("Listar entregas", _listar_entregas),
    }
    _submenu("5. Logística y distribución", opciones, sistema)


# --- Funcionalidad 6: seguimiento ----------------------------------------


def _ultimos_eventos(sistema: Sistema) -> None:
    eventos = sistema.seguimiento.ultimos_eventos(pedir_entero("Cantidad: "))
    for evento in eventos:
        print(
            f"  #{evento.id} {evento.timestamp:%Y-%m-%d %H:%M:%S} "
            f"{evento.tipo:<13} {evento.operacion_id:<10} {evento.descripcion}"
        )


def _eventos_por_tipo(sistema: Sistema) -> None:
    tipo = pedir_texto("Tipo (inventario/venta/pedido/despacho/transferencia): ")
    eventos = sistema.seguimiento.eventos_por_tipo(tipo)
    if not eventos:
        print("No hay eventos de ese tipo.")
        return
    for evento in eventos:
        print(f"  #{evento.id} {evento.operacion_id}: {evento.descripcion}")


def _eventos_entre_fechas(sistema: Sistema) -> None:
    print("Formato: AAAA-MM-DDTHH:MM (UTC), por ejemplo 2026-11-24T10:00")
    desde = datetime.fromisoformat(pedir_texto("Desde: "))
    hasta = datetime.fromisoformat(pedir_texto("Hasta: "))
    if desde.tzinfo is None:
        desde = desde.replace(tzinfo=timezone.utc)
    if hasta.tzinfo is None:
        hasta = hasta.replace(tzinfo=timezone.utc)
    eventos = sistema.seguimiento.eventos_entre(desde, hasta)
    if not eventos:
        print("No hay eventos en ese rango.")
        return
    for evento in eventos:
        print(f"  {evento.timestamp:%Y-%m-%d %H:%M} {evento.tipo}: {evento.descripcion}")


def _resumen_eventos(sistema: Sistema) -> None:
    for tipo, cantidad in sistema.seguimiento.resumen_por_tipo().items():
        print(f"  {tipo:<14} {cantidad}")


def menu_seguimiento(sistema: Sistema) -> None:
    """Submenú del registro de operaciones."""
    opciones: Opciones = {
        "1": ("Últimos eventos", _ultimos_eventos),
        "2": ("Eventos por tipo (índice)", _eventos_por_tipo),
        "3": ("Eventos entre fechas (árbol)", _eventos_entre_fechas),
        "4": ("Resumen por tipo", _resumen_eventos),
    }
    _submenu("6. Seguimiento de operaciones", opciones, sistema)


def run() -> None:
    """Inicia el menú principal con los datos de demostración cargados."""
    sistema = crear_sistema_con_datos()
    print("Bienvenido al sistema de gestión de Los Manguitos (prototipo CLI).")
    print("Se cargaron datos de ejemplo: productos, stock, clientes, ventas y pedidos.")

    while True:
        _titulo("Menú principal")
        print("  1. Productos e inventario")
        print("  2. Bodegas y sucursales")
        print("  3. Clientes y ventas")
        print("  4. Pedidos")
        print("  5. Logística y distribución")
        print("  6. Seguimiento de operaciones")
        print("  7. Recargar datos de ejemplo")
        print("  0. Salir")
        opcion = pedir_texto("Opción: ")

        if opcion == "0":
            print("Hasta pronto.")
            return
        if opcion == "7":
            sistema = crear_sistema_con_datos()
            print("Datos de ejemplo recargados.")
            pausar()
            continue

        menus = {
            "1": menu_productos,
            "2": menu_ubicaciones,
            "3": menu_ventas,
            "4": menu_pedidos,
            "5": menu_logistica,
            "6": menu_seguimiento,
        }
        menu = menus.get(opcion)
        if menu is None:
            print("Opción inválida.")
            pausar()
            continue
        menu(sistema)
