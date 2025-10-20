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

        # Deletion controls
        marco_borrar = ttk.LabelFrame(self.barra_lateral, text="Controles de Borrado")
        marco_borrar.pack(fill='x', pady=10)
        ttk.Button(marco_borrar, text="Borrar Último", command=self.deshacer).pack(fill='x', pady=2)
        ttk.Button(marco_borrar, text="Borrar Todo", command=self.borrar_todo).pack(fill='x', pady=2)

        # Translation
        marco_traslacion = ttk.LabelFrame(self.barra_lateral, text="Trasladar Figura")
        marco_traslacion.pack(fill='x', pady=10)
        ttk.Label(marco_traslacion, text="Desplazamiento en X").pack()
        self.entrada_dx = ttk.Entry(marco_traslacion)
        self.entrada_dx.insert(0, "0")
        self.entrada_dx.pack()
        ttk.Label(marco_traslacion, text="Desplazamiento en Y").pack()
        self.entrada_dy = ttk.Entry(marco_traslacion)
        self.entrada_dy.insert(0, "0")
        self.entrada_dy.pack()
        ttk.Button(marco_traslacion, text="Trasladar", command=self.trasladar_figura).pack(fill='x', pady=5)

        # Scaling
        marco_escala = ttk.LabelFrame(self.barra_lateral, text="Escalar Figura")
        marco_escala.pack(fill='x', pady=10)
        ttk.Label(marco_escala, text="Factor de Escalado").pack()
        self.entrada_escala = ttk.Entry(marco_escala)
        self.entrada_escala.insert(0, "1.0")
        self.entrada_escala.pack()
        ttk.Button(marco_escala, text="Escalar", command=self.escalar_figura).pack(fill='x', pady=5)

        # Symmetry
        marco_simetria = ttk.LabelFrame(self.barra_lateral, text="Simetría")
        marco_simetria.pack(fill='x', pady=10)
        ttk.Button(marco_simetria, text="Simetría en Eje X", command=self.simetria_x).pack(fill='x', pady=2)
        ttk.Button(marco_simetria, text="Simetría en Eje Y", command=self.simetria_y).pack(fill='x', pady=2)

        # Rotation
        marco_rotacion = ttk.LabelFrame(self.barra_lateral, text="Rotar Figura")
        marco_rotacion.pack(fill='x', pady=10)
        ttk.Label(marco_rotacion, text="Ángulo (°)").pack()
        self.entrada_angulo = ttk.Entry(marco_rotacion)
        self.entrada_angulo.insert(0, "0")
        self.entrada_angulo.pack()
        ttk.Button(marco_rotacion, text="Rotar", command=self.rotar_figura).pack(fill='x', pady=5)

        # Canvas events
        self.lienzo.bind("<Motion>", self.actualizar_pos_mouse)
        self.lienzo.bind("<Button-1>", self.al_clic)

        # Storage
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

    def trasladar_figura(self):
        if not self.formas_dibujadas:
            return
        try:
            dx = int(self.entrada_dx.get()) * 10
            dy = int(self.entrada_dy.get()) * 10
        except ValueError:
            return
        ids, puntos = self.formas_dibujadas.pop()
        for forma in ids:
            self.lienzo.delete(forma)
        T = np.array([[1,0,dx],[0,1,dy],[0,0,1]])
        nuevos_puntos = [tuple((T @ np.array([[x],[y],[1]])).flatten()[:2].astype(int)) for x,y in puntos]
        self.dibujar_figura(nuevos_puntos)

    def escalar_figura(self):
        if not self.formas_dibujadas:
            return
        try:
            factor = float(self.entrada_escala.get())
        except ValueError:
            return
        ids, puntos = self.formas_dibujadas.pop()
        for forma in ids:
            self.lienzo.delete(forma)
        px, py = puntos[0]
        S = np.array([[factor,0,px*(1-factor)],[0,factor,py*(1-factor)],[0,0,1]])
        nuevos_puntos = [tuple((S @ np.array([[x],[y],[1]])).flatten()[:2].astype(int)) for x,y in puntos]
        self.dibujar_figura(nuevos_puntos)

    def simetria_x(self):
        self.aplicar_simetria(np.array([[1,0,0],[0,-1,0],[0,0,1]]))

    def simetria_y(self):
        self.aplicar_simetria(np.array([[-1,0,0],[0,1,0],[0,0,1]]))

    def aplicar_simetria(self, matriz):
        if not self.formas_dibujadas:
            return
        ids, puntos = self.formas_dibujadas.pop()
        for forma in ids:
            self.lienzo.delete(forma)
        xs, ys = zip(*puntos)
        cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
        T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]])
        T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]])
        M = T2 @ matriz @ T1
        nuevos_puntos = [tuple((M @ np.array([[x],[y],[1]])).flatten()[:2].astype(int)) for x,y in puntos]
        self.dibujar_figura(nuevos_puntos)

    def rotar_figura(self):
        if not self.formas_dibujadas:
            return
        try:
            angulo = float(self.entrada_angulo.get())
        except ValueError:
            return
        rad = math.radians(angulo)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        R = np.array([[cos_a,-sin_a,0],[sin_a,cos_a,0],[0,0,1]])
        ids, puntos = self.formas_dibujadas.pop()
        for forma in ids:
            self.lienzo.delete(forma)
        xs, ys = zip(*puntos)
        cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
        T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]])
        T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]])
        M = T2 @ R @ T1
        nuevos_puntos = [tuple((M @ np.array([[x],[y],[1]])).flatten()[:2].astype(int)) for x,y in puntos]
        self.dibujar_figura(nuevos_puntos)

# --- Main ---
if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionDibujo(raiz)
    raiz.mainloop()
