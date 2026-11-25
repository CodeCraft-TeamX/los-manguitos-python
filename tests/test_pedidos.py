"""Pruebas de la funcionalidad 4: pedidos y estados."""

import unittest

from src.errores import ErrorDeNegocio, TransicionInvalida
from src.modelos import Item
from src.pedidos import GestorPedidos


class TestGestorPedidos(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorPedidos()
        self.gestor.crear_pedido("PED-001", "CLI-01", "SUC-01", [Item("MANG-01", 1, 10)])
        self.gestor.crear_pedido("PED-002", "CLI-02", "SUC-02", [Item("GUAN-01", 2, 10)])

    def test_atencion_fifo_y_estado_inicial(self) -> None:
        pedido = self.gestor.atender_siguiente()
        self.assertEqual(pedido.id, "PED-001")
        self.assertEqual(pedido.estado, "PREPARANDO")
        self.assertEqual([p.id for p in self.gestor.pedidos_pendientes()], ["PED-002"])
        self.assertEqual(self.gestor.consultar_estado("PED-002"), "RECIBIDO")

    def test_transicion_invalida(self) -> None:
        with self.assertRaises(TransicionInvalida):
            self.gestor.cambiar_estado("PED-001", "DESPACHADO")

    def test_deshacer_ultimo_cambio_usa_pila(self) -> None:
        self.gestor.atender_siguiente()
        self.gestor.cambiar_estado("PED-001", "LISTO")
        self.assertEqual(self.gestor.consultar_estado("PED-001"), "LISTO")
        self.gestor.deshacer_ultimo_cambio("PED-001")
        self.assertEqual(self.gestor.consultar_estado("PED-001"), "PREPARANDO")

    def test_cola_vacia_y_sin_historial(self) -> None:
        self.gestor.atender_siguiente()
        self.gestor.atender_siguiente()
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.atender_siguiente()
        self.gestor.deshacer_ultimo_cambio("PED-001")
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.deshacer_ultimo_cambio("PED-001")


if __name__ == "__main__":
    unittest.main()
