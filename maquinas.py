from config import COSTOS_CONSTRUCCION, obtener_nombre
from inventario import inventario

maquinas = {
    "mina_hierro": 1,
    "mina_carbon": 1,
    "fundidora": 1,
    "generador_carbon": 1,
}


def mostrar_maquinas(mostrar=True):
    if mostrar:
        print("\nMáquinas:")
        for maquina in (
            "mina_hierro",
            "mina_carbon",
            "fundidora",
            "generador_carbon",
        ):
            print(f"{obtener_nombre(maquina)}: {maquinas[maquina]}")

    return maquinas.copy()


def construir_maquina(tipo, costo=None, mostrar=True):
    if tipo not in maquinas or tipo not in COSTOS_CONSTRUCCION:
        if mostrar:
            print("No reconozco esa máquina para construir.")
        return False

    costo = costo if costo is not None else COSTOS_CONSTRUCCION[tipo]
    recursos_necesarios = costo if isinstance(costo, dict) else {"lingotes": costo}
    faltantes = {
        recurso: cantidad - inventario.get(recurso, 0)
        for recurso, cantidad in recursos_necesarios.items()
        if inventario.get(recurso, 0) < cantidad
    }

    if faltantes:
        if mostrar:
            print("No hay suficientes recursos para construir la máquina. Faltan:")
            for recurso, cantidad in faltantes.items():
                print(f" - {cantidad} de {obtener_nombre(recurso)}")
        return False

    for recurso, cantidad in recursos_necesarios.items():
        inventario[recurso] -= cantidad
    maquinas[tipo] += 1

    if mostrar:
        print(f"Máquina construida: {obtener_nombre(tipo)}.")
        recursos = ", ".join(
            f"{cantidad} de {obtener_nombre(recurso)}"
            for recurso, cantidad in recursos_necesarios.items()
        )
        print(f"Se han gastado {recursos}.")

    return True
