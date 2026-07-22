# FORGE OS v1.0

Simulador industrial de gestión con interfaz gráfica. Permite
administrar inventario, máquinas, energía, automatización, fabricación,
mercado, mejoras, objetivos, eventos y partidas guardadas.

## Requisitos

- Python 3.8 o posterior.
- No requiere dependencias externas.

## Ejecución

Desde la carpeta del proyecto:

```bash
python main.py
```

El juego abre directamente su interfaz gráfica Tkinter. `--gui` se conserva
como alias opcional por compatibilidad:

```bash
python main.py --gui
```

FORGE OS ya no ofrece un modo de juego por consola.

## Controles gráficos

La ventana principal muestra saldo, turnos, automatización, inventario,
máquinas, niveles, efectos y estado energético. Su registro de actividad
recoge resultados, advertencias y errores sin mostrar tracebacks técnicos.

Los botones principales permiten avanzar turno, generar energía, cambiar la
automatización, guardar, cargar, iniciar una partida, actualizar y salir. Las
ventanas secundarias permiten construir, fabricar, fundir manualmente,
comprar, vender, mejorar y consultar objetivos, progreso y recetas.

`Nueva partida` solicita confirmación gráfica. Cargar un archivo inexistente o
inválido conserva el estado actual. Al cerrar la GUI se respeta la regla de
autoguardado vigente.

La fundición manual está disponible desde su ventana propia. La automatización
opcional permite que cada fundidora con energía procese lingotes al avanzar el
turno. Al desactivarla, las fundidoras no reservan energía. El panel energético
distingue el consumo potencial del consumo efectivo.

Cada partida comienza con un generador de carbón y una reserva inicial de 10
MW. El botón `Generar energía` consume una unidad de carbón por generador y
añade 10 MW por generador a la reserva acumulativa. Al avanzar el turno se
descuenta la energía utilizada. Si no alcanza, se priorizan las minas de
carbón, después las minas de hierro y finalmente las fundidoras.

La ventana de mercado permite comprar materiales, minas, fundidoras y
generadores usando el saldo obtenido mediante ventas. Construir continúa
utilizando materiales.

## Mejoras de máquinas

Todas las máquinas de un mismo tipo comparten nivel, desde 1 hasta 3. Al
mejorar una mina aumenta su producción por turno; las fundidoras automáticas
procesan más lotes y los generadores producen más MW. El consumo eléctrico y
el carbón utilizado por cada generador no cambian.

La mejora requiere dinero y materiales. La operación es atómica: si falta
algún requisito, no se descuenta nada ni cambia el nivel. Las máquinas nuevas
heredan automáticamente el nivel vigente de su tipo.

## Guardado de partidas

Los botones `Guardar` y `Cargar` conservan inventario, máquinas, dinero,
energía, automatización y niveles en `datos.json`. Al cerrar la ventana se
realiza un guardado automático cuando está habilitado.

El archivo se guarda localmente junto al proyecto, usa JSON legible y está
excluido de Git. `Nueva partida` solicita confirmación gráfica antes de
reiniciar el progreso.

## Objetivos y eventos

FORGE OS incluye siete objetivos industriales para extracción, máquinas,
lingotes, saldo, mejoras, energía y automatización. Las recompensas se entregan
una sola vez y pueden incluir dinero, recursos o energía.

Las estadísticas de extracción, producción, generación y turnos son
acumulativas: consumir o vender recursos no reduce el progreso histórico. Las
ventanas `Progreso` y `Objetivos` muestran el resumen sin alterar el estado.

Cada cinco turnos ocurre un evento industrial básico: hallazgo de hierro,
subsidio energético, bonificación comercial o mantenimiento. El mantenimiento
nunca puede dejar el saldo por debajo de cero.

## Estructura del proyecto

```text
main.py         Punto de entrada del juego
comandos.py     Reportes y compatibilidad interna de operaciones
interfaz/       Adaptadores sin pantalla y ventanas Tkinter
juego.py        Lógica de turnos, fundición y fabricación
energia.py      Cálculo y asignación de energía
automatizacion.py Estado opcional de automatización
mejoras.py       Niveles y operaciones de mejora
persistencia.py  Guardado, validación y carga atómica
objetivos.py     Metas, estadísticas y recompensas
eventos.py       Eventos industriales periódicos
inventario.py   Estado y operaciones del inventario
maquinas.py     Construcción y estado de las máquinas
recetas.py      Definición de recetas
config.py       Nombres, alias y costes
```

## Limitaciones conocidas

- La interfaz es deliberadamente funcional y no incluye animaciones, mapas,
  cintas transportadoras ni imágenes.
- El juego se actualiza mediante acciones del usuario; no existen procesos en
  segundo plano.
- Las pruebas visuales reales necesitan una sesión de escritorio disponible,
  aunque la lógica y los callbacks se prueban sin abrir ventanas.

## Estado local

Los archivos generados por Python, la configuración del editor, las variables
de entorno y `datos.json` están excluidos del repositorio mediante
`.gitignore`.
