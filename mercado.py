from config import PRECIOS_COMPRA, PRECIOS_VENTA, obtener_nombre
from inventario import inventario
from maquinas import maquinas


SALDO_INICIAL = 0
dinero = SALDO_INICIAL


def obtener_saldo():
    return dinero


def establecer_saldo(nuevo_saldo):
    global dinero

    dinero = nuevo_saldo
    return dinero


def reiniciar_saldo():
    return establecer_saldo(SALDO_INICIAL)


def mostrar_saldo(mostrar=True):
    if mostrar:
        print(f"Saldo disponible: ${dinero}")

    return dinero


def mostrar_mercado(mostrar=True):
    if mostrar:
        print("\nMercado:")
        for producto, precio in PRECIOS_VENTA.items():
            print(f" - {obtener_nombre(producto)}: ${precio} por unidad")

    return PRECIOS_VENTA.copy()


def obtener_catalogo_compra():
    return PRECIOS_COMPRA.copy()


def comprar(producto, cantidad=1, mostrar_mensaje=True):
    global dinero

    if producto not in PRECIOS_COMPRA:
        if mostrar_mensaje:
            print(f"El producto '{producto}' no está disponible para comprar.")
        return 0

    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        if mostrar_mensaje:
            print("La cantidad debe ser un número entero mayor que cero.")
        return 0

    costo_total = PRECIOS_COMPRA[producto] * cantidad
    if dinero < costo_total:
        if mostrar_mensaje:
            print(
                f"Saldo insuficiente. Necesitas ${costo_total} "
                f"y tienes ${dinero}."
            )
        return 0

    if producto in inventario:
        destino = inventario
    elif producto in maquinas:
        destino = maquinas
    else:
        if mostrar_mensaje:
            print(f"No existe un destino válido para '{producto}'.")
        return 0

    dinero -= costo_total
    destino[producto] += cantidad

    if mostrar_mensaje:
        print(
            f"Compra completada: {cantidad} de {obtener_nombre(producto)} "
            f"por ${costo_total}."
        )
        print(f"Saldo actual: ${dinero}.")

    return costo_total


def vender(producto, cantidad, mostrar_mensaje=True):
    global dinero

    if producto not in inventario:
        if mostrar_mensaje:
            print(f"El producto '{producto}' no existe.")
        return 0

    if producto not in PRECIOS_VENTA:
        if mostrar_mensaje:
            print(f"{obtener_nombre(producto)} no puede venderse.")
        return 0

    if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
        if mostrar_mensaje:
            print("La cantidad debe ser un número entero mayor que cero.")
        return 0

    disponible = inventario[producto]
    if disponible < cantidad:
        if mostrar_mensaje:
            faltante = cantidad - disponible
            print(
                f"No hay suficiente {obtener_nombre(producto)}. "
                f"Tienes {disponible}, necesitas {cantidad} "
                f"y te faltan {faltante}."
            )
        return 0

    precio_unitario = PRECIOS_VENTA[producto]
    total = precio_unitario * cantidad
    inventario[producto] -= cantidad
    dinero += total

    if mostrar_mensaje:
        print(
            f"Venta completada: {cantidad} de {obtener_nombre(producto)} "
            f"a ${precio_unitario} por unidad."
        )
        print(f"Total obtenido: ${total}. Saldo actual: ${dinero}.")

    return total
