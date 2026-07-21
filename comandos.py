from config import obtener_nombre, normalizar_clave
from inventario import mostrar_inventario
from maquinas import mostrar_maquinas, construir_maquina
from mercado import mostrar_mercado, mostrar_saldo, vender
from juego import avanzar_turno, fabricar, fundir, mostrar_recetas


def mostrar_ayuda():
    print("Comandos disponibles:")
    print(" - turno: Avanzar un turno")
    print(" - inventario (inv): Mostrar el inventario")
    print(" - maquinas: Mostrar las máquinas")
    print(f" - construir {obtener_nombre('mina_hierro')}: Cuesta 3 lingotes")
    print(f" - construir {obtener_nombre('mina_carbon')}: Cuesta 2 lingotes")
    print(f" - construir {obtener_nombre('fundidora')}: Cuesta 4 lingotes")
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
            if clave in {"mina_hierro", "mina_carbon", "fundidora"}:
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
