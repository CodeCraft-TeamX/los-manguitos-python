"""Pruebas de la funcionalidad 3: clientes y ventas."""

import unittest

from src.errores import ErrorDeNegocio, ValidacionError
from src.modelos import Item
from src.ventas import GestorVentas


class TestGestorVentas(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorVentas()
        self.gestor.registrar_cliente("CLI-01", "Mercado La Ceiba", "frecuente")

    def test_registro_total_e_indice_por_cliente(self) -> None:
        venta = self.gestor.registrar_venta(
            "V-2026-0843",
            "CLI-01",
            [Item("PR-001", 2, 2.40), Item("PR-024", 3, 1.50)],
        )
        self.assertEqual(venta.total, 9.3)
        self.assertEqual([v.id for v in self.gestor.ventas_cliente("CLI-01")], ["V-2026-0843"])
        self.assertEqual(self.gestor.total_vendido(), 9.3)

    def test_cancelacion_es_lifo_y_mantiene_historial(self) -> None:
        self.gestor.registrar_venta("V-2026-0841", "CLI-01", [Item("PR-001", 1, 2.40)])
        self.gestor.registrar_venta("V-2026-0842", "CLI-01", [Item("PR-001", 2, 2.40)])
        cancelada = self.gestor.cancelar_ultima_venta()
        self.assertEqual(cancelada.id, "V-2026-0842")
        self.assertTrue(cancelada.cancelada)
        self.assertEqual(self.gestor.total_vendido(), 2.4)
        self.assertEqual(len(self.gestor.todas_las_ventas()), 2)

    def test_cancelar_sin_ventas_activas(self) -> None:
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.cancelar_ultima_venta()

    def test_venta_vacia_y_precio_invalido(self) -> None:
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_venta("V-2026-0844", "CLI-01", [])
        with self.assertRaises(ValidacionError):
            self.gestor.registrar_venta("V-2026-0845", "CLI-01", [Item("PR-001", 1, 0)])


if __name__ == "__main__":
    unittest.main()
