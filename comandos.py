from automatizacion import (
    activar_automatizacion,
    automatizacion_activa,
    desactivar_automatizacion,
    obtener_estado_automatizacion,
    obtener_maquinas_efectivas,
)
from config import obtener_nombre, normalizar_clave
from energia import generar_energia, obtener_reporte_energia
from inventario import inventario, mostrar_inventario
from maquinas import construir_maquina, maquinas, mostrar_maquinas
from mercado import (
    comprar,
    mostrar_mercado,
    mostrar_saldo,
    obtener_catalogo_compra,
    vender,
)
from mejoras import mejorar_maquina, obtener_reporte_mejoras
from juego import avanzar_turno, fabricar, fundir, mostrar_recetas


def mostrar_ayuda():
    print("Comandos disponibles:")
    print(" - turno: Avanzar un turno")
    print(" - inventario (inv): Mostrar el inventario")
    print(" - maquinas: Mostrar las máquinas")
    print(f" - construir {obtener_nombre('mina_hierro')}: Cuesta 3 lingotes")
    print(f" - construir {obtener_nombre('mina_carbon')}: Cuesta 2 lingotes")
    print(f" - construir {obtener_nombre('fundidora')}: Cuesta 4 lingotes")
    print(
        " - construir generador carbon: "
        "Cuesta 12 lingotes y 2 engranajes"
    )
    print(" - fundir: Fundir con una receta por defecto")
    print(
        " - fundir <cantidad> <recurso>: Fundir recursos específicos, "
        "por ejemplo: fundir 3 hierro"
    )
    print(" - fabricar <cantidad> <producto>: Fabricar un producto")
    print(" - recetas: Mostrar las recetas disponibles")
    print(" - vender <cantidad> <producto>: Vender productos")
    print(" - saldo: Mostrar el dinero disponible")
    print(" - mercado: Mostrar productos y precios de venta")
    print(" - comprar: Abrir el menú de compra")
    print(" - energia: Mostrar generación y consumo de energía")
    print(" - generar energia: Consumir carbón para almacenar energía")
    print(" - automatizacion: Mostrar el estado de automatización")
    print(" - automatizacion activar: Activar la fundición automática")
    print(" - automatizacion desactivar: Desactivar la automatización")
    print(" - mejoras: Mostrar niveles, efectos y costos de mejora")
    print(" - mejorar <maquina>: Mejorar todas las máquinas de ese tipo")
    print(" - ayuda: Mostrar esta ayuda")
    print(" - salir: Salir del juego")


