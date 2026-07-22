import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import mercado
import persistencia
from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
)
from comandos import procesar_comando
from energia import establecer_energia_almacenada, obtener_energia_almacenada
from inventario import INVENTARIO_INICIAL, inventario, restaurar_inventario
from main import iniciar_juego
from maquinas import MAQUINAS_INICIALES, maquinas, restaurar_maquinas
from mejoras import NIVELES_INICIALES, niveles_maquinas, restaurar_mejoras
from persistencia import (
    cargar_partida,
    guardar_partida,
    nueva_partida,
    recopilar_estado,
)


class PersistenciaTests(unittest.TestCase):
    def setUp(self):
        self.estado_original = self._capturar_estado()
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta = Path(self.temporal.name) / "datos.json"
        nueva_partida()

    def tearDown(self):
        self._restaurar_estado(self.estado_original)
        self.temporal.cleanup()

    def test_recopilar_estado_completo(self):
        estado = recopilar_estado()

        self.assertEqual(estado["version_guardado"], 1)
        self.assertEqual(estado["version_juego"], "0.8")
        self.assertEqual(
            set(estado),
            {
                "version_guardado",
                "version_juego",
                "inventario",
                "maquinas",
                "dinero",
                "energia_almacenada",
                "automatizacion_activa",
                "niveles_maquinas",
            },
        )

    def test_guardar_json_valido(self):
        resultado = guardar_partida(self.ruta)
        datos = json.loads(self.ruta.read_text(encoding="utf-8"))

        self.assertTrue(resultado["ok"])
        self.assertEqual(datos["version_guardado"], 1)

    def test_cargar_json_valido(self):
        datos = self._estado_valido()
        self._escribir(datos)

        resultado = cargar_partida(self.ruta)

        self.assertTrue(resultado["ok"])

    def test_cargar_restaura_inventario(self):
        datos = self._estado_valido()
        datos["inventario"]["hierro"] = 17
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(inventario["hierro"], 17)

    def test_cargar_restaura_maquinas(self):
        datos = self._estado_valido()
        datos["maquinas"]["fundidora"] = 4
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(maquinas["fundidora"], 4)

    def test_cargar_restaura_dinero(self):
        datos = self._estado_valido()
        datos["dinero"] = 123
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(mercado.obtener_saldo(), 123)

    def test_cargar_restaura_energia(self):
        datos = self._estado_valido()
        datos["energia_almacenada"] = 77
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(obtener_energia_almacenada(), 77)

    def test_cargar_restaura_automatizacion(self):
        datos = self._estado_valido()
        datos["automatizacion_activa"] = True
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertTrue(automatizacion_activa())

    def test_cargar_restaura_niveles(self):
        datos = self._estado_valido()
        datos["niveles_maquinas"]["mina_hierro"] = 3
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(niveles_maquinas["mina_hierro"], 3)

    def test_archivo_inexistente(self):
        resultado = cargar_partida(self.ruta)

        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["mensaje"], "No existe una partida guardada.")

    def test_json_mal_formado(self):
        self.ruta.write_text("{no es json", encoding="utf-8")

        resultado = cargar_partida(self.ruta)

        self.assertFalse(resultado["ok"])

    def test_raiz_no_es_diccionario(self):
        self._escribir([1, 2, 3])

        resultado = cargar_partida(self.ruta)

        self.assertFalse(resultado["ok"])

    def test_version_de_guardado_ausente(self):
        datos = self._estado_valido()
        del datos["version_guardado"]

        self.assert_carga_invalida(datos)

    def test_dinero_negativo(self):
        datos = self._estado_valido()
        datos["dinero"] = -1

        self.assert_carga_invalida(datos)

    def test_energia_negativa(self):
        datos = self._estado_valido()
        datos["energia_almacenada"] = -1

        self.assert_carga_invalida(datos)

    def test_cantidades_negativas(self):
        for seccion, clave in (
            ("inventario", "hierro"),
            ("maquinas", "mina_hierro"),
        ):
            with self.subTest(seccion=seccion):
                datos = self._estado_valido()
                datos[seccion][clave] = -1
                self.assert_carga_invalida(datos)

    def test_niveles_fuera_de_rango(self):
        for nivel in (0, 4):
            with self.subTest(nivel=nivel):
                datos = self._estado_valido()
                datos["niveles_maquinas"]["fundidora"] = nivel
                self.assert_carga_invalida(datos)

    def test_tipos_incorrectos(self):
        casos = (
            ("dinero", "mucho"),
            ("energia_almacenada", True),
            ("automatizacion_activa", 1),
            ("inventario", []),
            ("maquinas", []),
            ("niveles_maquinas", []),
        )
        for clave, valor in casos:
            with self.subTest(clave=clave):
                datos = self._estado_valido()
                datos[clave] = valor
                self.assert_carga_invalida(datos)

    def test_carga_invalida_no_modifica_estado(self):
        inventario["hierro"] = 9
        mercado.dinero = 50
        estado_inicial = self._capturar_estado()
        datos = self._estado_valido()
        datos["dinero"] = -1
        self._escribir(datos)

        cargar_partida(self.ruta)

        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_carga_atomica_ante_fallo_de_aplicacion(self):
        inventario["hierro"] = 9
        estado_inicial = self._capturar_estado()
        datos = self._estado_valido()
        datos["inventario"]["hierro"] = 20
        self._escribir(datos)
        restaurar_real = persistencia.restaurar_maquinas
        llamadas = 0

        def fallar_una_vez(nuevas_maquinas):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 1:
                raise RuntimeError("fallo simulado")
            return restaurar_real(nuevas_maquinas)

        with patch(
            "persistencia.restaurar_maquinas",
            side_effect=fallar_una_vez,
        ):
            resultado = cargar_partida(self.ruta)

        self.assertFalse(resultado["ok"])
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_claves_faltantes_usan_valores_iniciales(self):
        datos = self._estado_valido()
        datos["inventario"] = {"hierro": 7}
        datos["maquinas"] = {}
        datos["niveles_maquinas"] = {}
        self._escribir(datos)

        resultado = cargar_partida(self.ruta)

        self.assertTrue(resultado["ok"])
        self.assertEqual(inventario["hierro"], 7)
        self.assertEqual(inventario["carbon"], INVENTARIO_INICIAL["carbon"])
        self.assertEqual(maquinas, MAQUINAS_INICIALES)
        self.assertEqual(niveles_maquinas, NIVELES_INICIALES)

    def test_claves_desconocidas_se_ignoran(self):
        datos = self._estado_valido()
        datos["contenido_futuro"] = {"valor": object().__class__.__name__}
        datos["inventario"]["uranio"] = "dato futuro"
        self._escribir(datos)

        resultado = cargar_partida(self.ruta)

        self.assertTrue(resultado["ok"])
        self.assertNotIn("uranio", inventario)

    def test_nueva_partida_restaura_todos_los_estados(self):
        self._establecer_estado_modificado()

        with redirect_stdout(StringIO()):
            resultado_comando = procesar_comando("nueva partida confirmar")

        self.assertTrue(resultado_comando)
        self.assertEqual(inventario, INVENTARIO_INICIAL)
        self.assertEqual(maquinas, MAQUINAS_INICIALES)
        self.assertEqual(mercado.obtener_saldo(), 0)
        self.assertEqual(obtener_energia_almacenada(), 10)
        self.assertFalse(automatizacion_activa())
        self.assertEqual(niveles_maquinas, NIVELES_INICIALES)

    def test_nueva_partida_sin_confirmacion_no_modifica_estado(self):
        self._establecer_estado_modificado()
        estado_inicial = self._capturar_estado()

        with redirect_stdout(StringIO()):
            self.assertTrue(procesar_comando("nueva partida"))

        self.assertEqual(self._capturar_estado(), estado_inicial)

    def test_guardado_temporal_se_reemplaza(self):
        guardar_partida(self.ruta)

        self.assertTrue(self.ruta.is_file())
        self.assertFalse(Path(f"{self.ruta}.tmp").exists())

    def test_fallo_de_escritura_conserva_guardado_anterior(self):
        contenido_anterior = '{"guardado": "anterior"}'
        self.ruta.write_text(contenido_anterior, encoding="utf-8")

        with patch("persistencia.json.dump", side_effect=OSError("sin espacio")):
            resultado = guardar_partida(self.ruta)

        self.assertFalse(resultado["ok"])
        self.assertEqual(self.ruta.read_text(encoding="utf-8"), contenido_anterior)
        self.assertFalse(Path(f"{self.ruta}.tmp").exists())

    def test_guardado_automatico_al_salir(self):
        resultado = {"ok": True, "mensaje": "Guardada."}
        with patch("comandos.guardar_partida", return_value=resultado) as guardar:
            with redirect_stdout(StringIO()):
                self.assertFalse(procesar_comando("salir"))

        guardar.assert_called_once_with()

    def test_fallo_de_autoguardado_permite_salir(self):
        resultado = {"ok": False, "mensaje": "Fallo de guardado."}
        with patch("comandos.guardar_partida", return_value=resultado):
            with redirect_stdout(StringIO()) as salida:
                continuar = procesar_comando("salir")

        self.assertFalse(continuar)
        self.assertIn("Fallo de guardado", salida.getvalue())
        self.assertIn("Saliendo del juego", salida.getvalue())

    def test_arranque_avisa_si_existe_guardado(self):
        guardado = {"ok": True, "mensaje": "Guardada."}
        with patch("main.existe_partida_guardada", return_value=True):
            with patch("builtins.input", return_value="salir"):
                with patch("comandos.guardar_partida", return_value=guardado):
                    with redirect_stdout(StringIO()) as salida:
                        iniciar_juego()

        self.assertIn("Hay una partida guardada", salida.getvalue())

    def assert_carga_invalida(self, datos):
        estado_inicial = self._capturar_estado()
        self._escribir(datos)

        resultado = cargar_partida(self.ruta)

        self.assertFalse(resultado["ok"])
        self.assertEqual(self._capturar_estado(), estado_inicial)

    def _estado_valido(self):
        return {
            "version_guardado": 1,
            "version_juego": "0.8",
            "inventario": INVENTARIO_INICIAL.copy(),
            "maquinas": MAQUINAS_INICIALES.copy(),
            "dinero": 0,
            "energia_almacenada": 10,
            "automatizacion_activa": False,
            "niveles_maquinas": NIVELES_INICIALES.copy(),
        }

    def _escribir(self, datos):
        self.ruta.write_text(
            json.dumps(datos, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _capturar_estado():
        return {
            "inventario": deepcopy(inventario),
            "maquinas": deepcopy(maquinas),
            "dinero": mercado.obtener_saldo(),
            "energia": obtener_energia_almacenada(),
            "automatizacion": automatizacion_activa(),
            "niveles": deepcopy(niveles_maquinas),
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

    @staticmethod
    def _establecer_estado_modificado():
        inventario["hierro"] = 9
        maquinas["fundidora"] = 5
        mercado.dinero = 200
        establecer_energia_almacenada(90)
        activar_automatizacion()
        niveles_maquinas["fundidora"] = 3


if __name__ == "__main__":
    unittest.main()
