"""Pruebas de la funcionalidad 1: productos e inventario."""

import unittest

from src.errores import NoEncontrado, ValidacionError
from src.productos import GestorProductos


class TestGestorProductos(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorProductos()
        self.gestor.registrar_categoria("Indumentaria")
        self.gestor.registrar_categoria("Mangas", "Indumentaria")
        self.gestor.registrar_categoria("Térmicas", "Mangas")
        self.gestor.registrar_producto("MANG-01", "Manga térmica", "Térmicas", "PROV-01")
        self.gestor.registrar_producto("MANG-02", "Manga clásica", "Mangas", "PROV-01")

    def test_alta_y_consulta_por_sku(self) -> None:
        producto = self.gestor.consultar_producto("MANG-01")
        self.assertEqual(producto.nombre, "Manga térmica")
        self.assertEqual(len(self.gestor.listar_productos()), 2)

    def test_sku_duplicado_se_rechaza(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_producto("MANG-01", "Otro", "Mangas", "PROV-02")

    def test_movimientos_son_cronologicos_y_no_se_pierden(self) -> None:
        self.gestor.registrar_movimiento("MANG-01", "entrada", 10)
        self.gestor.registrar_movimiento("MANG-01", "salida", 3)
        movimientos = self.gestor.movimientos("MANG-01")
        self.assertEqual([m.tipo for m in movimientos], ["entrada", "salida"])
        self.assertLessEqual(movimientos[0].timestamp, movimientos[1].timestamp)

    def test_listado_recursivo_de_categoria(self) -> None:
        productos = self.gestor.listar_categoria("Indumentaria")
        self.assertEqual({p.sku for p in productos}, {"MANG-01", "MANG-02"})
        self.assertEqual(len(self.gestor.listar_categoria("Térmicas")), 1)

    def test_cantidad_invalida_y_producto_inexistente(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_movimiento("MANG-01", "entrada", 0)
        with self.assertRaises(NoEncontrado):
            self.gestor.consultar_producto("NO-EXISTE")

    def test_categoria_inexistente(self) -> None:
        with self.assertRaises(NoEncontrado):
            self.gestor.listar_categoria("Inexistente")


if __name__ == "__main__":
    unittest.main()
