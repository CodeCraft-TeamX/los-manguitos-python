"""Pruebas de la funcionalidad 2: bodegas, sucursales y transferencias."""

import unittest

from src.errores import ErrorDeNegocio, StockInsuficiente, ValidacionError
from src.ubicaciones import GestorUbicaciones


class TestGestorUbicaciones(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorUbicaciones()
        self.gestor.registrar_ubicacion("CENTRAL", "Casa central", "central")
        self.gestor.registrar_ubicacion("SUC-01", "Sucursal Centro", "sucursal")
        self.gestor.ajustar_stock("CENTRAL", "MANG-01", 10)

    def test_stock_por_ubicacion_y_total(self) -> None:
        self.assertEqual(self.gestor.consultar_stock("CENTRAL", "MANG-01"), 10)
        self.assertEqual(self.gestor.consultar_stock("SUC-01", "MANG-01"), 0)
        self.assertEqual(self.gestor.stock_total("MANG-01"), 10)

    def test_stock_negativo_se_rechaza_sin_modificar(self) -> None:
        with self.assertRaises(StockInsuficiente):
            self.gestor.ajustar_stock("CENTRAL", "MANG-01", -11)
        self.assertEqual(self.gestor.consultar_stock("CENTRAL", "MANG-01"), 10)

    def test_transferencias_se_atienden_en_orden_fifo(self) -> None:
        self.gestor.solicitar_transferencia("TR-001", "CENTRAL", "SUC-01", "MANG-01", 3)
        self.gestor.solicitar_transferencia("TR-002", "CENTRAL", "SUC-01", "MANG-01", 4)
        primera = self.gestor.procesar_siguiente_transferencia()
        segunda = self.gestor.procesar_siguiente_transferencia()
        self.assertEqual([primera.id, segunda.id], ["TR-001", "TR-002"])
        self.assertEqual(self.gestor.consultar_stock("CENTRAL", "MANG-01"), 3)
        self.assertEqual(self.gestor.consultar_stock("SUC-01", "MANG-01"), 7)

    def test_solicitud_con_stock_insuficiente_no_se_encola(self) -> None:
        with self.assertRaises(StockInsuficiente):
            self.gestor.solicitar_transferencia("TR-003", "CENTRAL", "SUC-01", "MANG-01", 20)
        self.assertEqual(self.gestor.transferencias_pendientes(), [])

    def test_cola_vacia_y_misma_ubicacion(self) -> None:
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.procesar_siguiente_transferencia()
        with self.assertRaises(ValidacionError):
            self.gestor.solicitar_transferencia("TR-004", "CENTRAL", "CENTRAL", "MANG-01", 1)


if __name__ == "__main__":
    unittest.main()
