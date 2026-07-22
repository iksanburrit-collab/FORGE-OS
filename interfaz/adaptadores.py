"""Adaptadores sin dependencias visuales para la interfaz de FORGE OS."""

from copy import deepcopy

import mercado
from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
)
from comandos import ejecutar_generacion_energia, mostrar_energia
from config import COSTOS_CONSTRUCCION, obtener_nombre
from inventario import inventario
from juego import avanzar_turno, fabricar, fundir
from maquinas import construir_maquina, maquinas
from mejoras import mejorar_maquina, niveles_maquinas, obtener_efecto
from objetivos import evaluar_objetivos, obtener_estadisticas, obtener_estado_objetivos
from persistencia import cargar_partida, guardar_partida, nueva_partida


def validar_cantidad(texto):
    if texto is None or not str(texto).strip():
        return None, "Indica una cantidad."
    try:
        cantidad = int(str(texto).strip())
    except ValueError:
        return None, "La cantidad debe ser un número entero."
    if cantidad <= 0:
        return None, "La cantidad debe ser mayor que cero."
    return cantidad, None


def formatear_costo(costo):
    recursos = costo if isinstance(costo, dict) else {"lingotes": costo}
    return ", ".join(
        f"${cantidad}" if recurso == "dinero" else
        f"{cantidad} {obtener_nombre(recurso)}"
        for recurso, cantidad in recursos.items()
    )


def formatear_inventario(datos):
    return [(obtener_nombre(clave), cantidad) for clave, cantidad in datos.items()]


def formatear_maquinas(datos, niveles=None):
    niveles = niveles or niveles_maquinas
    filas = []
    for tipo, cantidad in datos.items():
        nivel = niveles.get(tipo, 1)
        efecto = obtener_efecto(tipo, nivel)
        efecto_texto = (
            f"{efecto['cantidad']} {efecto['unidad']}" if efecto else "Sin efecto"
        )
        filas.append((obtener_nombre(tipo), cantidad, nivel, efecto_texto))
    return filas


def formatear_energia(reporte):
    estado = "Activa" if automatizacion_activa() else "Desactivada"
    generadores = sum(reporte["generadores"].values())
    return [
        ("Energía almacenada", f"{reporte['energia_disponible']} MW"),
        ("Consumo potencial", f"{reporte['consumo_potencial']} MW"),
        ("Consumo efectivo", f"{reporte['consumo_efectivo']} MW"),
        ("Generación por generador", f"{reporte['capacidad_generacion'] // generadores if generadores else 0} MW"),
        ("Automatización", estado),
    ]


def formatear_progreso(reporte):
    estadisticas = reporte["estadisticas"]
    filas = [(clave.replace("_", " ").capitalize(), valor) for clave, valor in estadisticas.items()]
    filas.append(("Objetivos completados", f"{reporte['objetivos_completados']}/{reporte['objetivos_totales']}"))
    return filas


def formatear_objetivos(objetivos):
    filas = []
    for objetivo in objetivos:
        marca = "[x]" if objetivo["completado"] else "[ ]"
        recompensa = formatear_costo(objetivo["recompensa"])
        filas.append(
            f"{marca} {objetivo['nombre']} — {objetivo['progreso']}/{objetivo['meta']} "
            f"{objetivo['unidad']} — Recompensa: {recompensa}"
        )
    return filas


def obtener_snapshot():
    energia = mostrar_energia(mostrar=False)
    estadisticas = obtener_estadisticas()
    objetivos = obtener_estado_objetivos()
    return {
        "saldo": mercado.obtener_saldo(),
        "turnos": estadisticas["turnos_completados"],
        "automatizacion": automatizacion_activa(),
        "inventario": deepcopy(inventario),
        "maquinas": deepcopy(maquinas),
        "niveles": deepcopy(niveles_maquinas),
        "energia": deepcopy(energia),
        "estadisticas": estadisticas,
        "objetivos": objetivos,
    }


