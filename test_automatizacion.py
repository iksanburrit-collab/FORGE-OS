import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest.mock import patch

import mercado
from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
)
from comandos import mostrar_automatizacion, mostrar_energia, procesar_comando
from energia import establecer_energia_almacenada, obtener_energia_almacenada
from inventario import inventario
from juego import avanzar_turno, fundir
from maquinas import maquinas
from recetas import RECETAS


class AutomatizacionTests(unittest.TestCase):
    def setUp(self):
        self.inventario_original = deepcopy(inventario)
        self.maquinas_original = deepcopy(maquinas)
        self.energia_original = obtener_energia_almacenada()
        self.dinero_original = mercado.dinero
        self.automatizacion_original = automatizacion_activa()

        inventario.update({
            "hierro": 0,
            "carbon": 0,
            "lingotes": 0,
            "engranajes": 0,
            "placas": 0,
        })
        maquinas.update({
            "mina_hierro": 1,
            "mina_carbon": 1,
            "fundidora": 1,
            "generador_carbon": 1,
        })
        establecer_energia_almacenada(10)
        mercado.dinero = 0
        desactivar_automatizacion()

    def tearDown(self):
        inventario.clear()
        inventario.update(self.inventario_original)
        maquinas.clear()
        maquinas.update(self.maquinas_original)
        establecer_energia_almacenada(self.energia_original)
        mercado.dinero = self.dinero_original
        if self.automatizacion_original:
            activar_automatizacion()
        else:
            desactivar_automatizacion()

    def test_automatizacion_desactivada_por_defecto(self):
        self.assertFalse(automatizacion_activa())

    def test_activar_automatizacion(self):
        reporte = activar_automatizacion()

        self.assertTrue(reporte["activa"])
        self.assertTrue(reporte["cambio"])
        self.assertTrue(automatizacion_activa())

    def test_desactivar_automatizacion(self):
        activar_automatizacion()

        reporte = desactivar_automatizacion()

        self.assertFalse(reporte["activa"])
        self.assertTrue(reporte["cambio"])

    def test_activar_dos_veces_es_seguro(self):
        primer_reporte = activar_automatizacion()
        segundo_reporte = activar_automatizacion()

        self.assertTrue(primer_reporte["cambio"])
        self.assertFalse(segundo_reporte["cambio"])
        self.assertTrue(automatizacion_activa())

    def test_comando_con_tilde_activa_automatizacion(self):
        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("automatización activar"))

        self.assertTrue(automatizacion_activa())

    def test_consulta_no_modifica_estado(self):
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("automatización"))
            reporte = mostrar_automatizacion(mostrar=False)

        self.assertEqual(self._capturar_estado(), estado_inicial)
        self.assertEqual(reporte["fundidoras_construidas"], 1)
        self.assertEqual(reporte["fundidoras_energizables"], 0)

    def test_desactivada_fundidoras_no_reservan_energia(self):
        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["maquinas_activas"]["fundidora"], 0)
        self.assertEqual(reporte["energia_utilizada"], 4)
        self.assertEqual(obtener_energia_almacenada(), 6)

    def test_activa_fundidoras_reciben_energia(self):
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["maquinas_activas"]["fundidora"], 1)
        self.assertEqual(reporte["energia_utilizada"], 8)
        self.assertEqual(obtener_energia_almacenada(), 2)

    def test_asignacion_no_modifica_diccionario_global_de_maquinas(self):
        maquinas_iniciales = deepcopy(maquinas)

        with redirect_stdout(StringIO()):
            avanzar_turno()

        self.assertEqual(maquinas, maquinas_iniciales)

    def test_minas_aprovechan_energia_sin_reserva_de_fundidoras(self):
        maquinas.update({
            "mina_carbon": 2,
            "mina_hierro": 2,
            "fundidora": 3,
        })
        establecer_energia_almacenada(8)

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["maquinas_activas"]["mina_carbon"], 2)
        self.assertEqual(reporte["maquinas_activas"]["mina_hierro"], 2)
        self.assertEqual(reporte["maquinas_activas"]["fundidora"], 0)
        self.assertEqual(reporte["produccion"], {"hierro": 4, "carbon": 2})

    def test_consulta_energia_muestra_consumo_potencial_y_efectivo(self):
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()):
            reporte = mostrar_energia()

        self.assertEqual(reporte["consumo_potencial"], 8)
        self.assertEqual(reporte["consumo_efectivo"], 4)
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_desactivada_no_produce_lingotes(self):
        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(inventario["lingotes"], 0)
        self.assertFalse(reporte["automatizacion_activa"])
        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 0)

    def test_activa_produce_con_recursos_suficientes(self):
        inventario.update({"hierro": 1, "carbon": 1})
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 1)
        self.assertEqual(inventario["lingotes"], 1)

    def test_produccion_limitada_por_fundidoras_energizadas(self):
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 3})
        inventario.update({"hierro": 10, "carbon": 10})
        establecer_energia_almacenada(4)
        maquinas_iniciales = deepcopy(maquinas)
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["maquinas_activas"]["fundidora"], 1)
        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 1)
        self.assertEqual(maquinas, maquinas_iniciales)

    def test_fundidoras_sin_energia_no_producen(self):
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 2})
        inventario.update({"hierro": 10, "carbon": 10})
        establecer_energia_almacenada(0)
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 0)
        self.assertEqual(inventario["lingotes"], 0)

    def test_produccion_limitada_por_hierro(self):
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 3})
        inventario.update({"hierro": 1, "carbon": 10})
        establecer_energia_almacenada(12)
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 1)

    def test_produccion_limitada_por_carbon(self):
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 3})
        inventario.update({"hierro": 10, "carbon": 1})
        establecer_energia_almacenada(12)
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 1)

    def test_usa_recursos_extraidos_en_el_mismo_turno(self):
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            avanzar_turno()

        self.assertEqual(inventario["lingotes"], 1)
        self.assertEqual(inventario["hierro"], 1)
        self.assertEqual(inventario["carbon"], 0)

    def test_fundicion_automatica_usa_receta_actual(self):
        receta_temporal = {
            "consume": {"hierro": 2, "carbon": 1},
            "produce": {"lingotes": 3},
        }
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 1})
        inventario.update({"hierro": 2, "carbon": 1})
        establecer_energia_almacenada(4)
        activar_automatizacion()

        with patch.dict(RECETAS, {"lingote": receta_temporal}):
            with redirect_stdout(StringIO()):
                reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 3)
        self.assertEqual(inventario["hierro"], 0)
        self.assertEqual(inventario["carbon"], 0)

    def test_fundicion_manual_sigue_funcionando(self):
        inventario.update({"hierro": 1, "carbon": 1})
        activar_automatizacion()

        resultado = fundir(
            recurso="hierro",
            cantidad=1,
            mostrar_mensaje=False,
        )

        self.assertEqual(resultado, 1)
        self.assertEqual(inventario["lingotes"], 1)

    def test_reporte_contiene_produccion_automatica(self):
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertIn("produccion_automatica", reporte)
        self.assertIn("automatizacion_activa", reporte)
        self.assertIn("maquinas_activas", reporte)
        self.assertIn("maquinas_sin_energia", reporte)

    def test_comando_invalido_conserva_estado(self):
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("automatizacion iniciar"))

        self.assertEqual(self._capturar_estado(), estado_inicial)

    @staticmethod
    def _capturar_estado():
        return {
            "inventario": deepcopy(inventario),
            "maquinas": deepcopy(maquinas),
            "energia": obtener_energia_almacenada(),
            "dinero": mercado.dinero,
            "automatizacion": automatizacion_activa(),
        }


if __name__ == "__main__":
    unittest.main()
