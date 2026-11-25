"""Pruebas de la funcionalidad 6: registro de operaciones."""

import unittest
from datetime import datetime, timedelta, timezone

from src.errores import ValidacionError
from src.seguimiento import RegistroOperaciones


class TestRegistroOperaciones(unittest.TestCase):
    def setUp(self) -> None:
        self.registro = RegistroOperaciones()

    def test_indice_por_tipo(self) -> None:
        self.registro.registrar_evento("inventario", "MANG-01", "Entrada")
        self.registro.registrar_evento("venta", "VEN-001", "Venta")
        self.assertEqual(len(self.registro.eventos_por_tipo("inventario")), 1)
        self.assertEqual(self.registro.eventos_por_tipo("despacho"), [])
        self.assertEqual(self.registro.resumen_por_tipo()["venta"], 1)

    def test_rango_temporal_usa_abb(self) -> None:
        antes = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.registro.registrar_evento("pedido", "PED-001", "Pedido creado")
        despues = datetime.now(timezone.utc) + timedelta(seconds=1)
        self.assertEqual(len(self.registro.eventos_entre(antes, despues)), 1)
        self.assertEqual(self.registro.eventos_entre(despues, despues + timedelta(days=1)), [])

    def test_rango_invertido_y_tipo_invalido(self) -> None:
        ahora = datetime.now(timezone.utc)
        with self.assertRaises(ValidacionError):
            self.registro.eventos_entre(ahora, ahora - timedelta(days=1))
        with self.assertRaises(ValidacionError):
            self.registro.registrar_evento("otro", "X", "Descripción")

    def test_log_vacio(self) -> None:
        self.assertEqual(self.registro.ultimos_eventos(), [])
        self.assertEqual(self.registro.todos_los_eventos(), [])


if __name__ == "__main__":
    unittest.main()
