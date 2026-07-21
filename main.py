from comandos import procesar_comando


print("=" * 45)
print("          FORGE OS")
print(" Sistema de Automatización Industrial")
print("             v0.2")
print("=" * 45)

print("\nEscribe 'ayuda' para ver los comandos.\n")

while True:
    comando = input("FORGE > ").strip().lower()
    if not procesar_comando(comando):
        break
