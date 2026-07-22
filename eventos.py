import random

import mercado

from energia import establecer_energia_almacenada, obtener_energia_almacenada
from inventario import inventario


EVENTOS = {
    "hallazgo_hierro": {
        "nombre": "Hallazgo de hierro",
        "descripcion": "+3 de Hierro",
    },
    "subsidio_energia": {
        "nombre": "Subsidio energético",
        "descripcion": "+10 MW",
    },
    "bonificacion_comercial": {
        "nombre": "Bonificación comercial",
        "descripcion": "+$30",
    },
    "mantenimiento": {
        "nombre": "Mantenimiento industrial",
        "descripcion": "Hasta -$15",
    },
}


def procesar_evento(evento_id=None, selector=None):
    opciones = tuple(EVENTOS)
    if evento_id is None:
        evento_id = selector(opciones) if selector else random.choice(opciones)

    if evento_id not in EVENTOS:
        return {
            "ok": False,
            "mensaje": "Evento industrial desconocido.",
            "evento": None,
        }

    cambios = {}
    if evento_id == "hallazgo_hierro":
        inventario["hierro"] += 3
        cambios["hierro"] = 3
    elif evento_id == "subsidio_energia":
        establecer_energia_almacenada(obtener_energia_almacenada() + 10)
        cambios["energia"] = 10
    elif evento_id == "bonificacion_comercial":
        mercado.establecer_saldo(mercado.obtener_saldo() + 30)
        cambios["dinero"] = 30
    elif evento_id == "mantenimiento":
        costo = min(15, mercado.obtener_saldo())
        mercado.establecer_saldo(mercado.obtener_saldo() - costo)
        cambios["dinero"] = -costo

    definicion = EVENTOS[evento_id]
    return {
        "ok": True,
        "id": evento_id,
        "nombre": definicion["nombre"],
        "descripcion": definicion["descripcion"],
        "cambios": cambios,
    }
