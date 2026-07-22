import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO

from comandos import mostrar_energia, procesar_comando
from energia import (
    calcular_consumo_maximo,
    calcular_generacion,
    distribuir_energia,
    establecer_energia_almacenada,
    obtener_energia_almacenada,
)
from inventario import inventario
from juego import avanzar_turno
from maquinas import construir_maquina, maquinas
from mercado import obtener_saldo


class CalculosEnergiaTests(unittest.TestCase):
    def test_calculo_generacion(self):
        estado = {"generador_carbon": 3}

        self.assertEqual(calcular_generacion(estado), 30)

    def test_calculo_consumo_maximo(self):
        estado = {
            "mina_carbon": 2,
            "mina_hierro": 3,
            "fundidora": 1,
        }

        self.assertEqual(calcular_consumo_maximo(estado), 14)

    def test_activacion_completa_con_energia_suficiente(self):
        estado = {
            "generador_carbon": 1,
            "mina_carbon": 1,
            "mina_hierro": 1,
            "fundidora": 1,
        }

        reporte = distribuir_energia(estado)

        self.assertEqual(reporte["energia_utilizada"], 8)
        self.assertEqual(reporte["energia_restante"], 2)
        self.assertEqual(reporte["maquinas_activas"], {
            "mina_carbon": 1,
            "mina_hierro": 1,
            "fundidora": 1,
        })

    def test_activacion_parcial_respeta_prioridad(self):
        estado = {
            "generador_carbon": 1,
            "mina_carbon": 3,
            "mina_hierro": 3,
            "fundidora": 1,
        }

        reporte = distribuir_energia(estado)

        self.assertEqual(reporte["maquinas_activas"], {
            "mina_carbon": 3,
            "mina_hierro": 2,
            "fundidora": 0,
        })
        self.assertEqual(reporte["maquinas_sin_energia"], {
            "mina_carbon": 0,
            "mina_hierro": 1,
            "fundidora": 1,
        })

    def test_cero_generadores_no_activa_maquinas(self):
        estado = {
            "generador_carbon": 0,
            "mina_carbon": 2,
            "mina_hierro": 1,
            "fundidora": 1,
        }

        reporte = distribuir_energia(estado)

        self.assertEqual(sum(reporte["maquinas_activas"].values()), 0)
        self.assertEqual(reporte["energia_disponible"], 0)


class IntegracionEnergiaTests(unittest.TestCase):
    def setUp(self):
        self.inventario_original = deepcopy(inventario)
        self.maquinas_original = deepcopy(maquinas)
        self.energia_original = obtener_energia_almacenada()
        establecer_energia_almacenada(10)

    def tearDown(self):
        inventario.clear()
        inventario.update(self.inventario_original)
        maquinas.clear()
        maquinas.update(self.maquinas_original)
        establecer_energia_almacenada(self.energia_original)

    def test_maquinas_sin_energia_no_producen(self):
        maquinas.update({
            "generador_carbon": 0,
            "mina_carbon": 2,
            "mina_hierro": 2,
            "fundidora": 2,
        })
        inventario.update({"hierro": 3, "carbon": 3, "lingotes": 0})
        estado_inicial = deepcopy(inventario)
        establecer_energia_almacenada(0)

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(inventario, estado_inicial)
        self.assertEqual(sum(reporte["produccion"].values()), 0)

    def test_turno_solo_produce_con_maquinas_activas(self):
        maquinas.update({
            "generador_carbon": 1,
            "mina_carbon": 3,
            "mina_hierro": 3,
            "fundidora": 1,
        })
        inventario.update({"hierro": 0, "carbon": 0, "lingotes": 0})

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion"], {
            "hierro": 4,
            "carbon": 3,
        })
        self.assertEqual(inventario["hierro"], 4)
        self.assertEqual(inventario["carbon"], 3)

    def test_generar_energia_consume_carbon_y_acumula(self):
        maquinas["generador_carbon"] = 1
        inventario["carbon"] = 2

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("generar energia"))
            self.assertTrue(procesar_comando("generar energia"))

        self.assertEqual(obtener_energia_almacenada(), 30)
        self.assertEqual(inventario["carbon"], 0)

    def test_generar_energia_sin_carbon_no_modifica_estado(self):
        inventario["carbon"] = 0
        energia_inicial = obtener_energia_almacenada()
        maquinas_iniciales = deepcopy(maquinas)

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("generar energia"))

        self.assertEqual(obtener_energia_almacenada(), energia_inicial)
        self.assertEqual(inventario["carbon"], 0)
        self.assertEqual(maquinas, maquinas_iniciales)

    def test_turno_descuenta_energia_utilizada(self):
        maquinas.update({
            "generador_carbon": 1,
            "mina_carbon": 1,
            "mina_hierro": 1,
            "fundidora": 1,
        })

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["energia_utilizada"], 4)
        self.assertEqual(obtener_energia_almacenada(), 6)

    def test_turno_no_funde_automaticamente(self):
        maquinas.update({
            "generador_carbon": 1,
            "mina_carbon": 1,
            "mina_hierro": 1,
            "fundidora": 1,
        })
        inventario.update({"hierro": 0, "carbon": 0, "lingotes": 0})

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertNotIn("lingotes", reporte["produccion"])
        self.assertEqual(inventario["lingotes"], 0)
        self.assertEqual(inventario["hierro"], 2)
        self.assertEqual(inventario["carbon"], 1)

    def test_comando_energia_no_modifica_estado(self):
        estado_inicial = {
            "inventario": deepcopy(inventario),
            "maquinas": deepcopy(maquinas),
            "saldo": obtener_saldo(),
            "energia": obtener_energia_almacenada(),
        }

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("energia"))
            reporte = mostrar_energia(mostrar=False)

        self.assertEqual(inventario, estado_inicial["inventario"])
        self.assertEqual(maquinas, estado_inicial["maquinas"])
        self.assertEqual(obtener_saldo(), estado_inicial["saldo"])
        self.assertEqual(obtener_energia_almacenada(), estado_inicial["energia"])
        self.assertIn("consumo_por_tipo", reporte)

    def test_construccion_generador(self):
        inventario["lingotes"] = 12
        inventario["engranajes"] = 2
        generadores_iniciales = maquinas["generador_carbon"]

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("construir generador carbon"))

        self.assertEqual(
            maquinas["generador_carbon"],
            generadores_iniciales + 1,
        )
        self.assertEqual(inventario["lingotes"], 0)
        self.assertEqual(inventario["engranajes"], 0)

    def test_construccion_sin_recursos_no_modifica_estado(self):
        inventario["lingotes"] = 11
        inventario["engranajes"] = 2
        inventario_inicial = deepcopy(inventario)
        maquinas_iniciales = deepcopy(maquinas)

        resultado = construir_maquina("generador_carbon", mostrar=False)

        self.assertFalse(resultado)
        self.assertEqual(inventario, inventario_inicial)
        self.assertEqual(maquinas, maquinas_iniciales)

    def test_construccion_invalida_no_modifica_estado(self):
        inventario_inicial = deepcopy(inventario)
        maquinas_iniciales = deepcopy(maquinas)

        resultado = construir_maquina("reactor", mostrar=False)

        self.assertFalse(resultado)
        self.assertEqual(inventario, inventario_inicial)
        self.assertEqual(maquinas, maquinas_iniciales)


if __name__ == "__main__":
    unittest.main()
