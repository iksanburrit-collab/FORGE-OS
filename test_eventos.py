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
from energia import establecer_energia_almacenada, obtener_energia_almacenada
from eventos import procesar_evento
from inventario import inventario, restaurar_inventario
from juego import avanzar_turno
from maquinas import maquinas, restaurar_maquinas
from mejoras import niveles_maquinas, restaurar_mejoras
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    objetivos_completados,
    restaurar_objetivos,
)


class EventosTests(unittest.TestCase):
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
        restaurar_objetivos(ESTADISTICAS_INICIALES, OBJETIVOS)

    def tearDown(self):
        self._restaurar_estado(self.estado_original)

    def test_evento_solo_cada_cinco_turnos(self):
        for _ in range(4):
            with redirect_stdout(StringIO()):
                reporte = avanzar_turno(evento_id="hallazgo_hierro")
            self.assertIsNone(reporte["evento"])

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno(evento_id="hallazgo_hierro")

        self.assertEqual(reporte["evento"]["id"], "hallazgo_hierro")

    def test_hallazgo_de_hierro(self):
        reporte = procesar_evento("hallazgo_hierro")

        self.assertTrue(reporte["ok"])
        self.assertEqual(inventario["hierro"], 3)

    def test_subsidio_energetico(self):
        establecer_energia_almacenada(5)

        procesar_evento("subsidio_energia")

        self.assertEqual(obtener_energia_almacenada(), 15)

    def test_bonificacion_comercial(self):
        procesar_evento("bonificacion_comercial")

        self.assertEqual(mercado.obtener_saldo(), 30)

    def test_mantenimiento_no_deja_saldo_negativo(self):
        mercado.establecer_saldo(10)

        reporte = procesar_evento("mantenimiento")

        self.assertEqual(mercado.obtener_saldo(), 0)
        self.assertEqual(reporte["cambios"]["dinero"], -10)

    def test_evento_forzado_es_determinista(self):
        primer_reporte = procesar_evento("hallazgo_hierro")
        segundo_reporte = procesar_evento("hallazgo_hierro")

        self.assertEqual(primer_reporte["id"], segundo_reporte["id"])
        self.assertEqual(inventario["hierro"], 6)

    def test_selector_controlable(self):
        reporte = procesar_evento(selector=lambda opciones: opciones[1])

        self.assertEqual(reporte["id"], "subsidio_energia")

    def test_reporte_del_turno_incluye_evento(self):
        estadisticas["turnos_completados"] = 4

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno(evento_id="bonificacion_comercial")

        self.assertEqual(reporte["evento"]["id"], "bonificacion_comercial")
        self.assertEqual(mercado.obtener_saldo(), 30)

    def test_reporte_refleja_energia_final_del_evento(self):
        estadisticas["turnos_completados"] = 4

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno(evento_id="subsidio_energia")

        self.assertEqual(reporte["energia_tras_consumo"], 96)
        self.assertEqual(reporte["energia_restante"], 106)

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
