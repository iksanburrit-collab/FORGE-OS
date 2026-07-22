from config import (
    CONSUMO_CARBON_GENERADOR,
    CONSUMO_ENERGIA,
    ENERGIA_INICIAL,
    GENERACION_GENERADOR_POR_NIVEL,
    PRIORIDAD_ENERGIA,
)
from mejoras import obtener_nivel


energia_almacenada = ENERGIA_INICIAL


def calcular_generacion(maquinas):
    nivel = obtener_nivel("generador_carbon")
    generacion = GENERACION_GENERADOR_POR_NIVEL[nivel]
    return maquinas.get("generador_carbon", 0) * generacion


def calcular_consumo_maximo(maquinas):
    return sum(
        maquinas.get(tipo, 0) * consumo
        for tipo, consumo in CONSUMO_ENERGIA.items()
    )


def obtener_energia_almacenada():
    return energia_almacenada


def establecer_energia_almacenada(cantidad):
    global energia_almacenada

    energia_almacenada = max(0, cantidad)


def generar_energia(maquinas, inventario):
    generadores = maquinas.get("generador_carbon", 0)
    carbon_disponible = inventario.get("carbon", 0)
    generadores_activos = min(
        generadores,
        carbon_disponible // CONSUMO_CARBON_GENERADOR,
    )
    carbon_consumido = generadores_activos * CONSUMO_CARBON_GENERADOR
    nivel = obtener_nivel("generador_carbon")
    generacion_unitaria = GENERACION_GENERADOR_POR_NIVEL[nivel]
    energia_generada = generadores_activos * generacion_unitaria

    if carbon_consumido:
        inventario["carbon"] -= carbon_consumido
    establecer_energia_almacenada(energia_almacenada + energia_generada)

    return {
        "generadores_disponibles": generadores,
        "generadores_activos": generadores_activos,
        "carbon_consumido": carbon_consumido,
        "energia_generada": energia_generada,
        "generacion_unitaria": generacion_unitaria,
        "nivel_generador": nivel,
        "energia_almacenada": energia_almacenada,
    }


def consumir_energia(cantidad):
    if cantidad < 0 or cantidad > energia_almacenada:
        return False

    establecer_energia_almacenada(energia_almacenada - cantidad)
    return True


def distribuir_energia(maquinas, energia_disponible=None):
    if energia_disponible is None:
        energia_disponible = calcular_generacion(maquinas)
    energia_restante = energia_disponible
    maquinas_activas = {}
    maquinas_sin_energia = {}

    for tipo in PRIORIDAD_ENERGIA:
        construidas = maquinas.get(tipo, 0)
        consumo_unitario = CONSUMO_ENERGIA[tipo]
        activas = min(construidas, energia_restante // consumo_unitario)
        sin_energia = construidas - activas

        maquinas_activas[tipo] = activas
        maquinas_sin_energia[tipo] = sin_energia
        energia_restante -= activas * consumo_unitario

    energia_utilizada = energia_disponible - energia_restante
    return {
        "energia_disponible": energia_disponible,
        "energia_utilizada": energia_utilizada,
        "energia_restante": energia_restante,
        "maquinas_activas": maquinas_activas,
        "maquinas_sin_energia": maquinas_sin_energia,
    }


def obtener_reporte_energia(maquinas, energia_disponible=None):
    if energia_disponible is None:
        energia_disponible = energia_almacenada
    reporte = distribuir_energia(maquinas, energia_disponible)
    consumo_maximo = calcular_consumo_maximo(maquinas)
    reporte.update(
        {
            "capacidad_generacion": calcular_generacion(maquinas),
            "consumo_maximo": consumo_maximo,
            "deficit": max(0, consumo_maximo - energia_disponible),
            "generadores": {
                "generador_carbon": maquinas.get("generador_carbon", 0),
            },
            "consumo_por_tipo": {
                tipo: {
                    "maquinas": maquinas.get(tipo, 0),
                    "consumo_unitario": consumo,
                    "consumo_total": maquinas.get(tipo, 0) * consumo,
                }
                for tipo, consumo in CONSUMO_ENERGIA.items()
            },
        }
    )
    return reporte
