import json
import math
import os
from pathlib import Path

import mercado

from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
    reiniciar_automatizacion,
)
from config import NIVEL_MAXIMO, VERSION_JUEGO
from energia import (
    establecer_energia_almacenada,
    obtener_energia_almacenada,
    reiniciar_energia,
)
from inventario import (
    INVENTARIO_INICIAL,
    inventario,
    reiniciar_inventario,
    restaurar_inventario,
)
from maquinas import (
    MAQUINAS_INICIALES,
    maquinas,
    reiniciar_maquinas,
    restaurar_maquinas,
)
from mejoras import (
    NIVELES_INICIALES,
    niveles_maquinas,
    reiniciar_mejoras,
    restaurar_mejoras,
)
from objetivos import (
    ESTADISTICAS_INICIALES,
    OBJETIVOS,
    estadisticas,
    obtener_objetivos_completados,
    reiniciar_objetivos,
    restaurar_objetivos,
)


VERSION_GUARDADO = 1
RUTA_GUARDADO = Path(__file__).resolve().parent / "datos.json"
_autoguardado_habilitado = True


def autoguardado_habilitado():
    return _autoguardado_habilitado


def establecer_autoguardado(habilitado):
    global _autoguardado_habilitado

    _autoguardado_habilitado = habilitado


def recopilar_estado():
    return {
        "version_guardado": VERSION_GUARDADO,
        "version_juego": VERSION_JUEGO,
        "inventario": inventario.copy(),
        "maquinas": maquinas.copy(),
        "dinero": mercado.obtener_saldo(),
        "energia_almacenada": obtener_energia_almacenada(),
        "automatizacion_activa": automatizacion_activa(),
        "niveles_maquinas": niveles_maquinas.copy(),
        "estadisticas": estadisticas.copy(),
        "objetivos_completados": obtener_objetivos_completados(),
    }


def _es_numero_no_negativo(valor):
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
        and valor >= 0
    )


def _validar_cantidades(datos, valores_iniciales, nombre):
    if not isinstance(datos, dict):
        return None, f"'{nombre}' debe ser un diccionario."

    resultado = valores_iniciales.copy()
    for clave in valores_iniciales:
        if clave not in datos:
            continue
        valor = datos[clave]
        if (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor < 0
        ):
            return None, f"Cantidad inválida en {nombre}: '{clave}'."
        resultado[clave] = valor
    return resultado, None


def _validar_niveles(datos):
    if not isinstance(datos, dict):
        return None, "'niveles_maquinas' debe ser un diccionario."

    resultado = NIVELES_INICIALES.copy()
    for tipo in NIVELES_INICIALES:
        if tipo not in datos:
            continue
        nivel = datos[tipo]
        if (
            not isinstance(nivel, int)
            or isinstance(nivel, bool)
            or not 1 <= nivel <= NIVEL_MAXIMO
        ):
            return None, f"Nivel inválido para '{tipo}'."
        resultado[tipo] = nivel
    return resultado, None


def _validar_estadisticas(datos):
    if datos is None:
        return ESTADISTICAS_INICIALES.copy(), None
    if not isinstance(datos, dict):
        return None, "'estadisticas' debe ser un diccionario."

    resultado = ESTADISTICAS_INICIALES.copy()
    for clave in ESTADISTICAS_INICIALES:
        if clave not in datos:
            continue
        valor = datos[clave]
        if (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor < 0
        ):
            return None, f"Estadística inválida: '{clave}'."
        resultado[clave] = valor
    return resultado, None


def _validar_objetivos_completados(datos):
    if datos is None:
        return [], None
    if not isinstance(datos, list):
        return None, "'objetivos_completados' debe ser una lista."
    if any(not isinstance(objetivo_id, str) for objetivo_id in datos):
        return None, "La lista de objetivos contiene tipos inválidos."

    conocidos = []
    for objetivo_id in OBJETIVOS:
        if objetivo_id in datos:
            conocidos.append(objetivo_id)
    return conocidos, None


