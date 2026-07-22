import sys


def iniciar_juego():
    """Abre la única modalidad jugable: la interfaz gráfica."""
    from interfaz.ventana_principal import iniciar_interfaz

    iniciar_interfaz()


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1:] == ["--gui"]:
        iniciar_juego()
    else:
        print("Uso: python main.py [--gui]")
