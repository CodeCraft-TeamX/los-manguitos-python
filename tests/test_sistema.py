"""Pruebas de integración entre los módulos a través de ``Sistema``."""

import unittest

from src.errores import StockInsuficiente, TransicionInvalida
from src.modelos import Item
from src.datos import crear_sistema_con_datos


class TestSistema(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = crear_sistema_con_datos()

    def test_datos_demo_cargan_stock_y_eventos(self) -> None:
        self.assertEqual(self.sistema.consultar_stock_total("PR-001"), 12)
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-001"), 12)
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-024"), 16)
        self.assertEqual(len(self.sistema.seguimiento.todos_los_eventos()), 6)

    def test_registrar_proveedor_y_producto(self) -> None:
        self.sistema.registrar_proveedor("PROV-03", "Agro El Sol", "7000-0000")
        producto = self.sistema.registrar_producto(
            "PR-099", "Mango Panadés", "Frutas frescas", "PROV-03", "CENTRAL", 10
        )
        self.assertEqual(producto.proveedor_id, "PROV-03")
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-099"), 10)

    def test_venta_atomica_rechaza_stock_insuficiente(self) -> None:
        with self.assertRaises(StockInsuficiente):
            self.sistema.registrar_venta("V-2026-0999", "CLI-01", [Item("PR-001", 999, 2.40)])
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-001"), 12)
        self.assertEqual(len(self.sistema.ventas.todas_las_ventas()), 2)

    def test_cancelar_venta_devuelve_stock_a_su_ubicacion(self) -> None:
        self.sistema.registrar_venta(
            "V-2026-0843", "CLI-01", [Item("PR-008", 2, 3.20)], ubicacion="SUC-CENTRO"
        )
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("SUC-CENTRO", "PR-008"), 6)
        self.sistema.cancelar_ultima_venta()
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("SUC-CENTRO", "PR-008"), 8)
        self.assertAlmostEqual(self.sistema.ventas.total_vendido(), 17.50)

    def test_transferencia_fifo_mueve_stock(self) -> None:
        self.sistema.procesar_siguiente_transferencia()
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-008"), 0)
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("SUC-SANTA-ANA", "PR-008"), 24)

    def test_despacho_completo_de_pedido(self) -> None:
        self.sistema.atender_siguiente_pedido()
        self.sistema.cambiar_estado_pedido("P-2026-311", "PREPARANDO")
        self.sistema.cambiar_estado_pedido("P-2026-311", "LISTO")
        entrega = self.sistema.despachar_pedido("P-2026-311", "ENT-001")
        self.assertEqual(entrega.ruta, ("CENTRAL", "SUC-SANTA-ANA"))
        self.assertEqual(self.sistema.pedidos.consultar_estado("P-2026-311"), "DESPACHADO")
        self.assertEqual(self.sistema.ubicaciones.consultar_stock("CENTRAL", "PR-001"), 7)
        self.assertEqual(len(self.sistema.seguimiento.eventos_por_tipo("despacho")), 1)

    def test_no_se_puede_despachar_pedido_nuevo(self) -> None:
        with self.assertRaises(TransicionInvalida):
            self.sistema.despachar_pedido("P-2026-311", "ENT-002")


if __name__ == "__main__":
    unittest.main()
