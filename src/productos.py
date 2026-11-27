"""Funcionalidad 1: catálogo de productos e inventario.

Estructuras: diccionario por SKU, lista de movimientos y árbol de categorías
recorrido con recursividad. El stock efectivo se consulta en ``Ubicaciones``;
aquí se guarda el historial de entradas y salidas.
"""

from __future__ import annotations

from src.errores import NoEncontrado, ValidacionError
from src.modelos import Movimiento, Producto, Proveedor, ahora
from src.utils import entero_requerido, texto_requerido

TIPOS_MOVIMIENTO = ("entrada", "salida")


class GestorProductos:
    """Administra proveedores, productos, movimientos y jerarquía de categorías."""

    def __init__(self) -> None:
        self._proveedores: dict[str, Proveedor] = {}
        self._productos: dict[str, Producto] = {}
        self._movimientos: dict[str, list[Movimiento]] = {}
        self._categorias: dict[str, list[str]] = {}

    def registrar_proveedor(
        self, id_proveedor: str, nombre: str, contacto: str = ""
    ) -> Proveedor:
        """Da de alta un proveedor con identificador único."""
        id_proveedor = texto_requerido(id_proveedor, "ID de proveedor")
        if id_proveedor in self._proveedores:
            raise ValidacionError(f"El proveedor '{id_proveedor}' ya está registrado")
        proveedor = Proveedor(
            id=id_proveedor,
            nombre=texto_requerido(nombre, "Nombre del proveedor"),
            contacto=contacto.strip(),
        )
        self._proveedores[id_proveedor] = proveedor
        return proveedor

    def consultar_proveedor(self, id_proveedor: str) -> Proveedor:
        """Devuelve un proveedor registrado o falla si no existe."""
        try:
            return self._proveedores[id_proveedor]
        except KeyError as exc:
            raise NoEncontrado(f"Proveedor '{id_proveedor}' no encontrado") from exc

    def listar_proveedores(self) -> list[Proveedor]:
        """Devuelve una copia de los proveedores registrados."""
        return list(self._proveedores.values())

    def registrar_categoria(self, nombre: str, padre: str | None = None) -> None:
        """Registra una categoría, opcionalmente debajo de otra."""
        nombre = texto_requerido(nombre, "Categoría")
        if padre is not None:
            padre = texto_requerido(padre, "Categoría padre")
            if padre not in self._categorias:
                raise NoEncontrado(f"Categoría padre '{padre}' no registrada")
        self._categorias.setdefault(nombre, [])
        if padre is not None and nombre not in self._categorias[padre]:
            self._categorias[padre].append(nombre)

    def listar_categorias(self) -> list[str]:
        """Devuelve los nombres de las categorías registradas."""
        return list(self._categorias)

    def registrar_producto(
        self, sku: str, nombre: str, categoria: str, proveedor_id: str
    ) -> Producto:
        """Da de alta un producto; el SKU es único y valida categoría y proveedor."""
        sku = texto_requerido(sku, "SKU")
        if sku in self._productos:
            raise ValidacionError(f"El producto '{sku}' ya está registrado")
        categoria = texto_requerido(categoria, "Categoría")
        if categoria not in self._categorias:
            raise NoEncontrado(f"Categoría '{categoria}' no registrada")
        proveedor_id = texto_requerido(proveedor_id, "Proveedor")
        self.consultar_proveedor(proveedor_id)
        producto = Producto(
            sku=sku,
            nombre=texto_requerido(nombre, "Nombre"),
            categoria=categoria,
            proveedor_id=proveedor_id,
        )
        self._productos[sku] = producto
        self._movimientos[sku] = []
        return producto

    def consultar_producto(self, sku: str) -> Producto:
        """Devuelve un producto por SKU o falla si no existe."""
        try:
            return self._productos[sku]
        except KeyError as exc:
            raise NoEncontrado(f"Producto '{sku}' no encontrado") from exc

    def listar_productos(self) -> list[Producto]:
        """Devuelve una copia del catálogo en orden de alta."""
        return list(self._productos.values())

    def registrar_movimiento(
        self, sku: str, tipo: str, cantidad: int, descripcion: str = ""
    ) -> Movimiento:
        """Agrega una entrada/salida al historial del producto."""
        self.consultar_producto(sku)
        if tipo not in TIPOS_MOVIMIENTO:
            raise ValidacionError(f"Tipo de movimiento inválido: '{tipo}'")
        movimiento = Movimiento(
            sku=sku,
            tipo=tipo,
            cantidad=entero_requerido(cantidad, "Cantidad"),
            timestamp=ahora(),
            descripcion=descripcion,
        )
        self._movimientos[sku].append(movimiento)
        return movimiento

    def movimientos(self, sku: str) -> list[Movimiento]:
        """Historial cronológico de movimientos de un producto."""
        self.consultar_producto(sku)
        return list(self._movimientos[sku])

    def listar_categoria(self, categoria: str) -> list[Producto]:
        """Lista productos de una categoría y de todas sus subcategorías."""
        categoria = texto_requerido(categoria, "Categoría")
        if categoria not in self._categorias:
            raise NoEncontrado(f"Categoría '{categoria}' no registrada")
        nombres = self._nombres_del_arbol(categoria, set())
        return [p for p in self._productos.values() if p.categoria in nombres]

    def _nombres_del_arbol(self, categoria: str, visitados: set[str]) -> set[str]:
        """Recorrido recursivo del árbol de categorías con protección de ciclos."""
        if categoria in visitados:
            return set()
        visitados.add(categoria)
        nombres = {categoria}
        for hijo in self._categorias.get(categoria, []):
            nombres |= self._nombres_del_arbol(hijo, visitados)
        return nombres
