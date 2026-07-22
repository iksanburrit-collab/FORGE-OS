"""Ventana principal Tkinter de FORGE OS."""

import tkinter as tk
from tkinter import messagebox, ttk

from automatizacion import automatizacion_activa
from comandos import mostrar_progreso
from config import (
    COSTOS_CONSTRUCCION,
    PRECIOS_COMPRA,
    PRECIOS_VENTA,
    VERSION_JUEGO,
    obtener_nombre,
)
from inventario import inventario
from maquinas import maquinas
from mejoras import obtener_reporte_mejoras
from objetivos import obtener_estado_objetivos
from persistencia import autoguardado_habilitado, guardar_partida
from recetas import RECETAS

from interfaz.adaptadores import (
    ControladorGUI,
    formatear_costo,
    formatear_energia,
    formatear_inventario,
    formatear_maquinas,
    formatear_objetivos,
    formatear_progreso,
    obtener_snapshot,
    validar_cantidad,
)


class VentanaPrincipal:
    def __init__(self, raiz, controlador=None):
        self.raiz = raiz
        self.controlador = controlador or ControladorGUI()
        self.raiz.title(f"FORGE OS v{VERSION_JUEGO}")
        self.raiz.geometry("1000x650")
        self.raiz.minsize(780, 520)
        self.raiz.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._crear_estilos()
        self._crear_widgets()
        self.actualizar_interfaz()
        self.registrar("FORGE OS listo.")

    def _crear_estilos(self):
        estilo = ttk.Style(self.raiz)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 16, "bold"))
        estilo.configure("Estado.TLabel", font=("Segoe UI", 10, "bold"))

    def _crear_widgets(self):
        principal = ttk.Frame(self.raiz, padding=10)
        principal.pack(fill="both", expand=True)

        encabezado = ttk.Frame(principal)
        encabezado.pack(fill="x", pady=(0, 8))
        ttk.Label(encabezado, text=f"FORGE OS v{VERSION_JUEGO}", style="Titulo.TLabel").pack(side="left")
        self.estado_var = tk.StringVar()
        ttk.Label(encabezado, textvariable=self.estado_var, style="Estado.TLabel").pack(side="right")

        paneles = ttk.PanedWindow(principal, orient="horizontal")
        paneles.pack(fill="both", expand=True)
        izquierda = ttk.Frame(paneles)
        derecha = ttk.Frame(paneles)
        paneles.add(izquierda, weight=1)
        paneles.add(derecha, weight=2)

        self.inventario_tabla = self._crear_tabla(izquierda, "Inventario", ("Recurso", "Cantidad"))
        self.inventario_tabla.master.pack(fill="both", expand=True, pady=(0, 6))
        self.energia_tabla = self._crear_tabla(izquierda, "Energía", ("Concepto", "Valor"))
        self.energia_tabla.master.pack(fill="both", expand=True)

        self.maquinas_tabla = self._crear_tabla(derecha, "Máquinas", ("Máquina", "Cantidad", "Nivel", "Efecto"))
        self.maquinas_tabla.master.pack(fill="both", expand=True, pady=(0, 6))

        registro_marco = ttk.LabelFrame(derecha, text="Registro de actividad", padding=5)
        registro_marco.pack(fill="both", expand=True)
        self.registro = tk.Text(registro_marco, height=10, wrap="word", state="disabled")
        barra = ttk.Scrollbar(registro_marco, orient="vertical", command=self.registro.yview)
        self.registro.configure(yscrollcommand=barra.set)
        self.registro.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        acciones = ttk.LabelFrame(principal, text="Acciones principales", padding=6)
        acciones.pack(fill="x", pady=(8, 4))
        botones = (
            ("Avanzar turno", self.avanzar_turno),
            ("Generar energía", self.generar_energia),
            ("Automatización", self.alternar_automatizacion),
            ("Guardar", self.guardar),
            ("Cargar", self.cargar),
            ("Nueva partida", self.nueva_partida),
            ("Actualizar", self.actualizar_interfaz),
            ("Salir", self.cerrar),
        )
        for columna, (texto, comando) in enumerate(botones):
            ttk.Button(acciones, text=texto, command=comando).grid(row=0, column=columna, padx=2, pady=2, sticky="ew")
            acciones.columnconfigure(columna, weight=1)

        secundarias = ttk.Frame(principal)
        secundarias.pack(fill="x")
        for texto, comando in (
            ("Construir", self.abrir_construccion),
            ("Fabricar", self.abrir_fabricacion),
            ("Fundir", self.abrir_fundicion),
            ("Mercado", self.abrir_mercado),
            ("Mejoras", self.abrir_mejoras),
            ("Objetivos", self.abrir_objetivos),
            ("Progreso", self.abrir_progreso),
            ("Recetas", self.abrir_recetas),
        ):
            ttk.Button(secundarias, text=texto, command=comando).pack(side="left", fill="x", expand=True, padx=2)

    @staticmethod
    def _crear_tabla(padre, titulo, columnas):
        marco = ttk.LabelFrame(padre, text=titulo, padding=5)
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=6)
        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=110, anchor="center")
        tabla.pack(fill="both", expand=True)
        return tabla

    @staticmethod
    def _llenar_tabla(tabla, filas):
        tabla.delete(*tabla.get_children())
        for fila in filas:
            tabla.insert("", "end", values=fila)

    def actualizar_interfaz(self):
        snapshot = obtener_snapshot()
        auto = "Activa" if snapshot["automatizacion"] else "Desactivada"
        self.estado_var.set(f"Saldo: ${snapshot['saldo']}   Turnos: {snapshot['turnos']}   Automatización: {auto}")
        self._llenar_tabla(self.inventario_tabla, formatear_inventario(snapshot["inventario"]))
        self._llenar_tabla(self.maquinas_tabla, formatear_maquinas(snapshot["maquinas"], snapshot["niveles"]))
        self._llenar_tabla(self.energia_tabla, formatear_energia(snapshot["energia"]))
        return snapshot

    def registrar(self, mensaje):
        self.registro.configure(state="normal")
        self.registro.insert("end", mensaje.rstrip() + "\n")
        self.registro.see("end")
        self.registro.configure(state="disabled")

    def _ejecutar(self, accion, *args):
        try:
            ok, mensaje, reporte = accion(*args)
            self.registrar(mensaje)
            self.actualizar_interfaz()
            return ok, mensaje, reporte
        except Exception:
            mensaje = "No se pudo completar la acción. El estado se conserva."
            self.registrar(mensaje)
            messagebox.showerror("FORGE OS", mensaje, parent=self.raiz)
            return False, mensaje, None

    def avanzar_turno(self):
        return self._ejecutar(self.controlador.avanzar_turno)

    def generar_energia(self):
        return self._ejecutar(self.controlador.generar_energia)

    def alternar_automatizacion(self):
        return self._ejecutar(self.controlador.alternar_automatizacion)

    def guardar(self):
        return self._ejecutar(self.controlador.guardar)

    def cargar(self):
        ok, mensaje, reporte = self._ejecutar(self.controlador.cargar)
        if not ok:
            messagebox.showwarning("Cargar partida", mensaje, parent=self.raiz)
        return ok, mensaje, reporte

    def nueva_partida(self):
        confirmada = messagebox.askyesno("Nueva partida", "¿Reiniciar todo el progreso?", parent=self.raiz)
        return self._ejecutar(self.controlador.nueva_partida, confirmada)

    def cerrar(self):
        if autoguardado_habilitado():
            resultado = guardar_partida()
            if not resultado["ok"]:
                messagebox.showwarning("Autoguardado", resultado["mensaje"], parent=self.raiz)
        self.raiz.destroy()

    def _dialogo_operacion(self, titulo, opciones, accion, descripcion=None):
        ventana = tk.Toplevel(self.raiz)
        ventana.title(titulo)
        ventana.transient(self.raiz)
        ventana.resizable(True, False)
        marco = ttk.Frame(ventana, padding=12)
        marco.pack(fill="both", expand=True)
        if descripcion:
            ttk.Label(marco, text=descripcion, wraplength=520).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(marco, text="Producto:").grid(row=1, column=0, sticky="w")
        seleccion = tk.StringVar(value=next(iter(opciones)))
        combo = ttk.Combobox(marco, textvariable=seleccion, values=list(opciones), state="readonly", width=42)
        combo.grid(row=1, column=1, sticky="ew")
        ttk.Label(marco, text="Cantidad:").grid(row=2, column=0, sticky="w", pady=6)
        cantidad_var = tk.StringVar(value="1")
        ttk.Entry(marco, textvariable=cantidad_var).grid(row=2, column=1, sticky="ew", pady=6)
        resultado_var = tk.StringVar()
        ttk.Label(marco, textvariable=resultado_var, wraplength=500).grid(row=3, column=0, columnspan=2, sticky="w")

        def ejecutar():
            cantidad, error = validar_cantidad(cantidad_var.get())
            if error:
                resultado_var.set(error)
                self.registrar(error)
                return
            clave = opciones[seleccion.get()]
            ok, mensaje, _ = self._ejecutar(accion, clave, cantidad)
            resultado_var.set(mensaje)
            if ok:
                ventana.lift()

        ttk.Button(marco, text="Ejecutar", command=ejecutar).grid(row=4, column=0, columnspan=2, pady=(10, 0))
        marco.columnconfigure(1, weight=1)
        return ventana

    def abrir_construccion(self):
        opciones = {f"{obtener_nombre(tipo)} — {formatear_costo(costo)} — actual: {maquinas[tipo]}": tipo for tipo, costo in COSTOS_CONSTRUCCION.items()}
        return self._dialogo_operacion("Construir", opciones, lambda tipo, cantidad: self._construir_varias(tipo, cantidad))

    def _construir_varias(self, tipo, cantidad):
        construidas = 0
        for _ in range(cantidad):
            ok, _, _ = self.controlador.construir(tipo)
            if not ok:
                break
            construidas += 1
        return bool(construidas), (f"Construidas {construidas} de {obtener_nombre(tipo)}." if construidas else "Recursos insuficientes para construir."), construidas

    def abrir_fabricacion(self):
        productos = {producto: producto for clave, receta in RECETAS.items() if clave != "lingote" for producto in receta["produce"]}
        return self._dialogo_operacion("Fabricar", productos, self.controlador.fabricar)

    def abrir_fundicion(self):
        receta = RECETAS["lingote"]
        opciones = {obtener_nombre(recurso): recurso for recurso in receta["consume"]}
        return self._dialogo_operacion("Fundición manual", opciones, self.controlador.fundir, "La fundición manual es independiente de la automatización por turnos.")

    def abrir_mercado(self):
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Mercado")
        cuaderno = ttk.Notebook(ventana)
        cuaderno.pack(fill="both", expand=True, padx=8, pady=8)
        for titulo, catalogo, accion in (("Comprar", PRECIOS_COMPRA, self.controlador.comprar), ("Vender", PRECIOS_VENTA, self.controlador.vender)):
            pagina = ttk.Frame(cuaderno, padding=8)
            cuaderno.add(pagina, text=titulo)
            opciones = {f"{obtener_nombre(p)} — ${precio}": p for p, precio in catalogo.items()}
            boton = ttk.Button(pagina, text=f"Abrir {titulo.lower()}", command=lambda t=titulo, o=opciones, a=accion: self._dialogo_operacion(t, o, a))
            boton.pack(padx=30, pady=20)
        ttk.Label(ventana, text=f"Saldo actual: ${self.actualizar_interfaz()['saldo']}").pack(pady=(0, 8))
        return ventana

    def abrir_mejoras(self):
        reporte = obtener_reporte_mejoras()
        opciones = {}
        for tipo, datos in reporte.items():
            siguiente = "nivel máximo" if datos["en_nivel_maximo"] else f"nivel {datos['siguiente_nivel']}, {formatear_costo(datos['costo_siguiente'])}"
            opciones[f"{obtener_nombre(tipo)} — nivel {datos['nivel_actual']} — {siguiente}"] = tipo
        return self._dialogo_operacion("Mejoras", opciones, lambda tipo, cantidad: self.controlador.mejorar(tipo), "La cantidad se ignora: cada acción mejora un nivel compartido.")

    def _abrir_texto(self, titulo, lineas):
        ventana = tk.Toplevel(self.raiz)
        ventana.title(titulo)
        texto = tk.Text(ventana, width=75, height=22, wrap="word")
        barra = ttk.Scrollbar(ventana, command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        texto.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        barra.pack(side="right", fill="y", pady=8)
        texto.insert("1.0", "\n".join(lineas))
        texto.configure(state="disabled")
        return ventana

    def abrir_objetivos(self):
        return self._abrir_texto("Objetivos", formatear_objetivos(obtener_estado_objetivos()))

    def abrir_progreso(self):
        reporte = mostrar_progreso(mostrar=False)
        return self._abrir_texto("Progreso", [f"{nombre}: {valor}" for nombre, valor in formatear_progreso(reporte)])

    def abrir_recetas(self):
        lineas = []
        for receta in RECETAS.values():
            consume = ", ".join(f"{n} {obtener_nombre(r)}" for r, n in receta["consume"].items())
            produce = ", ".join(f"{n} {obtener_nombre(r)}" for r, n in receta["produce"].items())
            lineas.append(f"{produce} ← {consume}")
        return self._abrir_texto("Recetas", lineas)


def iniciar_interfaz():
    raiz = tk.Tk()
    VentanaPrincipal(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
