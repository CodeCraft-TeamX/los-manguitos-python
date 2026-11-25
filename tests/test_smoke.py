"""Prueba mínima de arranque del prototipo."""

import contextlib
import io
import unittest

from main import main


class TestArranque(unittest.TestCase):
    def test_entrypoint_imprime_nombre_del_sistema(self) -> None:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            main()
        self.assertIn("Los Manguitos", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
