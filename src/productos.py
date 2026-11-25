"""Funcionalidad 1: catálogo de productos e inventario.

Estructuras: diccionario por SKU, lista de movimientos y árbol de categorías
recorrido con recursividad. El stock efectivo se consulta en ``Ubicaciones``;
aquí se guarda el historial de entradas y salidas.
"""

from __future__ import annotations

from src.errores import NoEncontrado, ValidacionError
from src.modelos import Movimiento, Producto, ahora
from src.utils import entero_requerido, texto_requerido

TIPOS_MOVIMIENTO = ("entrada", "salida")


class GestorProductos:
    """Administra productos, movimientos y la jerarquía de categorías."""

    def __init__(self) -> None:
        self._productos: dict[str, Producto] = {}
        self._movimientos: dict[str, list[Movimiento]] = {}
        self._categorias: dict[str, list[str]] = {}

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

    def registrar_producto(
        self, sku: str, nombre: str, categoria: str, proveedor_id: str
    ) -> Producto:
        """Da de alta un producto; el SKU es único."""
        sku = texto_requerido(sku, "SKU")
        if sku in self._productos:
            raise ValidacionError(f"El producto '{sku}' ya está registrado")
        categoria = texto_requerido(categoria, "Categoría")
        if categoria not in self._categorias:
            raise NoEncontrado(f"Categoría '{categoria}' no registrada")
        producto = Producto(
            sku=sku,
            nombre=texto_requerido(nombre, "Nombre"),
            categoria=categoria,
            proveedor_id=texto_requerido(proveedor_id, "Proveedor"),
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
