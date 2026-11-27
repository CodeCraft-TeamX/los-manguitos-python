"""Pruebas de la funcionalidad 5: grafo logístico y rutas."""

import unittest

from src.errores import ErrorDeNegocio, ValidacionError
from src.logistica import RedLogistica


class TestRedLogistica(unittest.TestCase):
    def setUp(self) -> None:
        self.red = RedLogistica()
        for nodo in ("CENTRAL", "SUC-CENTRO", "SUC-SANTA-ANA", "SUC-SAN-MIGUEL", "PUERTO-LA-LIBERTAD"):
            self.red.agregar_nodo(nodo)
        for origen, destino, distancia in (
            ("CENTRAL", "SUC-CENTRO", 12),
            ("CENTRAL", "SUC-SANTA-ANA", 26),
            ("CENTRAL", "SUC-SAN-MIGUEL", 48),
            ("CENTRAL", "PUERTO-LA-LIBERTAD", 18),
            ("SUC-CENTRO", "PUERTO-LA-LIBERTAD", 14),
        ):
            self.red.agregar_conexion(origen, destino, distancia)

    def test_ruta_mas_corta(self) -> None:
        self.assertEqual(
            self.red.ruta_mas_corta("CENTRAL", "PUERTO-LA-LIBERTAD"),
            ["CENTRAL", "PUERTO-LA-LIBERTAD"],
        )

    def test_rutas_posibles_con_recursividad(self) -> None:
        rutas = self.red.rutas_posibles("CENTRAL", "PUERTO-LA-LIBERTAD")
        self.assertTrue(rutas)
        self.assertIn(["CENTRAL", "PUERTO-LA-LIBERTAD"], rutas)
        self.assertIn(["CENTRAL", "SUC-CENTRO", "PUERTO-LA-LIBERTAD"], rutas)
        self.assertTrue(all(ruta[-1] == "PUERTO-LA-LIBERTAD" for ruta in rutas))
        self.assertTrue(all(len(set(ruta)) == len(ruta) for ruta in rutas))

    def test_sin_ruta_y_nodo_inexistente(self) -> None:
        self.red.agregar_nodo("AISLADO")
        with self.assertRaises(ErrorDeNegocio):
            self.red.ruta_mas_corta("CENTRAL", "AISLADO")
        with self.assertRaises(ErrorDeNegocio):
            self.red.vecinos("NO-EXISTE")

    def test_distancia_invalida(self) -> None:
        with self.assertRaises(ValidacionError):
            self.red.agregar_conexion("CENTRAL", "SUC-CENTRO", 0)


if __name__ == "__main__":
    unittest.main()
