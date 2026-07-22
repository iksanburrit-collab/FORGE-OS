from comandos import procesar_comando


def iniciar_juego():
    print("=" * 45)
    print("          FORGE OS")
    print(" Sistema de Automatización Industrial")
    print("             v0.5")
    print("=" * 45)

    print("\nEscribe 'ayuda' para ver los comandos.\n")

    while True:
        comando = input("FORGE > ").strip().lower()

        if not procesar_comando(comando):
            break


if __name__ == "__main__":
    iniciar_juego()
