from comandos import procesar_comando
from config import VERSION_JUEGO
from persistencia import existe_partida_guardada


def iniciar_juego():
    print("=" * 45)
    print("          FORGE OS")
    print(" Sistema de Automatización Industrial")
    print(f"             v{VERSION_JUEGO}")
    print("=" * 45)

    print("\nEscribe 'ayuda' para ver los comandos.\n")
    if existe_partida_guardada():
        print("Hay una partida guardada. Usa 'cargar' para recuperarla.\n")

    while True:
        comando = input("FORGE > ").strip().lower()

        if not procesar_comando(comando):
            break


if __name__ == "__main__":
    iniciar_juego()
