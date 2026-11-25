"""Prueba mínima de arranque del prototipo."""

import contextlib
import io
import unittest
from unittest.mock import patch

from main import main


class TestArranque(unittest.TestCase):
    def test_entrypoint_imprime_nombre_del_sistema(self) -> None:
        salida = io.StringIO()
        with patch("builtins.input", return_value="0"), contextlib.redirect_stdout(salida):
            main()
        self.assertIn("Los Manguitos", salida.getvalue())
        self.assertIn("Hasta pronto", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
