from config import obtener_nombre

INVENTARIO_INICIAL = {
    "hierro": 0,
    "carbon": 0,
    "lingotes": 0,
    "engranajes": 0,
    "placas": 0,
}

inventario = INVENTARIO_INICIAL.copy()


def reiniciar_inventario():
    inventario.clear()
    inventario.update(INVENTARIO_INICIAL)
    return inventario.copy()


def restaurar_inventario(nuevo_inventario):
    inventario.clear()
    inventario.update(nuevo_inventario)
    return inventario.copy()


def mostrar_inventario(mostrar=True):
    if mostrar:
        print("\nInventario:")
        for recurso in inventario:
            print(f"{obtener_nombre(recurso)}: {inventario[recurso]}")

    return inventario.copy()


def trabajar_mina(recurso, cantidad, mostrar_mensaje=False):
    inventario[recurso] += cantidad

    if mostrar_mensaje:
        print(f" +{cantidad} de {obtener_nombre(recurso)}.")
