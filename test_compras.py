import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import patch

import mercado
from comandos import procesar_comando
from inventario import inventario
from maquinas import maquinas
from mercado import comprar
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    objetivos_completados,
    restaurar_objetivos,
)


class ComprasTests(unittest.TestCase):
    def setUp(self):
        self.inventario_original = deepcopy(inventario)
        self.maquinas_original = deepcopy(maquinas)
        self.dinero_original = mercado.dinero
        self.estadisticas_originales = deepcopy(estadisticas)
        self.objetivos_originales = set(objetivos_completados)
        mercado.dinero = 0
        restaurar_objetivos(ESTADISTICAS_INICIALES, OBJETIVOS)

    def tearDown(self):
        inventario.clear()
        inventario.update(self.inventario_original)
        maquinas.clear()
        maquinas.update(self.maquinas_original)
        mercado.dinero = self.dinero_original
        restaurar_objetivos(
            self.estadisticas_originales,
            self.objetivos_originales,
        )

    def test_comprar_material(self):
        mercado.dinero = 20
        hierro_inicial = inventario["hierro"]

        gastado = comprar("hierro", 2, mostrar_mensaje=False)

        self.assertEqual(gastado, 10)
        self.assertEqual(inventario["hierro"], hierro_inicial + 2)
        self.assertEqual(mercado.obtener_saldo(), 10)

    def test_comprar_maquina(self):
        mercado.dinero = 100
        minas_iniciales = maquinas["mina_carbon"]

        gastado = comprar("mina_carbon", mostrar_mensaje=False)

        self.assertEqual(gastado, 80)
        self.assertEqual(maquinas["mina_carbon"], minas_iniciales + 1)
        self.assertEqual(mercado.obtener_saldo(), 20)

    def test_compra_sin_saldo_no_modifica_estado(self):
        mercado.dinero = 4
        inventario_inicial = deepcopy(inventario)
        maquinas_iniciales = deepcopy(maquinas)

        resultado = comprar("hierro", mostrar_mensaje=False)

        self.assertEqual(resultado, 0)
        self.assertEqual(mercado.obtener_saldo(), 4)
        self.assertEqual(inventario, inventario_inicial)
        self.assertEqual(maquinas, maquinas_iniciales)

    def test_compra_invalida_no_modifica_estado(self):
        mercado.dinero = 500
        estado_inicial = (
            deepcopy(inventario),
            deepcopy(maquinas),
            mercado.obtener_saldo(),
        )

        self.assertEqual(comprar("reactor", mostrar_mensaje=False), 0)
        self.assertEqual(comprar("hierro", 0, mostrar_mensaje=False), 0)

        self.assertEqual(
            (inventario, maquinas, mercado.obtener_saldo()),
            estado_inicial,
        )

    def test_comando_comprar_abre_menu_y_compra(self):
        mercado.dinero = 100
        minas_iniciales = maquinas["mina_carbon"]

        with patch("builtins.input", side_effect=["6", "1"]):
            with redirect_stdout(StringIO()) as salida:
                self.assertTrue(procesar_comando("comprar"))

        self.assertIn("TIENDA", salida.getvalue())
        self.assertEqual(maquinas["mina_carbon"], minas_iniciales + 1)
        self.assertEqual(mercado.obtener_saldo(), 20)

    def test_cancelar_menu_no_modifica_estado(self):
        mercado.dinero = 100
        estado_inicial = (
            deepcopy(inventario),
            deepcopy(maquinas),
            mercado.obtener_saldo(),
        )

        with patch("builtins.input", return_value="0"):
            with redirect_stdout(StringIO()):
                self.assertTrue(procesar_comando("comprar"))

        self.assertEqual(
            (inventario, maquinas, mercado.obtener_saldo()),
            estado_inicial,
        )


if __name__ == "__main__":
    unittest.main()
