_automatizacion_habilitada = False

PROCESOS_AUTOMATICOS = ("fundicion",)


def activar_automatizacion():
    global _automatizacion_habilitada

    cambio = not _automatizacion_habilitada
    _automatizacion_habilitada = True
    reporte = obtener_estado_automatizacion()
    reporte["cambio"] = cambio
    return reporte


def desactivar_automatizacion():
    global _automatizacion_habilitada

    cambio = _automatizacion_habilitada
    _automatizacion_habilitada = False
    reporte = obtener_estado_automatizacion()
    reporte["cambio"] = cambio
    return reporte


def automatizacion_activa():
    return _automatizacion_habilitada


def obtener_estado_automatizacion():
    return {
        "activa": _automatizacion_habilitada,
        "procesos": list(PROCESOS_AUTOMATICOS),
    }


def obtener_maquinas_efectivas(maquinas):
    maquinas_efectivas = maquinas.copy()
    if not automatizacion_activa():
        maquinas_efectivas["fundidora"] = 0
    return maquinas_efectivas
