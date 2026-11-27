"""Interfaz de línea de comandos del prototipo de Los Manguitos.

Usa ``rich`` para paneles, colores, negrita y tablas. El menú solo presenta
datos y captura entradas; la lógica de negocio vive en ``Sistema``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.datos import crear_sistema_con_datos
from src.errores import ErrorDeNegocio, ValidacionError
from src.modelos import Item
from src.sistema import Sistema
from src.utils import entero_requerido

Opciones = dict[str, tuple[str, Callable[[Sistema], None]]]
consola = Console(highlight=False)


# --- Ayudas de presentación y entrada ------------------------------------


def _decir(texto: str, estilo: str = "") -> None:
    """Imprime texto con estilo Rich, sin interpretar corchetes como markup."""
    consola.print(texto, style=estilo or None, markup=False)


def _pedir_texto(mensaje: str) -> str:
    """Muestra una etiqueta en azul y lee una línea del operador."""
    consola.print(Text(mensaje, style="bold blue"), end="")
    return input().strip()


def _pedir_entero(mensaje: str, minimo: int = 1) -> int:
    """Pide un entero válido, repitiendo la pregunta si hace falta."""
    while True:
        valor = _pedir_texto(mensaje)
        try:
            return entero_requerido(int(valor), "Valor", minimo)
        except (ValueError, ValidacionError):
            _decir("Ingrese un número entero válido.", "bold red")


def _pausar() -> None:
    """Espera a que el operador presione Enter antes de seguir."""
    consola.print(Text("\nPresione Enter para continuar...", style="dim"), end="")
    input()


def _titulo(texto: str) -> None:
    """Encabezado con panel cian."""
    consola.print()
    consola.print(
        Panel(
            Text(texto, style="bold cyan"),
            border_style="bright_cyan",
            expand=False,
        )
    )


def _tabla(*columnas: str) -> Table:
    """Crea una tabla ligera con encabezados en magenta."""
    tabla = Table(box=None, show_header=True, header_style="bold magenta", pad_edge=False)
    for columna in columnas:
        tabla.add_column(columna)
    return tabla


def _formatear_items(items: list[Item]) -> str:
    """Representa los ítems de una venta o pedido en una sola línea."""
    return ", ".join(f"{i.cantidad} x {i.sku} (@{i.precio_unitario})" for i in items)


def _leer_items() -> list[Item]:
    """Pide ítems como 'SKU,Cantidad,Precio'; línea vacía termina."""
    items: list[Item] = []
    _decir("Ítems (formato: SKU,Cantidad,Precio). Línea vacía para terminar:", "dim")
    while True:
        linea = _pedir_texto("  > ")
        if not linea:
            break
        partes = [parte.strip() for parte in linea.split(",")]
        if len(partes) != 3:
            _decir("  Formato inválido. Ejemplo: PR-001,2,2.40", "bold red")
            continue
        try:
            items.append(Item(partes[0], int(partes[1]), float(partes[2])))
        except ValueError:
            _decir("  Cantidad debe ser entero y precio numérico.", "bold red")
    return items


def _mostrar_opciones(opciones: Opciones, incluir_volver: bool = True) -> None:
    """Muestra las opciones de un submenú como una tabla."""
    tabla = Table(box=None, show_header=False, pad_edge=False)
    tabla.add_column(style="bold yellow", width=4)
    tabla.add_column()
    for clave, (etiqueta, _) in opciones.items():
        tabla.add_row(Text(clave), Text(etiqueta))
    if incluir_volver:
        tabla.add_row(Text("0"), Text("Volver al menú principal"))
    consola.print(tabla)


def _submenu(titulo: str, opciones: Opciones, sistema: Sistema) -> None:
    """Muestra un submenú y despacha la acción elegida."""
    while True:
        _titulo(titulo)
        _mostrar_opciones(opciones)
        opcion = _pedir_texto("Opción: ")
        if opcion == "0":
            return
        accion = opciones.get(opcion)
        if accion is None:
            _decir("Opción inválida.", "bold red")
            _pausar()
            continue
        try:
            accion[1](sistema)
        except ErrorDeNegocio as exc:
            consola.print(
                Panel(
                    Text(f"Error: {exc}", style="bold red"),
                    title="Atención",
                    border_style="red",
                    expand=False,
                )
            )
        _pausar()


# --- Funcionalidad 1: productos e inventario -----------------------------


def _listar_productos(sistema: Sistema) -> None:
    productos = sistema.productos.listar_productos()
    if not productos:
        _decir("No hay productos registrados.", "italic yellow")
        return
    tabla = _tabla("SKU", "Nombre", "Categoría", "Proveedor")
    for producto in productos:
        tabla.add_row(
            Text(producto.sku, style="bold yellow"),
            Text(producto.nombre),
            Text(producto.categoria, style="cyan"),
            Text(producto.proveedor_id),
        )
    consola.print(tabla)


def _consultar_producto(sistema: Sistema) -> None:
    sku = _pedir_texto("SKU: ")
    producto = sistema.productos.consultar_producto(sku)
    _decir(str(producto), "bold")
    _decir(f"Stock total: {sistema.consultar_stock_total(sku)}", "bold green")
    _decir(f"Stock por ubicación: {sistema.ubicaciones.stock_por_ubicacion(sku)}")


def _listar_categoria(sistema: Sistema) -> None:
    categoria = _pedir_texto("Categoría (incluye subcategorías): ")
    productos = sistema.productos.listar_categoria(categoria)
    if not productos:
        _decir("No hay productos en esa categoría.", "italic yellow")
        return
    tabla = _tabla("SKU", "Nombre", "Categoría")
    for producto in productos:
        tabla.add_row(
            Text(producto.sku, style="bold yellow"),
            Text(producto.nombre),
            Text(producto.categoria, style="cyan"),
        )
    consola.print(tabla)


def _registrar_entrada(sistema: Sistema) -> None:
    sku = _pedir_texto("SKU: ")
    cantidad = _pedir_entero("Cantidad: ")
    ubicacion = _pedir_texto("Ubicación: ")
    stock = sistema.registrar_entrada(sku, cantidad, ubicacion)
    _decir(f"Entrada registrada. Stock ahora en {ubicacion}: {stock}", "bold green")


def _registrar_salida(sistema: Sistema) -> None:
    sku = _pedir_texto("SKU: ")
    cantidad = _pedir_entero("Cantidad: ")
    ubicacion = _pedir_texto("Ubicación: ")
    stock = sistema.registrar_salida(sku, cantidad, ubicacion)
    _decir(f"Salida registrada. Stock ahora en {ubicacion}: {stock}", "bold green")


def _ver_movimientos(sistema: Sistema) -> None:
    sku = _pedir_texto("SKU: ")
    movimientos = sistema.productos.movimientos(sku)
    if not movimientos:
        _decir("El producto no tiene movimientos registrados.", "italic yellow")
        return
    tabla = _tabla("Fecha", "Tipo", "Cantidad", "Descripción")
    for movimiento in movimientos:
        estilo = "green" if movimiento.tipo == "entrada" else "red"
        tabla.add_row(
            Text(f"{movimiento.timestamp:%Y-%m-%d %H:%M}"),
            Text(movimiento.tipo, style=f"bold {estilo}"),
            Text(str(movimiento.cantidad)),
            Text(movimiento.descripcion),
        )
    consola.print(tabla)


def _registrar_producto(sistema: Sistema) -> None:
    sku = _pedir_texto("SKU (ej. PR-040): ")
    nombre = _pedir_texto("Nombre: ")
    _decir(f"Categorías: {', '.join(sistema.productos.listar_categorias())}", "dim")
    categoria = _pedir_texto("Categoría: ")
    _decir(
        "Proveedores: "
        + ", ".join(f"{p.id} ({p.nombre})" for p in sistema.productos.listar_proveedores()),
        "dim",
    )
    proveedor_id = _pedir_texto("ID de proveedor: ")
    ubicacion = _pedir_texto("Ubicación inicial (Enter = sin stock inicial): ")
    stock_inicial = _pedir_entero("Stock inicial: ", minimo=0) if ubicacion else 0
    producto = sistema.registrar_producto(
        sku,
        nombre,
        categoria,
        proveedor_id,
        ubicacion=ubicacion or None,
        stock_inicial=stock_inicial,
    )
    _decir(f"Producto {producto.sku} ({producto.nombre}) registrado.", "bold green")


def _registrar_categoria(sistema: Sistema) -> None:
    nombre = _pedir_texto("Nombre de categoría: ")
    padre = _pedir_texto("Categoría padre (Enter = raíz): ") or None
    sistema.productos.registrar_categoria(nombre, padre)
    _decir(f"Categoría '{nombre}' registrada.", "bold green")


def menu_productos(sistema: Sistema) -> None:
    """Submenú de productos, categorías y movimientos."""
    opciones: Opciones = {
        "1": ("Listar productos", _listar_productos),
        "2": ("Consultar producto y stock", _consultar_producto),
        "3": ("Listar categoría (recursivo)", _listar_categoria),
        "4": ("Registrar entrada", _registrar_entrada),
        "5": ("Registrar salida", _registrar_salida),
        "6": ("Ver movimientos de un producto", _ver_movimientos),
        "7": ("Registrar producto", _registrar_producto),
        "8": ("Registrar categoría", _registrar_categoria),
    }
    _submenu("1. Productos e inventario", opciones, sistema)


def _listar_proveedores(sistema: Sistema) -> None:
    proveedores = sistema.productos.listar_proveedores()
    if not proveedores:
        _decir("No hay proveedores registrados.", "italic yellow")
        return
    tabla = _tabla("ID", "Nombre", "Contacto")
    for proveedor in proveedores:
        tabla.add_row(
            Text(proveedor.id, style="bold yellow"),
            Text(proveedor.nombre),
            Text(proveedor.contacto or "—", style="cyan"),
        )
    consola.print(tabla)


def _registrar_proveedor(sistema: Sistema) -> None:
    id_proveedor = _pedir_texto("ID de proveedor (ej. PROV-03): ")
    nombre = _pedir_texto("Nombre: ")
    contacto = _pedir_texto("Teléfono o contacto: ")
    proveedor = sistema.registrar_proveedor(id_proveedor, nombre, contacto)
    _decir(f"Proveedor {proveedor.id} ({proveedor.nombre}) registrado.", "bold green")


def menu_proveedores(sistema: Sistema) -> None:
    """Submenú de administración de proveedores."""
    opciones: Opciones = {
        "1": ("Listar proveedores", _listar_proveedores),
        "2": ("Registrar proveedor", _registrar_proveedor),
    }
    _submenu("7. Proveedores", opciones, sistema)


# --- Funcionalidad 2: bodegas y sucursales -------------------------------


def _listar_ubicaciones(sistema: Sistema) -> None:
    ubicaciones = sistema.ubicaciones.listar_ubicaciones()
    if not ubicaciones:
        _decir("No hay ubicaciones registradas.", "italic yellow")
        return
    tabla = _tabla("ID", "Nombre", "Tipo")
    for ubicacion in ubicaciones:
        tabla.add_row(
            Text(ubicacion.id, style="bold yellow"),
            Text(ubicacion.nombre),
            Text(ubicacion.tipo, style="cyan"),
        )
    consola.print(tabla)


def _consultar_stock(sistema: Sistema) -> None:
    ubicacion = _pedir_texto("Ubicación: ")
    sku = _pedir_texto("SKU: ")
    cantidad = sistema.ubicaciones.consultar_stock(ubicacion, sku)
    _decir(f"{sku} en {ubicacion}: {cantidad} unidades", "bold green")


def _solicitar_transferencia(sistema: Sistema) -> None:
    id_transferencia = _pedir_texto("ID de transferencia: ")
    origen = _pedir_texto("Origen: ")
    destino = _pedir_texto("Destino: ")
    sku = _pedir_texto("SKU: ")
    cantidad = _pedir_entero("Cantidad: ")
    sistema.solicitar_transferencia(id_transferencia, origen, destino, sku, cantidad)
    _decir(f"Transferencia {id_transferencia} encolada.", "bold green")


def _procesar_transferencia(sistema: Sistema) -> None:
    transferencia = sistema.procesar_siguiente_transferencia()
    _decir(
        f"Transferencia {transferencia.id}: {transferencia.cantidad} x "
        f"{transferencia.sku} de {transferencia.origen} a {transferencia.destino}",
        "bold green",
    )


def _ver_transferencias(sistema: Sistema) -> None:
    pendientes = sistema.ubicaciones.transferencias_pendientes()
    if not pendientes:
        _decir("No hay transferencias pendientes.", "italic yellow")
        return
    tabla = _tabla("ID", "Origen", "Destino", "Producto", "Cantidad")
    for transferencia in pendientes:
        tabla.add_row(
            Text(transferencia.id, style="bold yellow"),
            Text(transferencia.origen),
            Text(transferencia.destino),
            Text(transferencia.sku, style="cyan"),
            Text(str(transferencia.cantidad)),
        )
    consola.print(tabla)


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
        _decir("No hay clientes registrados.", "italic yellow")
        return
    tabla = _tabla("ID", "Nombre", "Tipo")
    for cliente in clientes:
        tabla.add_row(
            Text(cliente.id, style="bold yellow"),
            Text(cliente.nombre),
            Text(cliente.tipo, style="cyan"),
        )
    consola.print(tabla)


def _registrar_cliente(sistema: Sistema) -> None:
    id_cliente = _pedir_texto("ID de cliente: ")
    nombre = _pedir_texto("Nombre: ")
    tipo = _pedir_texto("Tipo (natural/empresa): ")
    sistema.ventas.registrar_cliente(id_cliente, nombre, tipo)
    _decir(f"Cliente {id_cliente} registrado.", "bold green")


def _registrar_venta(sistema: Sistema) -> None:
    id_venta = _pedir_texto("ID de venta: ")
    id_cliente = _pedir_texto("ID de cliente: ")
    ubicacion = _pedir_texto("Ubicación de venta (Enter = CENTRAL): ") or "CENTRAL"
    items = _leer_items()
    venta = sistema.registrar_venta(id_venta, id_cliente, items, ubicacion=ubicacion)
    _decir(f"Venta {venta.id} registrada por ${venta.total:.2f}.", "bold green")


def _listar_ventas(sistema: Sistema) -> None:
    ventas = sistema.ventas.todas_las_ventas()
    if not ventas:
        _decir("No hay ventas registradas.", "italic yellow")
        return
    tabla = _tabla("ID", "Cliente", "Total", "Estado", "Ítems")
    for venta in ventas:
        estado = "CANCELADA" if venta.cancelada else "ACTIVA"
        estilo = "bold red" if venta.cancelada else "bold green"
        tabla.add_row(
            Text(venta.id, style="bold yellow"),
            Text(venta.cliente_id),
            Text(f"${venta.total:.2f}"),
            Text(estado, style=estilo),
            Text(_formatear_items(venta.items)),
        )
    consola.print(tabla)


def _ventas_por_cliente(sistema: Sistema) -> None:
    id_cliente = _pedir_texto("ID de cliente: ")
    ventas = sistema.ventas.ventas_cliente(id_cliente)
    if not ventas:
        _decir("El cliente no tiene ventas registradas.", "italic yellow")
        return
    tabla = _tabla("ID", "Total", "Estado")
    for venta in ventas:
        tabla.add_row(
            Text(venta.id, style="bold yellow"),
            Text(str(venta.total)),
            Text("cancelada" if venta.cancelada else "activa",
                 style="red" if venta.cancelada else "green"),
        )
    consola.print(tabla)


def _cancelar_venta(sistema: Sistema) -> None:
    venta = sistema.cancelar_ultima_venta()
    _decir(f"Venta {venta.id} cancelada; stock devuelto.", "bold green")


def _total_vendido(sistema: Sistema) -> None:
    _decir(f"Total vendido (sin cancelaciones): ${sistema.ventas.total_vendido():.2f}", "bold green")


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
        _decir("No hay pedidos registrados.", "italic yellow")
        return
    tabla = _tabla("ID", "Cliente", "Destino", "Estado", "Ítems")
    for pedido in pedidos:
        estados = {
            "NUEVO": "yellow",
            "CONFIRMADO": "blue",
            "PREPARANDO": "cyan",
            "LISTO": "green",
            "DESPACHADO": "bold green",
            "CANCELADO": "bold red",
        }
        tabla.add_row(
            Text(pedido.id, style="bold yellow"),
            Text(pedido.cliente_id),
            Text(pedido.destino),
            Text(pedido.estado, style=estados.get(pedido.estado, "")),
            Text(_formatear_items(pedido.items)),
        )
    consola.print(tabla)


def _pedidos_pendientes(sistema: Sistema) -> None:
    pedidos = sistema.pedidos.pedidos_pendientes()
    if not pedidos:
        _decir("La cola de atención está vacía.", "italic yellow")
        return
    tabla = _tabla("ID", "Cliente", "Destino")
    for pedido in pedidos:
        tabla.add_row(
            Text(pedido.id, style="bold yellow"),
            Text(pedido.cliente_id),
            Text(pedido.destino),
        )
    consola.print(tabla)


def _crear_pedido(sistema: Sistema) -> None:
    id_pedido = _pedir_texto("ID de pedido: ")
    id_cliente = _pedir_texto("ID de cliente: ")
    destino = _pedir_texto("Destino (ubicación): ")
    items = _leer_items()
    pedido = sistema.crear_pedido(id_pedido, id_cliente, destino, items)
    _decir(f"Pedido {pedido.id} encolado con estado {pedido.estado}.", "bold green")


def _atender_pedido(sistema: Sistema) -> None:
    pedido = sistema.atender_siguiente_pedido()
    _decir(f"Pedido {pedido.id} en atención; estado: {pedido.estado}", "bold green")


def _cambiar_estado(sistema: Sistema) -> None:
    id_pedido = _pedir_texto("ID de pedido: ")
    _decir("Estados: NUEVO, CONFIRMADO, PREPARANDO, LISTO, DESPACHADO, CANCELADO", "dim")
    estado = _pedir_texto("Nuevo estado: ").upper()
    pedido = sistema.cambiar_estado_pedido(id_pedido, estado)
    _decir(f"Pedido {pedido.id} ahora está {pedido.estado}.", "bold green")


def _deshacer_cambio(sistema: Sistema) -> None:
    id_pedido = _pedir_texto("ID de pedido: ")
    pedido = sistema.deshacer_cambio_pedido(id_pedido)
    _decir(f"Estado restaurado: {pedido.estado}.", "bold yellow")


def _despachar_pedido(sistema: Sistema) -> None:
    id_pedido = _pedir_texto("ID de pedido (debe estar LISTO): ")
    id_entrega = _pedir_texto("ID de entrega: ")
    entrega = sistema.despachar_pedido(id_pedido, id_entrega)
    _decir(
        f"Entrega {entrega.id} registrada. Ruta: {' -> '.join(entrega.ruta)}",
        "bold green",
    )


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
        _decir("La red está vacía.", "italic yellow")
        return
    tabla = _tabla("Nodo", "Vecinos (distancia)")
    for nodo in nodos:
        tabla.add_row(
            Text(nodo, style="bold yellow"),
            Text(str(sistema.logistica.vecinos(nodo))),
        )
    consola.print(tabla)


def _ruta_mas_corta(sistema: Sistema) -> None:
    origen = _pedir_texto("Origen: ")
    destino = _pedir_texto("Destino: ")
    ruta = sistema.ruta_mas_corta(origen, destino)
    _decir("Ruta más corta: " + " -> ".join(ruta), "bold green")


def _rutas_posibles(sistema: Sistema) -> None:
    origen = _pedir_texto("Origen: ")
    destino = _pedir_texto("Destino: ")
    rutas = sistema.rutas_posibles(origen, destino)
    if not rutas:
        _decir("No hay rutas simples entre esos nodos.", "italic yellow")
        return
    for ruta in rutas:
        _decir("  " + " -> ".join(ruta), "cyan")


def _listar_entregas(sistema: Sistema) -> None:
    entregas = sistema.logistica.listar_entregas()
    if not entregas:
        _decir("No hay entregas registradas.", "italic yellow")
        return
    tabla = _tabla("ID", "Pedido", "Ruta")
    for entrega in entregas:
        tabla.add_row(
            Text(entrega.id, style="bold yellow"),
            Text(entrega.pedido_id),
            Text(" -> ".join(entrega.ruta), style="green"),
        )
    consola.print(tabla)


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
    eventos = sistema.seguimiento.ultimos_eventos(_pedir_entero("Cantidad: "))
    if not eventos:
        _decir("No hay eventos registrados.", "italic yellow")
        return
    tabla = _tabla("#", "Fecha", "Tipo", "Operación", "Descripción")
    for evento in eventos:
        tabla.add_row(
            Text(str(evento.id)),
            Text(f"{evento.timestamp:%Y-%m-%d %H:%M:%S}"),
            Text(evento.tipo, style="cyan"),
            Text(evento.operacion_id, style="bold yellow"),
            Text(evento.descripcion),
        )
    consola.print(tabla)


def _eventos_por_tipo(sistema: Sistema) -> None:
    tipo = _pedir_texto("Tipo (inventario/venta/pedido/despacho/transferencia): ")
    eventos = sistema.seguimiento.eventos_por_tipo(tipo)
    if not eventos:
        _decir("No hay eventos de ese tipo.", "italic yellow")
        return
    tabla = _tabla("#", "Operación", "Descripción")
    for evento in eventos:
        tabla.add_row(
            Text(str(evento.id)),
            Text(evento.operacion_id, style="bold yellow"),
            Text(evento.descripcion),
        )
    consola.print(tabla)


def _eventos_entre_fechas(sistema: Sistema) -> None:
    _decir("Formato: AAAA-MM-DDTHH:MM (UTC), por ejemplo 2026-11-26T10:00", "dim")
    try:
        desde = datetime.fromisoformat(_pedir_texto("Desde: "))
        hasta = datetime.fromisoformat(_pedir_texto("Hasta: "))
    except ValueError:
        _decir("Formato de fecha inválido. Use AAAA-MM-DDTHH:MM.", "bold red")
        return
    if desde.tzinfo is None:
        desde = desde.replace(tzinfo=timezone.utc)
    if hasta.tzinfo is None:
        hasta = hasta.replace(tzinfo=timezone.utc)
    eventos = sistema.seguimiento.eventos_entre(desde, hasta)
    if not eventos:
        _decir("No hay eventos en ese rango.", "italic yellow")
        return
    tabla = _tabla("Fecha", "Tipo", "Descripción")
    for evento in eventos:
        tabla.add_row(
            Text(f"{evento.timestamp:%Y-%m-%d %H:%M}"),
            Text(evento.tipo, style="cyan"),
            Text(evento.descripcion),
        )
    consola.print(tabla)


def _resumen_eventos(sistema: Sistema) -> None:
    tabla = _tabla("Tipo", "Eventos")
    for tipo, cantidad in sistema.seguimiento.resumen_por_tipo().items():
        tabla.add_row(Text(tipo, style="cyan"), Text(str(cantidad), style="bold"))
    consola.print(tabla)


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
    consola.print(
        Panel(
            Text("Los Manguitos", style="bold white"),
            title="Sistema integral de gestión",
            subtitle="Prototipo CLI",
            border_style="blue",
            expand=False,
        )
    )
    _decir("Se cargaron datos de ejemplo: productos, stock, clientes, ventas y pedidos.", "dim")

    while True:
        _titulo("Menú principal")
        tabla = _tabla("Opción", "Módulo")
        modulos = (
            ("1", "Productos e inventario"),
            ("2", "Bodegas y sucursales"),
            ("3", "Clientes y ventas"),
            ("4", "Pedidos"),
            ("5", "Logística y distribución"),
            ("6", "Seguimiento de operaciones"),
            ("7", "Proveedores"),
            ("8", "Recargar datos de ejemplo"),
            ("0", "Salir"),
        )
        for clave, etiqueta in modulos:
            tabla.add_row(Text(clave, style="bold yellow"), Text(etiqueta))
        consola.print(tabla)
        opcion = _pedir_texto("Opción: ")

        if opcion == "0":
            _decir("Hasta pronto.", "bold green")
            return
        if opcion == "8":
            sistema = crear_sistema_con_datos()
            _decir("Datos de ejemplo recargados.", "bold green")
            _pausar()
            continue

        menus = {
            "1": menu_productos,
            "2": menu_ubicaciones,
            "3": menu_ventas,
            "4": menu_pedidos,
            "5": menu_logistica,
            "6": menu_seguimiento,
            "7": menu_proveedores,
        }
        menu = menus.get(opcion)
        if menu is None:
            _decir("Opción inválida.", "bold red")
            _pausar()
            continue
        menu(sistema)
