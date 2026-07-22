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
from comandos import mostrar_mejoras, procesar_comando
from energia import (
    calcular_generacion,
    establecer_energia_almacenada,
    generar_energia,
    obtener_energia_almacenada,
)
from inventario import inventario
from juego import avanzar_turno, fundir
from maquinas import construir_maquina, maquinas
from mejoras import mejorar_maquina, niveles_maquinas
from mercado import vender
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    objetivos_completados,
    restaurar_objetivos,
)


class MejorasTests(unittest.TestCase):
    def setUp(self):
        self.inventario_original = deepcopy(inventario)
        self.maquinas_original = deepcopy(maquinas)
        self.energia_original = obtener_energia_almacenada()
        self.dinero_original = mercado.dinero
        self.automatizacion_original = automatizacion_activa()
        self.niveles_originales = deepcopy(niveles_maquinas)
        self.estadisticas_originales = deepcopy(estadisticas)
        self.objetivos_originales = set(objetivos_completados)

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
        niveles_maquinas.update({tipo: 1 for tipo in niveles_maquinas})
        establecer_energia_almacenada(100)
        mercado.dinero = 0
        desactivar_automatizacion()
        restaurar_objetivos(ESTADISTICAS_INICIALES, OBJETIVOS)

    def tearDown(self):
        inventario.clear()
        inventario.update(self.inventario_original)
        maquinas.clear()
        maquinas.update(self.maquinas_original)
        niveles_maquinas.clear()
        niveles_maquinas.update(self.niveles_originales)
        establecer_energia_almacenada(self.energia_original)
        mercado.dinero = self.dinero_original
        if self.automatizacion_original:
            activar_automatizacion()
        else:
            desactivar_automatizacion()
        restaurar_objetivos(
            self.estadisticas_originales,
            self.objetivos_originales,
        )

    def test_todos_los_tipos_comienzan_en_nivel_uno(self):
        self.assertEqual(set(niveles_maquinas.values()), {1})

    def test_mejora_valida_de_nivel_uno_a_dos(self):
        mercado.dinero = 50
        inventario["lingotes"] = 5

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("mejorar mina de hierro"))

        self.assertEqual(niveles_maquinas["mina_hierro"], 2)

    def test_mejora_valida_de_nivel_dos_a_tres(self):
        niveles_maquinas["mina_carbon"] = 2
        mercado.dinero = 120
        inventario["placas"] = 4

        reporte = mejorar_maquina("mina_carbon")

        self.assertTrue(reporte["exito"])
        self.assertEqual(niveles_maquinas["mina_carbon"], 3)

    def test_no_supera_nivel_maximo(self):
        niveles_maquinas["fundidora"] = 3
        mercado.dinero = 1000
        inventario["engranajes"] = 10
        estado_inicial = self._capturar_estado()

        reporte = mejorar_maquina("fundidora")

        self.assertFalse(reporte["exito"])
        self.assertEqual(reporte["motivo"], "nivel_maximo")
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_costo_se_descuenta_correctamente(self):
        mercado.dinero = 100
        inventario["lingotes"] = 10

        reporte = mejorar_maquina("fundidora")

        self.assertTrue(reporte["exito"])
        self.assertEqual(mercado.obtener_saldo(), 20)
        self.assertEqual(inventario["lingotes"], 2)

    def test_falta_dinero_no_modifica_estado(self):
        mercado.dinero = 49
        inventario["lingotes"] = 5
        estado_inicial = self._capturar_estado()

        reporte = mejorar_maquina("mina_hierro")

        self.assertEqual(reporte["faltantes"], {"dinero": 1})
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_falta_material_no_modifica_estado(self):
        mercado.dinero = 50
        inventario["lingotes"] = 4
        estado_inicial = self._capturar_estado()

        reporte = mejorar_maquina("mina_hierro")

        self.assertEqual(reporte["faltantes"], {"lingotes": 1})
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_falta_dinero_y_materiales_reporta_ambos(self):
        reporte = mejorar_maquina("generador_carbon")

        self.assertEqual(reporte["faltantes"], {"dinero": 100, "placas": 5})
        self.assertEqual(niveles_maquinas["generador_carbon"], 1)

    def test_operacion_es_atomica(self):
        mercado.dinero = 80
        inventario["lingotes"] = 7
        estado_inicial = self._capturar_estado()

        mejorar_maquina("fundidora")

        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_consulta_mejoras_no_tiene_efectos_secundarios(self):
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()) as salida:
            self.assertTrue(procesar_comando("mejoras"))
            reporte = mostrar_mejoras(mostrar=False)

        self.assertIn("MEJORAS", salida.getvalue())
        self.assertEqual(len(reporte), 4)
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_produccion_minera_por_nivel(self):
        maquinas.update({"mina_hierro": 1, "mina_carbon": 0, "fundidora": 0})
        niveles_maquinas["mina_hierro"] = 2

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion"]["hierro"], 3)

    def test_varias_minas_comparten_nivel(self):
        maquinas.update({"mina_hierro": 2, "mina_carbon": 0, "fundidora": 0})
        niveles_maquinas["mina_hierro"] = 3

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion"]["hierro"], 8)

    def test_fundidoras_automaticas_usan_capacidad_por_nivel(self):
        maquinas.update({"mina_hierro": 0, "mina_carbon": 0, "fundidora": 2})
        niveles_maquinas["fundidora"] = 2
        inventario.update({"hierro": 10, "carbon": 10})
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 4)

    def test_fundidoras_mejoradas_sin_energia_no_producen(self):
        niveles_maquinas["fundidora"] = 3
        inventario.update({"hierro": 10, "carbon": 10})
        establecer_energia_almacenada(0)
        activar_automatizacion()

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(reporte["produccion_automatica"]["lingotes"], 0)

    def test_generacion_energetica_por_nivel(self):
        niveles_maquinas["generador_carbon"] = 2

        self.assertEqual(calcular_generacion(maquinas), 15)

    def test_varios_generadores_comparten_nivel(self):
        maquinas["generador_carbon"] = 2
        niveles_maquinas["generador_carbon"] = 3
        inventario["carbon"] = 2

        reporte = generar_energia(maquinas, inventario)

        self.assertEqual(reporte["energia_generada"], 40)
        self.assertEqual(reporte["carbon_consumido"], 2)

    def test_maquina_nueva_hereda_nivel_del_tipo(self):
        niveles_maquinas["mina_hierro"] = 2
        construir_maquina("mina_hierro", costo=0, mostrar=False)
        maquinas.update({"mina_carbon": 0, "fundidora": 0})

        with redirect_stdout(StringIO()):
            reporte = avanzar_turno()

        self.assertEqual(maquinas["mina_hierro"], 2)
        self.assertEqual(reporte["produccion"]["hierro"], 6)

    def test_fundicion_manual_no_usa_capacidad_mejorada(self):
        niveles_maquinas["fundidora"] = 3
        inventario.update({"hierro": 1, "carbon": 1})

        resultado = fundir(
            recurso="hierro",
            cantidad=1,
            mostrar_mensaje=False,
        )

        self.assertEqual(resultado, 1)
        self.assertEqual(inventario["lingotes"], 1)

    def test_mercado_y_ventas_siguen_funcionando(self):
        inventario["hierro"] = 1

        total = vender("hierro", 1, mostrar_mensaje=False)

        self.assertEqual(total, 2)
        self.assertEqual(mercado.obtener_saldo(), 2)

    def test_estado_global_se_reinicia_en_cada_prueba(self):
        self.assertEqual(set(niveles_maquinas.values()), {1})
        self.assertEqual(mercado.obtener_saldo(), 0)
        self.assertFalse(automatizacion_activa())
        self.assertEqual(obtener_energia_almacenada(), 100)

    @staticmethod
    def _capturar_estado():
        return {
            "inventario": deepcopy(inventario),
            "maquinas": deepcopy(maquinas),
            "energia": obtener_energia_almacenada(),
            "dinero": mercado.dinero,
            "automatizacion": automatizacion_activa(),
            "niveles": deepcopy(niveles_maquinas),
        }


if __name__ == "__main__":
    unittest.main()
