ESTADISTICAS_INICIALES = {
    "hierro_extraido": 0,
    "carbon_extraido": 0,
    "lingotes_producidos": 0,
    "lingotes_automaticos": 0,
    "energia_generada": 0,
    "turnos_completados": 0,
}

OBJETIVOS = {
    "extraer_hierro": {
        "nombre": "Primeros recursos",
        "descripcion": "Extrae 20 unidades de hierro.",
        "tipo": "estadistica",
        "estadistica": "hierro_extraido",
        "meta": 20,
        "unidad": "hierro",
        "recompensa": {"dinero": 50},
    },
    "construir_fundidora": {
        "nombre": "Industria básica",
        "descripcion": "Ten al menos una fundidora construida.",
        "tipo": "maquinas",
        "maquina": "fundidora",
        "meta": 1,
        "unidad": "fundidora",
        "recompensa": {"carbon": 5},
    },
    "producir_lingotes": {
        "nombre": "Metalurgia inicial",
        "descripcion": "Produce acumulativamente 5 lingotes.",
        "tipo": "estadistica",
        "estadistica": "lingotes_producidos",
        "meta": 5,
        "unidad": "lingotes",
        "recompensa": {"dinero": 75},
    },
    "alcanzar_saldo": {
        "nombre": "Capital industrial",
        "descripcion": "Alcanza un saldo de $200.",
        "tipo": "saldo",
        "meta": 200,
        "unidad": "dinero",
        "recompensa": {"placas": 3},
    },
    "mejorar_maquina": {
        "nombre": "Maquinaria avanzada",
        "descripcion": "Mejora cualquier tipo de máquina al nivel 2.",
        "tipo": "nivel_maximo",
        "meta": 2,
        "unidad": "nivel",
        "recompensa": {"energia": 10},
    },
    "generar_energia": {
        "nombre": "Red energética",
        "descripcion": "Genera acumulativamente 30 MW.",
        "tipo": "estadistica",
        "estadistica": "energia_generada",
        "meta": 30,
        "unidad": "MW",
        "recompensa": {"carbon": 5},
    },
    "automatizar_lingotes": {
        "nombre": "Producción automatizada",
        "descripcion": "Produce automáticamente 10 lingotes.",
        "tipo": "estadistica",
        "estadistica": "lingotes_automaticos",
        "meta": 10,
        "unidad": "lingotes automáticos",
        "recompensa": {"dinero": 150},
    },
}

estadisticas = ESTADISTICAS_INICIALES.copy()
objetivos_completados = set()


def registrar_extraccion(hierro=0, carbon=0):
    estadisticas["hierro_extraido"] += max(0, hierro)
    estadisticas["carbon_extraido"] += max(0, carbon)
    return obtener_estadisticas()


def registrar_produccion(lingotes=0, automaticos=0):
    estadisticas["lingotes_producidos"] += max(0, lingotes)
    estadisticas["lingotes_automaticos"] += max(0, automaticos)
    return obtener_estadisticas()


def registrar_generacion_energia(cantidad):
    estadisticas["energia_generada"] += max(0, cantidad)
    return obtener_estadisticas()


def registrar_turno():
    estadisticas["turnos_completados"] += 1
    return estadisticas["turnos_completados"]


def obtener_estadisticas():
    return estadisticas.copy()


def obtener_objetivos_completados():
    return [
        objetivo_id
        for objetivo_id in OBJETIVOS
        if objetivo_id in objetivos_completados
    ]


def _obtener_progreso(definicion):
    tipo = definicion["tipo"]
    if tipo == "estadistica":
        return estadisticas[definicion["estadistica"]]
    if tipo == "maquinas":
        from maquinas import maquinas

        return maquinas.get(definicion["maquina"], 0)
    if tipo == "saldo":
        import mercado

        return mercado.obtener_saldo()
    if tipo == "nivel_maximo":
        from mejoras import niveles_maquinas

        return max(niveles_maquinas.values(), default=1)
    return 0


def _entregar_recompensa(recompensa):
    from energia import establecer_energia_almacenada, obtener_energia_almacenada
    from inventario import inventario
    import mercado

    for tipo, cantidad in recompensa.items():
        if tipo == "dinero":
            mercado.establecer_saldo(mercado.obtener_saldo() + cantidad)
        elif tipo == "energia":
            establecer_energia_almacenada(
                obtener_energia_almacenada() + cantidad
            )
        elif tipo in inventario:
            inventario[tipo] += cantidad


def evaluar_objetivos():
    nuevos = []
    for objetivo_id, definicion in OBJETIVOS.items():
        if objetivo_id in objetivos_completados:
            continue
        progreso = _obtener_progreso(definicion)
        if progreso < definicion["meta"]:
            continue

        objetivos_completados.add(objetivo_id)
        recompensa = definicion["recompensa"].copy()
        _entregar_recompensa(recompensa)
        nuevos.append(
            {
                "id": objetivo_id,
                "nombre": definicion["nombre"],
                "recompensa": recompensa,
            }
        )
    return nuevos


def obtener_estado_objetivos():
    reporte = []
    for objetivo_id, definicion in OBJETIVOS.items():
        reporte.append(
            {
                "id": objetivo_id,
                "nombre": definicion["nombre"],
                "descripcion": definicion["descripcion"],
                "progreso": min(_obtener_progreso(definicion), definicion["meta"]),
                "meta": definicion["meta"],
                "unidad": definicion["unidad"],
                "recompensa": definicion["recompensa"].copy(),
                "completado": objetivo_id in objetivos_completados,
            }
        )
    return reporte


def reiniciar_objetivos():
    estadisticas.clear()
    estadisticas.update(ESTADISTICAS_INICIALES)
    objetivos_completados.clear()
    return obtener_estadisticas()


def restaurar_objetivos(nuevas_estadisticas, completados):
    estadisticas.clear()
    estadisticas.update(nuevas_estadisticas)
    objetivos_completados.clear()
    objetivos_completados.update(completados)
    return {
        "estadisticas": obtener_estadisticas(),
        "objetivos_completados": obtener_objetivos_completados(),
    }