class ControladorGUI:
    """Coordina acciones de GUI sin conocer widgets de Tkinter."""

    def avanzar_turno(self):
        reporte = avanzar_turno(mostrar_produccion=False, mostrar_mensaje=False)
        produccion = reporte["produccion"]
        mensaje = (
            f"Turno completado. Hierro +{produccion['hierro']}, "
            f"Carbón +{produccion['carbon']}, lingotes automáticos "
            f"+{reporte['produccion_automatica']['lingotes']}."
        )
        if reporte.get("evento") and reporte["evento"].get("ok"):
            mensaje += f" Evento: {reporte['evento']['nombre']}."
        return True, mensaje, reporte

    def generar_energia(self):
        reporte = ejecutar_generacion_energia(mostrar=False)
        if reporte["energia_generada"]:
            mensaje = f"Energía +{reporte['energia_generada']} MW; carbón -{reporte['carbon_consumido']}."
            return True, mensaje, reporte
        mensaje = "No hay carbón suficiente para generar energía."
        if not reporte["generadores_disponibles"]:
            mensaje = "No hay generadores de carbón construidos."
        return False, mensaje, reporte

    def alternar_automatizacion(self):
        reporte = desactivar_automatizacion() if automatizacion_activa() else activar_automatizacion()
        estado = "activada" if reporte["activa"] else "desactivada"
        return True, f"Automatización {estado}.", reporte

    def construir(self, tipo):
        ok = construir_maquina(tipo, mostrar=False)
        mensaje = f"{obtener_nombre(tipo)} construida." if ok else "Recursos insuficientes para construir."
        if ok:
            evaluar_objetivos()
        return ok, mensaje, None

    def fabricar(self, producto, cantidad):
        producido = fabricar(producto, cantidad, mostrar_mensaje=False)
        if producido:
            evaluar_objetivos()
        return bool(producido), (f"Fabricados {producido} de {obtener_nombre(producto)}." if producido else "No se pudo fabricar: revisa receta y recursos."), producido

    def fundir(self, recurso, cantidad):
        producido = fundir(recurso=recurso, cantidad=cantidad, mostrar_mensaje=False)
        if producido:
            evaluar_objetivos()
        return bool(producido), (f"Fundidos {producido} lingotes." if producido else "No se pudo fundir: revisa receta y recursos."), producido

    def comprar(self, producto, cantidad):
        total = mercado.comprar(producto, cantidad, mostrar_mensaje=False)
        if total:
            evaluar_objetivos()
        return bool(total), (f"Compra completada por ${total}." if total else "No se pudo comprar: revisa saldo y producto."), total

    def vender(self, producto, cantidad):
        total = mercado.vender(producto, cantidad, mostrar_mensaje=False)
        if total:
            evaluar_objetivos()
        return bool(total), (f"Venta completada por ${total}." if total else "No se pudo vender: revisa existencias."), total

    def mejorar(self, tipo):
        reporte = mejorar_maquina(tipo)
        if reporte["exito"]:
            evaluar_objetivos()
            return True, f"{obtener_nombre(tipo)} mejorada al nivel {reporte['nivel_actual']}.", reporte
        motivos = {"nivel_maximo": "La máquina ya está en nivel máximo.", "tipo_invalido": "Tipo de máquina inválido."}
        return False, motivos.get(reporte["motivo"], "Recursos insuficientes para mejorar."), reporte

    def guardar(self, ruta=None):
        reporte = guardar_partida(ruta)
        return reporte["ok"], reporte["mensaje"], reporte

    def cargar(self, ruta=None):
        reporte = cargar_partida(ruta)
        return reporte["ok"], reporte["mensaje"], reporte

    def nueva_partida(self, confirmada):
        if not confirmada:
            return False, "Nueva partida cancelada.", None
        reporte = nueva_partida()
        return True, reporte["mensaje"], reporte
