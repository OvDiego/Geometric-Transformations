import tkinter as tk
from tkinter import ttk
import numpy as np
import math

class AplicacionDibujo:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Dibujo de Figuras Geométricas")

        self.marco_principal = tk.Frame(raiz)
        self.marco_principal.pack(fill=tk.BOTH, expand=True)

        self.lienzo = tk.Canvas(self.marco_principal, width=800, height=600, bg="white")
        self.lienzo.pack(side=tk.RIGHT)

        # Sidebar
        self.barra_lateral = tk.Frame(self.marco_principal, padx=10, pady=10)
        self.barra_lateral.pack(side=tk.LEFT, fill=tk.Y)

        # Figure selection
        marco_figura = ttk.LabelFrame(self.barra_lateral, text="Tipo de Figura")
        marco_figura.pack(fill='x', pady=10)
        self.tipo_figura = tk.StringVar(value="línea")
        for texto in ["línea", "circulo", "triangulo", "cuadrilatero"]:
            ttk.Button(marco_figura, text=texto.capitalize(),
                       command=lambda t=texto: self.seleccionar_figura(t)).pack(fill='x', pady=2)

        # Color selection
        marco_color = ttk.LabelFrame(self.barra_lateral, text="Color de Figura")
        marco_color.pack(fill='x', pady=10)
        self.color = tk.StringVar(value="Azul")
        menu_color = ttk.Combobox(marco_color, textvariable=self.color,
                                  values=["Negro", "Azul", "Rojo"], state="readonly")
        menu_color.current(1)
        menu_color.pack()

        # Mouse position
        self.etiqueta_coord = ttk.Label(self.barra_lateral, text="Posición del mouse: ( , )")
        self.etiqueta_coord.pack(pady=5)

        # Canvas events
        self.lienzo.bind("<Motion>", self.actualizar_pos_mouse)
        self.lienzo.bind("<Button-1>", self.al_clic)

        # Deletion controls
        marco_borrar = ttk.LabelFrame(self.barra_lateral, text="Controles de Borrado")
        marco_borrar.pack(fill='x', pady=10)
        ttk.Button(marco_borrar, text="Borrar Último", command=self.deshacer).pack(fill='x', pady=2)
        ttk.Button(marco_borrar, text="Borrar Todo", command=self.borrar_todo).pack(fill='x', pady=2)

        # Storage for points and drawings
        self.puntos = []
        self.formas_temporales = []
        self.formas_dibujadas = []

    # --- Methods ---
    def seleccionar_figura(self, tipo):
        self.tipo_figura.set(tipo)
        self.puntos = []
        self.borrar_formas_temporales()

    def actualizar_pos_mouse(self, evento):
        self.etiqueta_coord.config(text=f"Posición del mouse: ({evento.x}, {evento.y})")
        self.previsualizar_figura((evento.x, evento.y))

    def al_clic(self, evento):
        self.puntos.append((evento.x, evento.y))
        tipo = self.tipo_figura.get()
        puntos_necesarios = {"línea":2, "circulo":2, "triangulo":3, "cuadrilatero":4}[tipo]

        if len(self.puntos) == puntos_necesarios:
            self.dibujar_figura(self.puntos)
            self.puntos = []
            self.borrar_formas_temporales()

    def borrar_formas_temporales(self):
        for forma in self.formas_temporales:
            self.lienzo.delete(forma)
        self.formas_temporales = []

    def previsualizar_figura(self, punto_actual):
        tipo = self.tipo_figura.get()
        color_previsualizacion = "light gray"
        formas_temp = []
        puntos = self.puntos + [punto_actual]

        self.borrar_formas_temporales()

        if tipo == "línea" and len(puntos)==2:
            formas_temp.append(self.lienzo.create_line(*puntos[0], *puntos[1],
                                                       fill=color_previsualizacion, dash=(3,2)))
        elif tipo=="circulo" and len(puntos)==2:
            x0, y0 = puntos[0]
            x1, y1 = puntos[1]
            r = (((x1-x0)**2 + (y1-y0)**2)**0.5)*0.5
            formas_temp.append(self.lienzo.create_oval(x0-r,y0-r,x0+r,y0+r,
                                                       outline=color_previsualizacion,dash=(3,2)))
        elif tipo=="triangulo" and len(puntos)>=2:
            for i in range(len(puntos)-1):
                formas_temp.append(self.lienzo.create_line(*puntos[i],*puntos[i+1],
                                                           fill=color_previsualizacion,dash=(3,2)))
            if len(puntos)==3:
                formas_temp.append(self.lienzo.create_line(*puntos[2],*puntos[0],
                                                           fill=color_previsualizacion,dash=(3,2)))
        elif tipo=="cuadrilatero" and len(puntos)>=2:
            for i in range(len(puntos)-1):
                formas_temp.append(self.lienzo.create_line(*puntos[i],*puntos[i+1],
                                                           fill=color_previsualizacion,dash=(3,2)))
            if len(puntos)==4:
                formas_temp.append(self.lienzo.create_line(*puntos[3],*puntos[0],
                                                           fill=color_previsualizacion,dash=(3,2)))
        self.formas_temporales = formas_temp

    def dibujar_figura(self, puntos):
        tipo = self.tipo_figura.get()
        mapa_colores = {"Negro":"black","Azul":"blue","Rojo":"red"}
        color = mapa_colores.get(self.color.get(), self.color.get())
        ids = []

        if tipo=="línea":
            ids.append(self.lienzo.create_line(*puntos[0],*puntos[1],fill=color))
        elif tipo=="circulo":
            x0,y0 = puntos[0]
            x1,y1 = puntos[1]
            r = (((x1-x0)**2+(y1-y0)**2)**0.5)*0.5
            ids.append(self.lienzo.create_oval(x0-r,y0-r,x0+r,y0+r,outline=color))
        elif tipo=="triangulo":
            for i in range(2):
                ids.append(self.lienzo.create_line(*puntos[i],*puntos[i+1],fill=color))
            ids.append(self.lienzo.create_line(*puntos[2],*puntos[0],fill=color))
        elif tipo=="cuadrilatero":
            for i in range(3):
                ids.append(self.lienzo.create_line(*puntos[i],*puntos[i+1],fill=color))
            ids.append(self.lienzo.create_line(*puntos[3],*puntos[0],fill=color))

        self.formas_dibujadas.append((ids,puntos))

    def deshacer(self):
        if self.formas_dibujadas:
            ids,_ = self.formas_dibujadas.pop()
            for forma in ids:
                self.lienzo.delete(forma)

    def borrar_todo(self):
        for ids,_ in self.formas_dibujadas:
            for forma in ids:
                self.lienzo.delete(forma)
        self.formas_dibujadas.clear()

# --- Main ---
if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionDibujo(raiz)
    raiz.mainloop()
