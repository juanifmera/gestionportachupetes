import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.join(os.path.dirname(__file__), "..", "sistema_portachupetes")
sys.path.insert(0, os.path.abspath(ROOT))

from crud.pedidos import obtener_materiales_mayorista, obtener_materiales_utilizados


class MaterialesPedidoTest(unittest.TestCase):
    @patch(
        "crud.pedidos.verificar_confeccion_portachupetes",
        return_value={"success": True, "faltantes": [], "detalles": []},
    )
    def test_minorista_agrupa_y_normaliza(self, _):
        resultado = dict(obtener_materiales_utilizados({
            "broche": " sbla ",
            "nombre": "Ana María",
            "dijes_normales": [{"codigo": "025"}],
            "bolitas": [
                {"codigo": "bbla12", "cantidad": 2},
                {"codigo": "BBLA12", "cantidad": 3},
            ],
        }))
        self.assertEqual(resultado["SBLA"], 1)
        self.assertEqual(resultado["A"], 4)
        self.assertEqual(resultado["N"], 1)
        self.assertEqual(resultado["M"], 1)
        self.assertEqual(resultado["R"], 1)
        self.assertEqual(resultado["I"], 1)
        self.assertEqual(resultado["BBLA12"], 5)

    def test_mayorista_agrupa_codigos_repetidos(self):
        resultado = dict(obtener_materiales_mayorista({
            "bolitas": [
                {"codigo": "bros09", "cantidad": 4},
                {"codigo": " BROS09 ", "cantidad": 2},
            ],
            "letras": [{"codigo": "A", "cantidad": 5}],
        }))
        self.assertEqual(resultado, {"BROS09": 6, "A": 5})


if __name__ == "__main__":
    unittest.main()
