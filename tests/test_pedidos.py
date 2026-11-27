"""Pruebas de la funcionalidad 4: pedidos y estados."""

import unittest

from src.errores import ErrorDeNegocio, TransicionInvalida
from src.modelos import Item
from src.pedidos import GestorPedidos


class TestGestorPedidos(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorPedidos()
        self.gestor.crear_pedido("P-2026-311", "CLI-01", "SUC-CENTRO", [Item("PR-001", 1, 2.40)])
        self.gestor.crear_pedido("P-2026-312", "CLI-02", "SUC-SANTA-ANA", [Item("PR-024", 2, 1.50)])

    def test_atencion_fifo_y_estado_inicial(self) -> None:
        pedido = self.gestor.atender_siguiente()
        self.assertEqual(pedido.id, "P-2026-311")
        self.assertEqual(pedido.estado, "CONFIRMADO")
        self.assertEqual([p.id for p in self.gestor.pedidos_pendientes()], ["P-2026-312"])
        self.assertEqual(self.gestor.consultar_estado("P-2026-312"), "NUEVO")

    def test_transicion_invalida(self) -> None:
        with self.assertRaises(TransicionInvalida):
            self.gestor.cambiar_estado("P-2026-311", "DESPACHADO")

    def test_deshacer_ultimo_cambio_usa_pila(self) -> None:
        self.gestor.atender_siguiente()
        self.gestor.cambiar_estado("P-2026-311", "PREPARANDO")
        self.assertEqual(self.gestor.consultar_estado("P-2026-311"), "PREPARANDO")
        self.gestor.deshacer_ultimo_cambio("P-2026-311")
        self.assertEqual(self.gestor.consultar_estado("P-2026-311"), "CONFIRMADO")

    def test_cola_vacia_y_sin_historial(self) -> None:
        self.gestor.atender_siguiente()
        self.gestor.atender_siguiente()
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.atender_siguiente()
        self.gestor.deshacer_ultimo_cambio("P-2026-311")
        with self.assertRaises(ErrorDeNegocio):
            self.gestor.deshacer_ultimo_cambio("P-2026-311")


if __name__ == "__main__":
    unittest.main()
