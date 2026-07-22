import mercado

from config import (
    COSTOS_MEJORAS,
    GENERACION_GENERADOR_POR_NIVEL,
    LOTES_FUNDIDORA_POR_NIVEL,
    NIVEL_MAXIMO,
    PRODUCCION_POR_NIVEL,
)
from inventario import inventario


NIVELES_INICIALES = {
    "mina_hierro": 1,
    "mina_carbon": 1,
    "fundidora": 1,
    "generador_carbon": 1,
}

niveles_maquinas = NIVELES_INICIALES.copy()


def reiniciar_mejoras():
    niveles_maquinas.clear()
    niveles_maquinas.update(NIVELES_INICIALES)
    return niveles_maquinas.copy()


def restaurar_mejoras(nuevos_niveles):
    niveles_maquinas.clear()
    niveles_maquinas.update(nuevos_niveles)
    return niveles_maquinas.copy()


def obtener_nivel(tipo):
    return niveles_maquinas.get(tipo)


def puede_mejorarse(tipo):
    nivel = obtener_nivel(tipo)
    return nivel is not None and nivel < NIVEL_MAXIMO


def obtener_siguiente_nivel(tipo):
    if not puede_mejorarse(tipo):
        return None
    return obtener_nivel(tipo) + 1


def obtener_costo_mejora(tipo):
    siguiente_nivel = obtener_siguiente_nivel(tipo)
    if siguiente_nivel is None:
        return None
    return COSTOS_MEJORAS[tipo][siguiente_nivel].copy()


def obtener_efecto(tipo, nivel=None):
    nivel = nivel if nivel is not None else obtener_nivel(tipo)
    if tipo in PRODUCCION_POR_NIVEL:
        return {
            "tipo": "produccion",
            "cantidad": PRODUCCION_POR_NIVEL[tipo][nivel],
            "unidad": "por máquina y turno",
        }
    if tipo == "fundidora":
        return {
            "tipo": "lotes",
            "cantidad": LOTES_FUNDIDORA_POR_NIVEL[nivel],
            "unidad": "lote(s) por fundidora y turno",
        }
    if tipo == "generador_carbon":
        return {
            "tipo": "generacion",
            "cantidad": GENERACION_GENERADOR_POR_NIVEL[nivel],
            "unidad": "MW por generador",
        }
    return None


def mejorar_maquina(tipo):
    if tipo not in niveles_maquinas:
        return {
            "exito": False,
            "motivo": "tipo_invalido",
            "tipo": tipo,
            "faltantes": {},
        }

    nivel_actual = obtener_nivel(tipo)
    if not puede_mejorarse(tipo):
        return {
            "exito": False,
            "motivo": "nivel_maximo",
            "tipo": tipo,
            "nivel_actual": nivel_actual,
            "faltantes": {},
        }

    siguiente_nivel = obtener_siguiente_nivel(tipo)
    costo = obtener_costo_mejora(tipo)
    faltantes = {}

    dinero_requerido = costo.get("dinero", 0)
    if mercado.obtener_saldo() < dinero_requerido:
        faltantes["dinero"] = dinero_requerido - mercado.obtener_saldo()

    for recurso, cantidad in costo.items():
        if recurso == "dinero":
            continue
        disponible = inventario.get(recurso, 0)
        if disponible < cantidad:
            faltantes[recurso] = cantidad - disponible

    if faltantes:
        return {
            "exito": False,
            "motivo": "recursos_insuficientes",
            "tipo": tipo,
            "nivel_actual": nivel_actual,
            "nivel_objetivo": siguiente_nivel,
            "costo": costo,
            "faltantes": faltantes,
        }

    mercado.dinero -= dinero_requerido
    for recurso, cantidad in costo.items():
        if recurso != "dinero":
            inventario[recurso] -= cantidad
    niveles_maquinas[tipo] = siguiente_nivel

    return {
        "exito": True,
        "motivo": "mejora_completada",
        "tipo": tipo,
        "nivel_anterior": nivel_actual,
        "nivel_actual": siguiente_nivel,
        "costo": costo,
        "faltantes": {},
    }


def obtener_reporte_mejoras():
    reporte = {}
    for tipo, nivel in niveles_maquinas.items():
        siguiente_nivel = obtener_siguiente_nivel(tipo)
        reporte[tipo] = {
            "nivel_actual": nivel,
            "nivel_maximo": NIVEL_MAXIMO,
            "efecto_actual": obtener_efecto(tipo, nivel),
            "siguiente_nivel": siguiente_nivel,
            "efecto_siguiente": (
                obtener_efecto(tipo, siguiente_nivel)
                if siguiente_nivel is not None
                else None
            ),
            "costo_siguiente": obtener_costo_mejora(tipo),
            "en_nivel_maximo": nivel == NIVEL_MAXIMO,
        }
    return reporte
