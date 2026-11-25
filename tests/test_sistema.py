"""Pruebas de integración entre los módulos a través de ``Sistema``."""

import unittest

from src.errores import StockInsuficiente, TransicionInvalida
from src.modelos import Item
from src.datos import crear_sistema_con_datos


class TestSistema(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = crear_sistema_con_datos()

    def test_datos_demo_cargan_stock_y_eventos(self) -> None:
        self.assertEqual(self.sistema.consultar_stock_total("MANG-01"), 56)
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "MANG-01"), 38)
        self.assertEqual(len(self.sistema.seguimiento.todos_los_eventos()), 6)

    def test_venta_atomica_rechaza_stock_insuficiente(self) -> None:
        with self.assertRaises(StockInsuficiente):
            self.sistema.registrar_venta("VEN-100", "CLI-01", [Item("MANG-01", 999, 1)])
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "MANG-01"), 38)
        self.assertEqual(len(self.sistema.ventas.todas_las_ventas()), 2)

    def test_cancelar_venta_devuelve_stock(self) -> None:
        self.sistema.cancelar_ultima_venta()
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "GUAN-01"), 15)
        self.assertEqual(self.sistema.ventas.total_vendido(), 50000)

    def test_transferencia_fifo_mueve_stock(self) -> None:
        self.sistema.procesar_siguiente_transferencia()
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "MANG-01"), 33)
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("SUC-02", "MANG-01"), 5)

    def test_despacho_completo_de_pedido(self) -> None:
        self.sistema.atender_siguiente_pedido()
        self.sistema.cambiar_estado_pedido("PED-001", "LISTO")
        entrega = self.sistema.despachar_pedido("PED-001", "ENT-001")
        self.assertEqual(entrega.ruta, ("CENTRAL", "BODEGA-NORTE", "SUC-01"))
        self.assertEqual(self.sistema.pedidos.consultar_estado("PED-001"), "DESPACHADO")
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "MANG-01"), 36)
        self.assertEqual(len(self.sistema.seguimiento.eventos_por_tipo("despacho")), 1)

    def test_no_se_puede_despachar_pedido_recibido(self) -> None:
        with self.assertRaises(TransicionInvalida):
            self.sistema.despachar_pedido("PED-001", "ENT-002")


if __name__ == "__main__":
    unittest.main()
