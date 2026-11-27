"""Pruebas de la funcionalidad 1: productos e inventario."""

import unittest

from src.errores import NoEncontrado, ValidacionError
from src.productos import GestorProductos


class TestGestorProductos(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorProductos()
        self.gestor.registrar_proveedor("PROV-01", "Finca El Paraíso", "7890-1122")
        self.gestor.registrar_categoria("Frutas frescas")
        self.gestor.registrar_categoria("Cítricos", "Frutas frescas")
        self.gestor.registrar_categoria("Procesados")
        self.gestor.registrar_producto("PR-001", "Mango Tommy", "Frutas frescas", "PROV-01")
        self.gestor.registrar_producto("PR-008", "Limón pérsico", "Cítricos", "PROV-01")

    def test_alta_y_consulta_por_sku(self) -> None:
        producto = self.gestor.consultar_producto("PR-001")
        self.assertEqual(producto.nombre, "Mango Tommy")
        self.assertEqual(len(self.gestor.listar_productos()), 2)

    def test_sku_duplicado_y_proveedor_inexistente_se_rechazan(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_producto("PR-001", "Otro", "Cítricos", "PROV-01")
        with self.assertRaises(NoEncontrado):
            self.gestor.registrar_producto("PR-099", "Otro", "Cítricos", "PROV-999")

    def test_movimientos_son_cronologicos_y_no_se_pierden(self) -> None:
        self.gestor.registrar_movimiento("PR-001", "entrada", 10)
        self.gestor.registrar_movimiento("PR-001", "salida", 3)
        movimientos = self.gestor.movimientos("PR-001")
        self.assertEqual([m.tipo for m in movimientos], ["entrada", "salida"])
        self.assertLessEqual(movimientos[0].timestamp, movimientos[1].timestamp)

    def test_listado_recursivo_de_categoria(self) -> None:
        productos = self.gestor.listar_categoria("Frutas frescas")
        self.assertEqual({p.sku for p in productos}, {"PR-001", "PR-008"})
        self.assertEqual(len(self.gestor.listar_categoria("Cítricos")), 1)

    def test_cantidad_invalida_y_producto_inexistente(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_movimiento("PR-001", "entrada", 0)
        with self.assertRaises(NoEncontrado):
            self.gestor.consultar_producto("NO-EXISTE")

    def test_categoria_inexistente(self) -> None:
        with self.assertRaises(NoEncontrado):
            self.gestor.listar_categoria("Inexistente")


if __name__ == "__main__":
    unittest.main()
