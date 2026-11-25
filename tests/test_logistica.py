"""Pruebas de la funcionalidad 5: grafo logístico y rutas."""

import unittest

from src.errores import ErrorDeNegocio, ValidacionError
from src.logistica import RedLogistica


class TestRedLogistica(unittest.TestCase):
    def setUp(self) -> None:
        self.red = RedLogistica()
        for nodo in ("CENTRAL", "BODEGA-NORTE", "BODEGA-SUR", "SUC-01", "SUC-02"):
            self.red.agregar_nodo(nodo)
        for origen, destino, distancia in (
            ("CENTRAL", "BODEGA-NORTE", 12),
            ("CENTRAL", "BODEGA-SUR", 8),
            ("BODEGA-NORTE", "SUC-01", 7),
            ("BODEGA-SUR", "SUC-02", 9),
            ("BODEGA-NORTE", "SUC-02", 15),
        ):
            self.red.agregar_conexion(origen, destino, distancia)

    def test_ruta_mas_corta(self) -> None:
        self.assertEqual(
            self.red.ruta_mas_corta("CENTRAL", "SUC-02"),
            ["CENTRAL", "BODEGA-SUR", "SUC-02"],
        )

    def test_rutas_posibles_con_recursividad(self) -> None:
        rutas = self.red.rutas_posibles("CENTRAL", "SUC-01")
        self.assertTrue(rutas)
        self.assertIn(["CENTRAL", "BODEGA-NORTE", "SUC-01"], rutas)
        self.assertTrue(all(ruta[-1] == "SUC-01" for ruta in rutas))
        self.assertTrue(all(len(set(ruta)) == len(ruta) for ruta in rutas))

    def test_sin_ruta_y_nodo_inexistente(self) -> None:
        self.red.agregar_nodo("AISLADO")
        with self.assertRaises(ErrorDeNegocio):
            self.red.ruta_mas_corta("CENTRAL", "AISLADO")
        with self.assertRaises(ErrorDeNegocio):
            self.red.vecinos("NO-EXISTE")

    def test_distancia_invalida(self) -> None:
        with self.assertRaises(ValidacionError):
            self.red.agregar_conexion("CENTRAL", "SUC-01", 0)


if __name__ == "__main__":
    unittest.main()