def procesar_comando(comando):
    comando = comando.strip().lower()

    if comando == "turno":
        avanzar_turno()
    elif comando.startswith("vender"):
        partes = comando.split()
        if len(partes) != 3:
            print("Formato inválido. Usa: vender <cantidad> <producto>")
            return True

        try:
            cantidad = int(partes[1])
        except ValueError:
            print("La cantidad debe ser un número entero mayor que cero.")
            return True

        producto = normalizar_clave(partes[2])
        vender(producto, cantidad)
    elif comando == "saldo":
        mostrar_saldo()
    elif comando == "mercado":
        mostrar_mercado()
    elif comando == "comprar":
        mostrar_menu_compra()
    elif comando == "energia":
        mostrar_energia()
    elif comando == "generar energia":
        ejecutar_generacion_energia()
    elif comando in {"automatizacion", "automatización"}:
        mostrar_automatizacion()
    elif comando in {
        "automatizacion activar",
        "automatización activar",
    }:
        reporte = activar_automatizacion()
        if reporte["cambio"]:
            print("Automatización activada.")
        else:
            print("La automatización ya estaba activada.")
    elif comando in {
        "automatizacion desactivar",
        "automatización desactivar",
    }:
        reporte = desactivar_automatizacion()
        if reporte["cambio"]:
            print("Automatización desactivada.")
        else:
            print("La automatización ya estaba desactivada.")
    elif comando.startswith(("automatizacion", "automatización")):
        print(
            "Formato inválido. Usa: automatizacion, "
            "automatizacion activar o automatizacion desactivar"
        )
    elif comando == "mejoras":
        mostrar_mejoras()
    elif comando.startswith("mejorar"):
        partes = comando.split()
        if len(partes) < 2:
            print("Formato inválido. Usa: mejorar <maquina>")
            return True

        tipo = normalizar_clave(" ".join(partes[1:]))
        reporte = mejorar_maquina(tipo)
        mostrar_resultado_mejora(reporte)
    elif comando.startswith("fabricar"):
        partes = comando.split()
        if len(partes) != 3:
            print("Formato inválido. Usa: fabricar <cantidad> <producto>")
            return True

        try:
            cantidad = int(partes[1])
        except ValueError:
            print("La cantidad debe ser un número entero mayor que cero.")
            return True

        producto = normalizar_clave(partes[2])
        fabricar(producto, cantidad)
    elif comando == "recetas":
        mostrar_recetas()
    elif comando.startswith("fundir"):
        partes = comando.split()

        if len(partes) == 1:
            entrada_cantidad = input("¿Cuántos quieres fundir? ").strip()
            if not entrada_cantidad:
                fundir()
                return True

            try:
                cantidad = int(entrada_cantidad)
            except ValueError:
                print("Cantidad inválida.")
                return True

            recurso = input("¿Qué recurso quieres fundir? ").strip().lower()
            if not recurso:
                print("Debes indicar un recurso.")
                return True

            recurso = normalizar_clave(recurso)
            fundir(recurso=recurso, cantidad=cantidad)
        elif len(partes) == 3:
            try:
                cantidad = int(partes[1])
            except ValueError:
                print("La cantidad debe ser un número.")
                return True

            recurso = normalizar_clave(partes[2])
            fundir(recurso=recurso, cantidad=cantidad)
        else:
            print("Formato inválido. Usa: fundir <cantidad> <recurso>")
    elif comando in {"inventario", "inv"}:
        mostrar_inventario()
    elif comando == "maquinas":
        mostrar_maquinas()
    elif comando.startswith("construir"):
        partes = comando.split()
        if len(partes) >= 2:
            nombre_maquina = " ".join(partes[1:])
            clave = normalizar_clave(nombre_maquina)
            if clave in {
                "mina_hierro",
                "mina_carbon",
                "fundidora",
                "generador_carbon",
            }:
                construir_maquina(clave)
            else:
                print("No reconozco esa máquina para construir.")
        else:
            print("Formato inválido. Usa: construir mina de hierro")
    elif comando == "ayuda":
        mostrar_ayuda()
    elif comando == "salir":
        print("Saliendo del juego...")
        return False
    else:
        print("Opción no válida. Por favor, seleccione una opción válida.")

    return True


def mostrar_energia(mostrar=True):
    reporte_potencial = obtener_reporte_energia(maquinas)
    maquinas_efectivas = obtener_maquinas_efectivas(maquinas)
    reporte = obtener_reporte_energia(maquinas_efectivas)
    reporte["consumo_potencial"] = reporte_potencial["consumo_maximo"]
    reporte["consumo_efectivo"] = reporte["consumo_maximo"]

    if mostrar:
        print("\nEnergía:")
        print(f"Energía almacenada: {reporte['energia_disponible']} MW")
        print(
            f"Capacidad por generación: "
            f"{reporte['capacidad_generacion']} MW"
        )
        print(
            "Consumo potencial (todas las máquinas): "
            f"{reporte['consumo_potencial']} MW"
        )
        print(
            "Consumo efectivo del próximo turno: "
            f"{reporte['consumo_efectivo']} MW"
        )
        estado = "activa" if automatizacion_activa() else "desactivada"
        print(f"Automatización: {estado}")
        if reporte["deficit"]:
            print(f"Déficit: {reporte['deficit']} MW")
        else:
            disponible = reporte["energia_disponible"] - reporte["consumo_maximo"]
            print(f"Energía disponible: {disponible} MW")
        generadores = sum(reporte["generadores"].values())
        print(f"Generadores: {generadores}")
        print("Consumo por tipo de máquina:")
        for tipo, consumo in reporte["consumo_por_tipo"].items():
            print(
                f" - {obtener_nombre(tipo)}: {consumo['consumo_total']} MW "
                f"({consumo['maquinas']} x {consumo['consumo_unitario']} MW)"
            )

    return reporte


