import importlib
import runpy
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock, patch

import mercado
from automatizacion import automatizacion_activa
from config import VERSION_JUEGO
from energia import obtener_energia_almacenada
from interfaz.adaptadores import (
    ControladorGUI,
    formatear_energia,
    formatear_inventario,
    formatear_maquinas,
    formatear_objetivos,
    formatear_progreso,
    obtener_snapshot,
    validar_cantidad,
)
from inventario import inventario
from maquinas import maquinas
from objetivos import obtener_estado_objetivos
from persistencia import nueva_partida, recopilar_estado


class AdaptadoresInterfazTests(unittest.TestCase):
    def setUp(self):
        self.estado = deepcopy(recopilar_estado())
        nueva_partida()
        self.controlador = ControladorGUI()

    def tearDown(self):
        from persistencia import _aplicar_estado

        _aplicar_estado(self.estado)

    def test_importar_interfaz_no_crea_ventana(self):
        with patch("tkinter.Tk") as crear_tk:
            importlib.reload(sys.modules["interfaz.ventana_principal"])
        crear_tk.assert_not_called()

    def test_formatear_inventario(self):
        self.assertIn(("Hierro", 2), formatear_inventario({"hierro": 2}))

    def test_formatear_maquinas(self):
        filas = formatear_maquinas({"mina_hierro": 1}, {"mina_hierro": 1})
        self.assertEqual(filas[0][1:3], (1, 1))

    def test_formatear_energia(self):
        filas = dict(formatear_energia(obtener_snapshot()["energia"]))
        self.assertIn("Consumo potencial", filas)
        self.assertIn("Consumo efectivo", filas)

    def test_formatear_progreso(self):
        reporte = {"estadisticas": {"turnos_completados": 3}, "objetivos_completados": 1, "objetivos_totales": 7}
        self.assertIn(("Turnos completados", 3), formatear_progreso(reporte))

    def test_formatear_objetivos(self):
        lineas = formatear_objetivos(obtener_estado_objetivos())
        self.assertTrue(lineas[0].startswith("["))
        self.assertIn("Recompensa", lineas[0])

    def test_cantidad_vacia(self):
        self.assertEqual(validar_cantidad(""), (None, "Indica una cantidad."))

    def test_cantidad_texto(self):
        self.assertIsNotNone(validar_cantidad("abc")[1])

    def test_cantidad_cero(self):
        self.assertIsNotNone(validar_cantidad("0")[1])

    def test_cantidad_negativa(self):
        self.assertIsNotNone(validar_cantidad("-2")[1])

    def test_cantidad_valida(self):
        self.assertEqual(validar_cantidad(" 4 "), (4, None))

    def test_controlador_reutiliza_logica_de_fabricacion(self):
        with patch("interfaz.adaptadores.fabricar", return_value=2) as fabricar:
            ok, _, _ = self.controlador.fabricar("placas", 2)
        self.assertTrue(ok)
        fabricar.assert_called_once_with("placas", 2, mostrar_mensaje=False)

    def test_snapshot_no_modifica_estado(self):
        antes = deepcopy(recopilar_estado())
        obtener_snapshot()
        self.assertEqual(recopilar_estado(), antes)

    def test_guardar_mediante_controlador(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "partida.json"
            ok, _, _ = self.controlador.guardar(ruta)
            self.assertTrue(ok)
            self.assertTrue(ruta.exists())

    def test_cargar_mediante_controlador(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "partida.json"
            inventario["hierro"] = 9
            self.controlador.guardar(ruta)
            inventario["hierro"] = 0
            ok, _, _ = self.controlador.cargar(ruta)
            self.assertTrue(ok)
            self.assertEqual(inventario["hierro"], 9)

    def test_carga_fallida_conserva_estado(self):
        antes = deepcopy(recopilar_estado())
        ok, _, _ = self.controlador.cargar("archivo-que-no-existe.json")
        self.assertFalse(ok)
        self.assertEqual(recopilar_estado(), antes)

    def test_nueva_partida_cancelada_no_modifica_estado(self):
        inventario["hierro"] = 8
        antes = deepcopy(recopilar_estado())
        ok, _, _ = self.controlador.nueva_partida(False)
        self.assertFalse(ok)
        self.assertEqual(recopilar_estado(), antes)

    def test_nueva_partida_confirmada_reinicia(self):
        inventario["hierro"] = 8
        ok, _, _ = self.controlador.nueva_partida(True)
        self.assertTrue(ok)
        self.assertEqual(inventario["hierro"], 0)

    def test_automatizacion_cambia(self):
        antes = automatizacion_activa()
        self.controlador.alternar_automatizacion()
        self.assertNotEqual(automatizacion_activa(), antes)

    def test_avanzar_turno_devuelve_reporte(self):
        ok, mensaje, reporte = self.controlador.avanzar_turno()
        self.assertTrue(ok)
        self.assertIn("Turno completado", mensaje)
        self.assertEqual(reporte["estadisticas"]["turnos_completados"], 1)

    def test_error_visual_se_contiene(self):
        from interfaz.ventana_principal import VentanaPrincipal

        ventana = VentanaPrincipal.__new__(VentanaPrincipal)
        ventana.raiz = Mock()
        ventana.registrar = Mock()
        ventana.actualizar_interfaz = Mock()
        with patch("interfaz.ventana_principal.messagebox.showerror"):
            resultado = ventana._ejecutar(Mock(side_effect=RuntimeError("fallo")))
        self.assertFalse(resultado[0])

    def test_modo_predeterminado_abre_gui(self):
        with patch(
            "interfaz.ventana_principal.iniciar_interfaz"
        ) as iniciar, patch.object(sys, "argv", ["main.py"]):
            runpy.run_path("main.py", run_name="__main__")
        iniciar.assert_called_once_with()

    def test_seleccion_gui_funciona(self):
        with patch("interfaz.ventana_principal.iniciar_interfaz") as iniciar, patch.object(sys, "argv", ["main.py", "--gui"]):
            runpy.run_path("main.py", run_name="__main__")
        iniciar.assert_called_once_with()

    def test_version_visible_es_1_0(self):
        self.assertEqual(VERSION_JUEGO, "1.0")


if __name__ == "__main__":
    unittest.main()
