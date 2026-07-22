import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO

import mercado
from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
)
from comandos import mostrar_objetivos, mostrar_progreso
from energia import establecer_energia_almacenada, obtener_energia_almacenada
from inventario import inventario, restaurar_inventario
from juego import avanzar_turno, fundir
from maquinas import maquinas, restaurar_maquinas
from mejoras import niveles_maquinas, restaurar_mejoras
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    evaluar_objetivos,
    objetivos_completados,
    obtener_estado_objetivos,
    registrar_extraccion,
    registrar_generacion_energia,
    registrar_produccion,
    restaurar_objetivos,
)


class ObjetivosTests(unittest.TestCase):
    def setUp(self):
        self.estado_original = self._capturar_estado()
        restaurar_inventario({clave: 0 for clave in inventario})
        restaurar_maquinas({
            "mina_hierro": 1,
            "mina_carbon": 1,
            "fundidora": 0,
            "generador_carbon": 1,
        })
        mercado.establecer_saldo(0)
        establecer_energia_almacenada(100)
        desactivar_automatizacion()
        restaurar_mejoras({clave: 1 for clave in niveles_maquinas})
        restaurar_objetivos(ESTADISTICAS_INICIALES, [])

    def tearDown(self):
        self._restaurar_estado(self.estado_original)

    def test_estadisticas_comienzan_en_cero(self):
        self.assertEqual(estadisticas, ESTADISTICAS_INICIALES)

    def test_objetivos_comienzan_pendientes(self):
        self.assertEqual(objetivos_completados, set())
        self.assertTrue(
            all(not objetivo["completado"] for objetivo in obtener_estado_objetivos())
        )

    def test_progreso_acumulativo_de_hierro(self):
        registrar_extraccion(hierro=8)
        registrar_extraccion(hierro=12)

        nuevos = evaluar_objetivos()

        self.assertEqual(estadisticas["hierro_extraido"], 20)
        self.assertIn("extraer_hierro", {objetivo["id"] for objetivo in nuevos})

    def test_consumir_hierro_no_reduce_progreso(self):
        inventario.update({"hierro": 20, "carbon": 1})
        registrar_extraccion(hierro=20)

        fundir(recurso="hierro", cantidad=1, mostrar_mensaje=False)

        self.assertEqual(inventario["hierro"], 19)
        self.assertEqual(estadisticas["hierro_extraido"], 20)

    def test_objetivo_de_fundidora(self):
        maquinas["fundidora"] = 1

        nuevos = evaluar_objetivos()

        self.assertIn(
            "construir_fundidora",
            {objetivo["id"] for objetivo in nuevos},
        )

    def test_objetivo_de_lingotes(self):
        registrar_produccion(lingotes=5)

        evaluar_objetivos()

        self.assertIn("producir_lingotes", objetivos_completados)

    def test_objetivo_de_saldo(self):
        mercado.establecer_saldo(200)

        evaluar_objetivos()

        self.assertIn("alcanzar_saldo", objetivos_completados)

    def test_objetivo_de_mejora(self):
        niveles_maquinas["mina_hierro"] = 2

        evaluar_objetivos()

        self.assertIn("mejorar_maquina", objetivos_completados)

    def test_objetivo_de_energia_generada(self):
        registrar_generacion_energia(30)

        evaluar_objetivos()

        self.assertIn("generar_energia", objetivos_completados)

    def test_objetivo_de_produccion_automatica(self):
        registrar_produccion(lingotes=10, automaticos=10)

        evaluar_objetivos()

        self.assertIn("automatizar_lingotes", objetivos_completados)

    def test_recompensa_se_entrega_una_sola_vez(self):
        registrar_extraccion(hierro=20)

        evaluar_objetivos()
        saldo_tras_recompensa = mercado.obtener_saldo()
        evaluar_objetivos()

        self.assertEqual(saldo_tras_recompensa, 50)
        self.assertEqual(mercado.obtener_saldo(), 50)

    def test_evaluar_dos_veces_no_duplica_objetivo(self):
        registrar_produccion(lingotes=5)

        primera = evaluar_objetivos()
        segunda = evaluar_objetivos()

        self.assertEqual(len(primera), 1)
        self.assertEqual(segunda, [])

    def test_consultas_no_tienen_efectos_secundarios(self):
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()):
            mostrar_objetivos()
            mostrar_progreso()

        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_turnos_se_acumulan(self):
        with redirect_stdout(StringIO()):
            avanzar_turno()
            avanzar_turno()

        self.assertEqual(estadisticas["turnos_completados"], 2)

    def test_reporte_incluye_objetivos_completados(self):
        estadisticas["hierro_extraido"] = 18
        maquinas.update({"mina_carbon": 0, "fundidora": 0})

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        completados = {
            objetivo["id"] for objetivo in reporte["objetivos_completados"]
        }
        self.assertIn("extraer_hierro", completados)

    def test_definiciones_contienen_siete_objetivos(self):
        self.assertEqual(len(OBJETIVOS), 7)

    @staticmethod
    def _capturar_estado():
        return {
            "inventario": deepcopy(inventario),
            "maquinas": deepcopy(maquinas),
            "dinero": mercado.obtener_saldo(),
            "energia": obtener_energia_almacenada(),
            "automatizacion": automatizacion_activa(),
            "niveles": deepcopy(niveles_maquinas),
            "estadisticas": deepcopy(estadisticas),
            "objetivos": set(objetivos_completados),
        }

    @staticmethod
    def _restaurar_estado(estado):
        restaurar_inventario(estado["inventario"])
        restaurar_maquinas(estado["maquinas"])
        mercado.establecer_saldo(estado["dinero"])
        establecer_energia_almacenada(estado["energia"])
        if estado["automatizacion"]:
            activar_automatizacion()
        else:
            desactivar_automatizacion()
        restaurar_mejoras(estado["niveles"])
        restaurar_objetivos(estado["estadisticas"], estado["objetivos"])


if __name__ == "__main__":
    unittest.main()