def mostrar_automatizacion(mostrar=True):
    estado = obtener_estado_automatizacion()
    maquinas_efectivas = obtener_maquinas_efectivas(maquinas)
    reporte_energia = obtener_reporte_energia(maquinas_efectivas)
    reporte = {
        **estado,
        "fundidoras_construidas": maquinas.get("fundidora", 0),
        "fundidoras_energizables": reporte_energia["maquinas_activas"].get(
            "fundidora",
            0,
        ),
    }

    if mostrar:
        estado_visible = "activada" if reporte["activa"] else "desactivada"
        print("\nAutomatización:")
        print(f"Estado: {estado_visible}")
        print("Procesos disponibles: fundición de lingotes")
        print(f"Fundidoras construidas: {reporte['fundidoras_construidas']}")
        print(
            "Fundidoras con energía disponible: "
            f"{reporte['fundidoras_energizables']}"
        )

    return reporte


def ejecutar_generacion_energia(mostrar=True):
    reporte = generar_energia(maquinas, inventario)

    if mostrar:
        if reporte["energia_generada"]:
            print(
                f"Energía generada: +{reporte['energia_generada']} MW "
                f"({reporte['carbon_consumido']} de Carbón consumido)."
            )
            print(f"Energía almacenada: {reporte['energia_almacenada']} MW")
        elif not reporte["generadores_disponibles"]:
            print("No hay generadores de carbón construidos.")
        else:
            print("No hay carbón suficiente para generar energía.")

    return reporte


def mostrar_menu_compra():
    catalogo = obtener_catalogo_compra()
    opciones = list(catalogo)

    print("\n===== TIENDA =====")
    mostrar_saldo()
    for numero, producto in enumerate(opciones, start=1):
        print(
            f" {numero}. {obtener_nombre(producto)} "
            f"- ${catalogo[producto]}"
        )
    print(" 0. Cancelar")

    seleccion = input("Elige qué comprar: ").strip()
    if seleccion == "0":
        print("Compra cancelada.")
        return 0

    try:
        indice = int(seleccion) - 1
    except ValueError:
        print("Selección inválida.")
        return 0

    if indice < 0 or indice >= len(opciones):
        print("Selección inválida.")
        return 0

    entrada_cantidad = input("Cantidad: ").strip()
    try:
        cantidad = int(entrada_cantidad)
    except ValueError:
        print("La cantidad debe ser un número entero mayor que cero.")
        return 0

    return comprar(opciones[indice], cantidad)


def _formatear_efecto(efecto):
    return f"{efecto['cantidad']} {efecto['unidad']}"


def _formatear_costo(costo):
    partes = []
    for recurso, cantidad in costo.items():
        if recurso == "dinero":
            partes.append(f"${cantidad}")
        else:
            partes.append(f"{cantidad} de {obtener_nombre(recurso)}")
    return ", ".join(partes)


def mostrar_mejoras(mostrar=True):
    reporte = obtener_reporte_mejoras()

    if mostrar:
        print("\n===== MEJORAS DE MÁQUINAS =====")
        for tipo, datos in reporte.items():
            print(f"\n{obtener_nombre(tipo)}")
            print(
                f" Nivel: {datos['nivel_actual']}/{datos['nivel_maximo']}"
            )
            print(f" Efecto actual: {_formatear_efecto(datos['efecto_actual'])}")
            if datos["en_nivel_maximo"]:
                print(" Nivel máximo alcanzado.")
            else:
                print(
                    " Siguiente nivel: "
                    f"{_formatear_efecto(datos['efecto_siguiente'])}"
                )
                print(
                    " Costo: "
                    f"{_formatear_costo(datos['costo_siguiente'])}"
                )

    return reporte


def mostrar_resultado_mejora(reporte):
    if reporte["exito"]:
        print(
            f"Mejora completada: {obtener_nombre(reporte['tipo'])} "
            f"ahora está en nivel {reporte['nivel_actual']}."
        )
        return

    if reporte["motivo"] == "tipo_invalido":
        print("No reconozco ese tipo de máquina para mejorar.")
        return

    if reporte["motivo"] == "nivel_maximo":
        print(
            f"{obtener_nombre(reporte['tipo'])} ya está en el nivel máximo."
        )
        return

    print("No se puede completar la mejora. Faltan:")
    for recurso, cantidad in reporte["faltantes"].items():
        if recurso == "dinero":
            print(f" - ${cantidad}")
        else:
            print(f" - {cantidad} de {obtener_nombre(recurso)}")
