# FORGE OS

Simulador industrial por consola inspirado en juegos de automatización como
Factorio. Permite obtener recursos, fundir materiales, fabricar productos y
construir máquinas mediante comandos.

## Requisitos

- Python 3.8 o posterior.
- No requiere dependencias externas.

## Ejecución

Desde la carpeta del proyecto:

```bash
python main.py
```

## Comandos

| Comando | Descripción |
| --- | --- |
| `turno` | Avanza un turno y produce recursos. |
| `inventario` o `inv` | Muestra los recursos y productos disponibles. |
| `maquinas` | Muestra las máquinas construidas. |
| `energia` | Muestra la generación y el consumo energético actual. |
| `generar energia` | Consume carbón y añade energía a la reserva. |
| `comprar` | Abre la tienda de materiales y máquinas. |
| `automatizacion` | Muestra el estado de automatización. |
| `automatizacion activar` | Activa la fundición automática. |
| `automatizacion desactivar` | Desactiva la automatización. |
| `fundir` | Inicia la fundición interactiva. |
| `fundir <cantidad> <recurso>` | Funde una cantidad concreta. |
| `fabricar <cantidad> <producto>` | Fabrica placas o engranajes. |
| `recetas` | Muestra todas las recetas disponibles. |
| `construir <maquina>` | Construye una máquina. |
| `ayuda` | Muestra la ayuda dentro del juego. |
| `salir` | Cierra el simulador. |

Ejemplos:

```text
fundir 3 hierro
fabricar 2 engranajes
fabricar 5 placas
construir mina de hierro
construir generador carbon
generar energia
comprar
automatizacion activar
turno
```

La fundición manual con `fundir` siempre está disponible. De forma opcional,
`automatizacion activar` permite que cada fundidora con energía procese como
máximo un lote de lingotes durante el turno. `automatizacion desactivar`
restaura el comportamiento exclusivamente manual y evita que las fundidoras
reserven energía. El comando `energia` distingue entre el consumo potencial
de todas las máquinas y el consumo efectivo del próximo turno.

Cada partida comienza con un generador de carbón y una reserva inicial de 10
MW. `generar energia` consume una unidad de carbón por generador activo y
añade 10 MW por generador a la reserva acumulativa. Al avanzar el turno se
descuenta la energía utilizada. Si no alcanza, se priorizan las minas de
carbón, después las minas de hierro y finalmente las fundidoras.

El comando `comprar` abre un menú numerado con materiales, minas, fundidoras y
generadores. Comprar utiliza el saldo obtenido mediante ventas; construir
continúa utilizando materiales.

## Estructura del proyecto

```text
main.py         Punto de entrada del juego
comandos.py     Procesamiento de comandos de consola
juego.py        Lógica de turnos, fundición y fabricación
energia.py      Cálculo y asignación de energía
automatizacion.py Estado opcional de automatización
inventario.py   Estado y operaciones del inventario
maquinas.py     Construcción y estado de las máquinas
recetas.py      Definición de recetas
config.py       Nombres, alias y costes
```

## Estado local

Los archivos generados por Python, la configuración del editor, las variables
de entorno y `datos.json` están excluidos del repositorio mediante
`.gitignore`.
