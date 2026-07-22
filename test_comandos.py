import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import patch

from comandos import procesar_comando
from inventario import inventario
from juego import fabricar, fundir
from main import iniciar_juego
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    objetivos_completados,
    restaurar_objetivos,
)


class ValidacionRecetasTests(unittest.TestCase):
    def setUp(self):
        self.inventario_original = deepcopy(inventario)
        self.estadisticas_originales = deepcopy(estadisticas)
        self.objetivos_originales = set(objetivos_completados)
        restaurar_objetivos(ESTADISTICAS_INICIALES, OBJETIVOS)

    def tearDown(self):
        inventario.clear()
        inventario.update(self.inventario_original)
        restaurar_objetivos(
            self.estadisticas_originales,
            self.objetivos_originales,
        )

    def test_arranque_y_salida(self):
        salida = StringIO()
        guardado = {"ok": True, "mensaje": "Guardada."}
        with patch("builtins.input", return_value="salir"):
            with patch("comandos.guardar_partida", return_value=guardado):
                with redirect_stdout(salida):
                    iniciar_juego()

        self.assertIn("FORGE OS", salida.getvalue())
        self.assertIn("Saliendo del juego", salida.getvalue())

    def test_fabricar_producto_valido(self):
        inventario["lingotes"] = 3

        self.assertEqual(fabricar("engranajes", mostrar_mensaje=False), 1)
        self.assertEqual(inventario["lingotes"], 0)
        self.assertEqual(inventario["engranajes"], 1)

    def test_fabricar_producto_invalido_no_cambia_inventario(self):
        estado_inicial = deepcopy(inventario)

        salida = StringIO()
        with redirect_stdout(salida):
            resultado = fabricar("tornillos")

        self.assertEqual(resultado, 0)
        self.assertEqual(inventario, estado_inicial)
        self.assertIn("No existe una receta", salida.getvalue())

    def test_fundir_recurso_valido(self):
        inventario["hierro"] = 1
        inventario["carbon"] = 1

        self.assertEqual(
            fundir(recurso="hierro", cantidad=1, mostrar_mensaje=False),
            1,
        )
        self.assertEqual(inventario["hierro"], 0)
        self.assertEqual(inventario["carbon"], 0)
        self.assertEqual(inventario["lingotes"], 1)

    def test_fundir_producto_invalido_no_cambia_inventario(self):
        inventario["hierro"] = 5
        inventario["carbon"] = 5
        estado_inicial = deepcopy(inventario)

        salida = StringIO()
        with redirect_stdout(salida):
            resultado = fundir(recurso="placas", cantidad=1)

        self.assertEqual(resultado, 0)
        self.assertEqual(inventario, estado_inicial)
        self.assertIn("No existe una receta de fundición", salida.getvalue())

    def test_comando_invalido_no_cambia_inventario(self):
        inventario["hierro"] = 5
        inventario["carbon"] = 5
        estado_inicial = deepcopy(inventario)

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("fabricar 1 tornillos"))
            self.assertTrue(procesar_comando("fundir 1 placas"))

        self.assertEqual(inventario, estado_inicial)

    def test_comandos_validos_fundir_y_fabricar(self):
        inventario["hierro"] = 3
        inventario["carbon"] = 3

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("fundir 3 hierro"))
            self.assertTrue(procesar_comando("fabricar 1 engranajes"))

        self.assertEqual(inventario["hierro"], 0)
        self.assertEqual(inventario["carbon"], 0)
        self.assertEqual(inventario["lingotes"], 0)
        self.assertEqual(inventario["engranajes"], 1)


if __name__ == "__main__":
    unittest.main()
