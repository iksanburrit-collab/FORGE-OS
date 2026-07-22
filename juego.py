from math import ceil

from config import obtener_nombre
from inventario import inventario, trabajar_mina
from maquinas import maquinas
from recetas import RECETAS


def _buscar_receta(producto):
    if producto in RECETAS:
        return RECETAS[producto]

    for receta in RECETAS.values():
        if producto in receta["produce"]:
            return receta

    return None


def fabricar(producto, cantidad=1, mostrar_mensaje=True):
    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        if mostrar_mensaje:
            print("La cantidad debe ser un número entero mayor que cero.")
        return 0

    if producto in {"lingote", "lingotes"}:
        if mostrar_mensaje:
            print("Los lingotes se producen con el comando 'fundir'.")
        return 0

    receta = _buscar_receta(producto)
    if receta is None or producto not in receta["produce"]:
        if mostrar_mensaje:
            print(f"No existe una receta para '{producto}'.")
        return 0

    producido_por_lote = receta["produce"][producto]
    lotes = ceil(cantidad / producido_por_lote)
    recursos_necesarios = {
        recurso: requerido * lotes
        for recurso, requerido in receta["consume"].items()
    }
    faltantes = {
        recurso: requerido - inventario.get(recurso, 0)
        for recurso, requerido in recursos_necesarios.items()
        if inventario.get(recurso, 0) < requerido
    }

    if faltantes:
        if mostrar_mensaje:
            print("No se puede completar la fabricación. Faltan:")
            for recurso, faltante in faltantes.items():
                necesario = recursos_necesarios[recurso]
                disponible = inventario.get(recurso, 0)
                print(
                    f" - {obtener_nombre(recurso)}: {faltante} "
                    f"(necesitas {necesario}, tienes {disponible})"
                )
        return 0

    for recurso, requerido in recursos_necesarios.items():
        inventario[recurso] -= requerido

    cantidad_producida = producido_por_lote * lotes
    inventario[producto] = inventario.get(producto, 0) + cantidad_producida

    if mostrar_mensaje:
        print(
            f"Se fabricaron {cantidad_producida} "
            f"de {obtener_nombre(producto)}."
        )

    return cantidad_producida


def mostrar_recetas(mostrar=True):
    if mostrar:
        print("\nRecetas disponibles:")
        for receta in RECETAS.values():
            productos = ", ".join(
                f"{cantidad} {obtener_nombre(producto)}"
                for producto, cantidad in receta["produce"].items()
            )
            recursos = ", ".join(
                f"{cantidad} {obtener_nombre(recurso)}"
                for recurso, cantidad in receta["consume"].items()
            )
            print(f" - {productos}: {recursos}")

    return RECETAS.copy()


def fundir_recursos(recurso, cantidad=1, mostrar_mensaje=True):
    receta = RECETAS["lingote"]

    if recurso not in receta["consume"]:
        if mostrar_mensaje:
            print(f"No existe una receta de fundición para '{recurso}'.")
        return 0

    if cantidad <= 0:
        if mostrar_mensaje:
            print("La cantidad debe ser mayor que cero.")
        return 0

    recursos_necesarios = {
        nombre: requerido * cantidad
        for nombre, requerido in receta["consume"].items()
    }

    if any(
        inventario[nombre] < requerido
        for nombre, requerido in recursos_necesarios.items()
    ):
        if mostrar_mensaje:
            print("No hay suficientes recursos para fundir.")
        return 0

    for nombre, requerido in recursos_necesarios.items():
        inventario[nombre] -= requerido
    for producto, producido in receta["produce"].items():
        inventario[producto] += producido * cantidad

    if mostrar_mensaje:
        print(f"Se usaron hierro y carbón para fundir {cantidad} lingote(s).")

    return cantidad


def fundir(mostrar_mensaje=True, recurso=None, cantidad=None):
    if recurso is not None:
        cantidad = cantidad if cantidad is not None else 1
        return fundir_recursos(
            recurso,
            cantidad,
            mostrar_mensaje=mostrar_mensaje,
        )

    receta = RECETAS["lingote"]

    recursos_necesarios = receta["consume"]
    productos_creados = receta["produce"]

    lingotes_creados = 0

    for _ in range(maquinas["fundidora"]):
        puede_fundir = all(
            inventario[recurso] >= cantidad
            for recurso, cantidad in recursos_necesarios.items()
        )
        if puede_fundir:
            for recurso, cantidad in recursos_necesarios.items():
                inventario[recurso] -= cantidad
            for producto, cantidad in productos_creados.items():
                inventario[producto] += cantidad
            lingotes_creados += 1

    if lingotes_creados > 0:
        if mostrar_mensaje:
            print(f"Se fundieron {lingotes_creados} lingotes.")
    else:
        if mostrar_mensaje:
            print("No hay suficientes recursos para fundir.")

    return lingotes_creados


def avanzar_turno(mostrar_produccion=True):
    print("\n===== NUEVO TURNO =====")

    hierro_producido = maquinas["mina_hierro"] * 2
    carbon_producido = maquinas["mina_carbon"] * 1

    trabajar_mina("hierro", hierro_producido, mostrar_mensaje=mostrar_produccion)
    trabajar_mina("carbon", carbon_producido, mostrar_mensaje=mostrar_produccion)
