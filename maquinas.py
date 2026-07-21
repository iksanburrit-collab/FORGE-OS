from config import COSTOS_CONSTRUCCION, obtener_nombre
from inventario import inventario

maquinas = {
    "mina_hierro": 1,
    "mina_carbon": 1,
    "fundidora": 1,
}


def mostrar_maquinas(mostrar=True):
    if mostrar:
        print("\nMáquinas:")
        for maquina in ("mina_hierro", "mina_carbon", "fundidora"):
            print(f"{obtener_nombre(maquina)}: {maquinas[maquina]}")

    return maquinas.copy()


def construir_maquina(tipo, costo=None, mostrar=True):
    costo = costo if costo is not None else COSTOS_CONSTRUCCION[tipo]

    if inventario["lingotes"] >= costo:
        inventario["lingotes"] -= costo
        maquinas[tipo] += 1
        if mostrar:
            print(f"Se ha construido una nueva {obtener_nombre(tipo)}.")
            print(f"Se han gastado {costo} lingotes.")
    else:
        if mostrar:
            print(
                f"No hay suficientes lingotes para construir la máquina."
                f" Se necesitan {costo} lingotes, pero solo hay {inventario['lingotes']}."
            )
