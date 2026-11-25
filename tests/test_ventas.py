"""Pruebas de la funcionalidad 3: clientes y ventas."""

import unittest

from src.errores import ErrorDeNegocio, ValidacionError
from src.modelos import Item
from src.ventas import GestorVentas


class TestGestorVentas(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorVentas()
        self.gestor.registrar_cliente("CLI-01", "Juan Pérez", "natural")

    def test_registro_total_e_indice_por_cliente(self) -> None:
        venta = self.gestor.registrar_venta(
            "VEN-001", "CLI-01", [Item("MANG-01", 2, 25000)]
        )
        self.assertEqual(venta.total, 50000)
        self.assertEqual([v.id for v in self.gestor.ventas_cliente("CLI-01")], ["VEN-001"])
        self.assertEqual(self.gestor.total_vendido(), 50000)

    def test_cancelacion_es_lifo_y_mantiene_historial(self) -> None:
        self.gestor.registrar_venta("VEN-001", "CLI-01", [Item("MANG-01", 1, 10)])
        self.gestor.registrar_venta("VEN-002", "CLI-01", [Item("MANG-01", 2, 10)])
        cancelada = self.gestor.cancelar_ultima_venta()
        self.assertEqual(cancelada.id, "VEN-002")
        self.assertTrue(cancelada.cancelada)
        self.assertEqual(self.gestor.total_vendido(), 10)
        self.assertEqual(len(self.gestor.todas_las_ventas()), 2)

    def test_cancelar_sin_ventas_activas(self) -> None:
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.cancelar_ultima_venta()

    def test_venta_vacia_y_precio_invalido(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_venta("VEN-003", "CLI-01", [])
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_venta("VEN-004", "CLI-01", [Item("MANG-01", 1, 0)])


if __name__ == "__main__":
    unittest.main()