def validar_estado(datos):
    if not isinstance(datos, dict):
        return {"ok": False, "mensaje": "La raíz debe ser un diccionario."}

    version = datos.get("version_guardado")
    if (
        not isinstance(version, int)
        or isinstance(version, bool)
        or version != VERSION_GUARDADO
    ):
        return {"ok": False, "mensaje": "Versión de guardado no compatible."}

    inventario_validado, error = _validar_cantidades(
        datos.get("inventario"),
        INVENTARIO_INICIAL,
        "inventario",
    )
    if error:
        return {"ok": False, "mensaje": error}

    maquinas_validadas, error = _validar_cantidades(
        datos.get("maquinas"),
        MAQUINAS_INICIALES,
        "maquinas",
    )
    if error:
        return {"ok": False, "mensaje": error}

    niveles_validados, error = _validar_niveles(
        datos.get("niveles_maquinas")
    )
    if error:
        return {"ok": False, "mensaje": error}

    dinero = datos.get("dinero")
    if not _es_numero_no_negativo(dinero):
        return {"ok": False, "mensaje": "El dinero es inválido."}

    energia = datos.get("energia_almacenada")
    if not _es_numero_no_negativo(energia):
        return {"ok": False, "mensaje": "La energía es inválida."}

    automatizacion = datos.get("automatizacion_activa")
    if not isinstance(automatizacion, bool):
        return {"ok": False, "mensaje": "La automatización es inválida."}

    estadisticas_validadas, error = _validar_estadisticas(
        datos.get("estadisticas")
    )
    if error:
        return {"ok": False, "mensaje": error}

    objetivos_validados, error = _validar_objetivos_completados(
        datos.get("objetivos_completados")
    )
    if error:
        return {"ok": False, "mensaje": error}

    return {
        "ok": True,
        "mensaje": "Estado válido.",
        "estado": {
            "inventario": inventario_validado,
            "maquinas": maquinas_validadas,
            "dinero": dinero,
            "energia_almacenada": energia,
            "automatizacion_activa": automatizacion,
            "niveles_maquinas": niveles_validados,
            "estadisticas": estadisticas_validadas,
            "objetivos_completados": objetivos_validados,
        },
    }


def _aplicar_estado(estado):
    restaurar_inventario(estado["inventario"])
    restaurar_maquinas(estado["maquinas"])
    mercado.establecer_saldo(estado["dinero"])
    establecer_energia_almacenada(estado["energia_almacenada"])
    if estado["automatizacion_activa"]:
        activar_automatizacion()
    else:
        desactivar_automatizacion()
    restaurar_mejoras(estado["niveles_maquinas"])
    restaurar_objetivos(
        estado.get("estadisticas", ESTADISTICAS_INICIALES),
        estado.get("objetivos_completados", []),
    )


def guardar_partida(ruta=None):
    ruta_guardado = Path(ruta) if ruta is not None else RUTA_GUARDADO
    ruta_temporal = ruta_guardado.with_suffix(ruta_guardado.suffix + ".tmp")
    datos = recopilar_estado()

    try:
        with ruta_temporal.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())
        ruta_temporal.replace(ruta_guardado)
    except (OSError, TypeError, ValueError) as error:
        try:
            ruta_temporal.unlink(missing_ok=True)
        except OSError:
            pass
        return {
            "ok": False,
            "mensaje": f"No se pudo guardar la partida: {error}",
        }

    establecer_autoguardado(True)
    return {"ok": True, "mensaje": "Partida guardada correctamente."}


def cargar_partida(ruta=None):
    ruta_guardado = Path(ruta) if ruta is not None else RUTA_GUARDADO

    try:
        with ruta_guardado.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        return {"ok": False, "mensaje": "No existe una partida guardada."}
    except (OSError, json.JSONDecodeError):
        return {
            "ok": False,
            "mensaje": "No se pudo cargar la partida: archivo inválido.",
        }

    validacion = validar_estado(datos)
    if not validacion["ok"]:
        return {
            "ok": False,
            "mensaje": (
                "No se pudo cargar la partida: archivo inválido. "
                f"{validacion['mensaje']}"
            ),
        }

    estado_anterior = recopilar_estado()
    try:
        _aplicar_estado(validacion["estado"])
    except Exception:
        _aplicar_estado(estado_anterior)
        return {
            "ok": False,
            "mensaje": "No se pudo cargar la partida de forma segura.",
        }

    establecer_autoguardado(True)
    return {"ok": True, "mensaje": "Partida cargada correctamente."}


def nueva_partida():
    reiniciar_inventario()
    reiniciar_maquinas()
    mercado.reiniciar_saldo()
    reiniciar_energia()
    reiniciar_automatizacion()
    reiniciar_mejoras()
    reiniciar_objetivos()
    establecer_autoguardado(True)
    return {"ok": True, "mensaje": "Nueva partida iniciada."}


def existe_partida_guardada(ruta=None):
    ruta_guardado = Path(ruta) if ruta is not None else RUTA_GUARDADO
    return ruta_guardado.is_file()


def borrar_partida_guardada(ruta=None):
    ruta_guardado = Path(ruta) if ruta is not None else RUTA_GUARDADO

    try:
        ruta_guardado.unlink()
    except FileNotFoundError:
        return {"ok": False, "mensaje": "No existe una partida guardada."}
    except OSError as error:
        return {
            "ok": False,
            "mensaje": f"No se pudo borrar la partida guardada: {error}",
        }

    establecer_autoguardado(False)
    return {"ok": True, "mensaje": "Partida guardada borrada correctamente."}
