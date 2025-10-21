import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import os 

class AplicacionDibujo:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Dibujo de Figuras Geométricas")
        self.raiz.geometry("1200x700") 

        self.marco_principal = tk.Frame(raiz)
        self.marco_principal.pack(fill=tk.BOTH, expand=True)

       
        script_dir = os.path.dirname(os.path.abspath(__file__))
        media_dir = os.path.join(script_dir, "media")

       
        self.undo_icon = tk.PhotoImage(file=os.path.join(media_dir, "previous.png"))
        self.redo_icon = tk.PhotoImage(file=os.path.join(media_dir, "next.png"))
        self.shape_icon = tk.PhotoImage(file=os.path.join(media_dir, "period.png"))
        self.color_icon = tk.PhotoImage(file=os.path.join(media_dir, "color-wheel.png"))
        self.move_icon = tk.PhotoImage(file=os.path.join(media_dir, "translate.png"))
        self.scale_icon = tk.PhotoImage(file=os.path.join(media_dir, "scale.png"))
        self.rotate_icon = tk.PhotoImage(file=os.path.join(media_dir, "view.png"))
        self.symmetry_icon = tk.PhotoImage(file=os.path.join(media_dir, "reflect.png"))
        
        
        self.barra_superior = tk.Frame(self.marco_principal, padx=5, pady=5)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X)

        
        self.lienzo = tk.Canvas(self.marco_principal, bg="white")
        self.lienzo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        marco_figura = ttk.LabelFrame(self.barra_superior, text="Tipo de Figura")
        marco_figura.pack(side=tk.LEFT, padx=5, pady=2)
        
        ttk.Label(marco_figura, image=self.shape_icon).pack(side=tk.LEFT, padx=(5,0), pady=5)
        self.tipo_figura = tk.StringVar(value="línea")
        figure_menu = ttk.Combobox(marco_figura, textvariable=self.tipo_figura,
                                   values=["línea", "circulo", "arco"], state="readonly", width=8)
        figure_menu.pack(side=tk.LEFT, padx=5, pady=5)
        figure_menu.bind("<<ComboboxSelected>>", self.on_figure_select)


        marco_color = ttk.LabelFrame(self.barra_superior, text="Color")
        marco_color.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_color, image=self.color_icon).pack(side=tk.LEFT, padx=(5,0), pady=5)
        self.color = tk.StringVar(value="Azul")
        menu_color = ttk.Combobox(marco_color, textvariable=self.color,
                                  values=["Negro", "Azul", "Rojo"], state="readonly", width=7)
        menu_color.current(1)
        menu_color.pack(side=tk.LEFT, padx=5, pady=5)

        self.crear_controles_transformacion()

        
        marco_historial = ttk.LabelFrame(self.barra_superior, text="Historial")
        marco_historial.pack(side=tk.LEFT, padx=5, pady=2)
        
        ttk.Button(marco_historial, image=self.undo_icon, command=self.deshacer).pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(marco_historial, image=self.redo_icon, command=self.rehacer).pack(side=tk.LEFT, padx=2, pady=5)
        
        self.etiqueta_coord = ttk.Label(self.barra_superior, text="Posición: ( , )")
        self.etiqueta_coord.pack(side=tk.RIGHT, padx=10)

       
        self.lienzo.bind("<Motion>", self.actualizar_pos_mouse)
        self.lienzo.bind("<Button-1>", self.al_clic)

        
        self.puntos = []
        self.formas_temporales = []
        self.formas_dibujadas = []
        self.formas_deshechas = [] 

    def crear_controles_transformacion(self):
        """Helper function to create transformation controls in the top bar."""
        # Translation
        marco_traslacion = ttk.LabelFrame(self.barra_superior, text="Trasladar")
        marco_traslacion.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_traslacion, text="X:").pack(side=tk.LEFT, pady=5)
        self.entrada_dx = ttk.Entry(marco_traslacion, width=4)
        self.entrada_dx.insert(0, "10")
        self.entrada_dx.pack(side=tk.LEFT, pady=5)
        ttk.Label(marco_traslacion, text="Y:").pack(side=tk.LEFT, pady=5)
        self.entrada_dy = ttk.Entry(marco_traslacion, width=4)
        self.entrada_dy.insert(0, "10")
        self.entrada_dy.pack(side=tk.LEFT, pady=5)
        ttk.Button(marco_traslacion, text="Mover", image=self.move_icon, compound=tk.LEFT, command=self.trasladar_figura).pack(side=tk.LEFT, padx=5, pady=5)

        # Scaling
        marco_escala = ttk.LabelFrame(self.barra_superior, text="Escalar")
        marco_escala.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_escala, text="Factor:").pack(side=tk.LEFT, pady=5)
        self.entrada_escala = ttk.Entry(marco_escala, width=5)
        self.entrada_escala.insert(0, "1.2")
        self.entrada_escala.pack(side=tk.LEFT, pady=5)
        ttk.Button(marco_escala, text="Escalar", image=self.scale_icon, compound=tk.LEFT, command=self.escalar_figura).pack(side=tk.LEFT, padx=5, pady=5)

        # Rotation
        marco_rotacion = ttk.LabelFrame(self.barra_superior, text="Rotar")
        marco_rotacion.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_rotacion, text="Ángulo(°):").pack(side=tk.LEFT, pady=5)
        self.entrada_angulo = ttk.Entry(marco_rotacion, width=4)
        self.entrada_angulo.insert(0, "15")
        self.entrada_angulo.pack(side=tk.LEFT, pady=5)
        ttk.Button(marco_rotacion, text="Rotar", image=self.rotate_icon, compound=tk.LEFT, command=self.rotar_figura).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Symmetry
        marco_simetria = ttk.LabelFrame(self.barra_superior, text="Simetría")
        marco_simetria.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.eje_simetria = tk.StringVar(value="Eje X")
        eje_menu = ttk.Combobox(marco_simetria, textvariable=self.eje_simetria,
                                  values=["Eje X", "Eje Y"], state="readonly", width=7)
        eje_menu.pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(marco_simetria, text="Aplicar", image=self.symmetry_icon, compound=tk.LEFT, command=self.aplicar_simetria).pack(side=tk.LEFT, padx=5, pady=5)

    def on_figure_select(self, event=None):
        """Resets points when the figure type changes."""
        self.puntos = []
        self.borrar_formas_temporales()

    def actualizar_pos_mouse(self, evento):
        self.etiqueta_coord.config(text=f"Posición: ({evento.x}, {evento.y})")
        self.previsualizar_figura((evento.x, evento.y))

    def al_clic(self, evento):
        self.puntos.append((evento.x, evento.y))
        tipo = self.tipo_figura.get()
        puntos_necesarios = {"línea": 2, "circulo": 2, "arco": 3}[tipo]

        if len(self.puntos) == puntos_necesarios:
            self.dibujar_figura(self.puntos)
            self.puntos = []
            self.borrar_formas_temporales()

    def borrar_formas_temporales(self):
        for forma in self.formas_temporales:
            self.lienzo.delete(forma)
        self.formas_temporales = []
    
    def calcular_arco_desde_puntos(self, p1, p2, p3):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D) < 1e-6: return None 

        ux = ((x1*x1 + y1*y1) * (y2 - y3) + (x2*x2 + y2*y2) * (y3 - y1) + (x3*x3 + y3*y3) * (y1 - y2)) / D
        uy = ((x1*x1 + y1*y1) * (x3 - x2) + (x2*x2 + y2*y2) * (x1 - x3) + (x3*x3 + y3*y3) * (x2 - x1)) / D

        radius = math.sqrt((x1 - ux)**2 + (y1 - uy)**2)
        bbox = (ux - radius, uy - radius, ux + radius, uy + radius)
        
        start_angle = math.degrees(math.atan2(-(y1 - uy), x1 - ux))
        end_angle = math.degrees(math.atan2(-(y2 - uy), x2 - ux))
        mid_angle = math.degrees(math.atan2(-(y3 - uy), x3 - ux))
        
        s_norm = (start_angle + 360) % 360
        e_norm = (end_angle + 360) % 360
        m_norm = (mid_angle + 360) % 360
        
        extent_ccw = (e_norm - s_norm + 360) % 360
        
        is_in_ccw = False
        if s_norm < e_norm:
            if s_norm < m_norm < e_norm: is_in_ccw = True
        else:
            if m_norm > s_norm or m_norm < e_norm: is_in_ccw = True
        
        if is_in_ccw:
            return bbox, start_angle, extent_ccw
        else:
            extent_cw = (s_norm - e_norm + 360) % 360
            return bbox, start_angle, -extent_cw

    def previsualizar_figura(self, punto_actual):
        self.borrar_formas_temporales()
        if not self.puntos: return
        tipo = self.tipo_figura.get(); color_previsualizacion = "light gray"
        puntos = self.puntos + [punto_actual]
        
        for p in self.puntos:
            x, y = p
            self.formas_temporales.append(self.lienzo.create_oval(x-2, y-2, x+2, y+2, fill="gray"))

        if tipo == "línea" and len(puntos) == 2:
            self.formas_temporales.append(self.lienzo.create_line(*puntos[0], *puntos[1], fill=color_previsualizacion, dash=(3, 2)))
        elif tipo == "circulo" and len(puntos) == 2:
            x0, y0 = puntos[0]; x1, y1 = puntos[1]
            r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            self.formas_temporales.append(self.lienzo.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline=color_previsualizacion, dash=(3, 2)))
        elif tipo == "arco":
            if len(puntos) == 2: self.formas_temporales.append(self.lienzo.create_line(*puntos[0], *puntos[1], fill=color_previsualizacion, dash=(3,2)))
            elif len(puntos) == 3:
                arc_params = self.calcular_arco_desde_puntos(*puntos)
                if arc_params:
                    bbox, start, extent = arc_params
                    self.formas_temporales.append(self.lienzo.create_arc(bbox, start=start, extent=extent, style=tk.ARC, outline=color_previsualizacion, dash=(3,2), width=2))

    def dibujar_figura(self, puntos):
        tipo = self.tipo_figura.get()
        mapa_colores = {"Negro": "black", "Azul": "blue", "Rojo": "red"}
        color = mapa_colores.get(self.color.get(), "black")
        ids = []

        if tipo == "línea": ids.append(self.lienzo.create_line(puntos, fill=color, width=2))
        elif tipo == "circulo":
            x0, y0 = puntos[0]; x1, y1 = puntos[1]
            r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            ids.append(self.lienzo.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline=color, width=2))
        elif tipo == "arco":
            arc_params = self.calcular_arco_desde_puntos(*puntos)
            if arc_params:
                bbox, start, extent = arc_params
                ids.append(self.lienzo.create_arc(bbox, start=start, extent=extent, style=tk.ARC, outline=color, width=2))
        
        if ids:
            self.formas_dibujadas.append({'ids': ids, 'puntos': puntos, 'tipo': tipo, 'color': color})
            self.formas_deshechas.clear() # Clear redo stack on new action

    def redibujar_figura(self, figura_dict):
        puntos = figura_dict['puntos']; tipo = figura_dict['tipo']; color = figura_dict['color']
        ids = []
        if tipo == "línea": ids.append(self.lienzo.create_line(puntos, fill=color, width=2))
        elif tipo == "circulo":
            x0, y0 = puntos[0]; x1, y1 = puntos[1]
            r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            ids.append(self.lienzo.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline=color, width=2))
        elif tipo == "arco":
            arc_params = self.calcular_arco_desde_puntos(*puntos)
            if arc_params:
                bbox, start, extent = arc_params
                ids.append(self.lienzo.create_arc(bbox, start=start, extent=extent, style=tk.ARC, outline=color, width=2))
        
        if ids:
            figura_dict['ids'] = ids
            self.formas_dibujadas.append(figura_dict)

    def deshacer(self):
        if self.formas_dibujadas:
            figura = self.formas_dibujadas.pop()
            for item_id in figura['ids']:
                self.lienzo.delete(item_id)
            self.formas_deshechas.append(figura)

    def rehacer(self):
        if self.formas_deshechas:
            figura = self.formas_deshechas.pop()
            self.redibujar_figura(figura)
            
    def aplicar_transformacion(self, matriz):
        if not self.formas_dibujadas: return
        
        figura_a_transformar = self.formas_dibujadas.pop()
        for item_id in figura_a_transformar['ids']: self.lienzo.delete(item_id)
        puntos = figura_a_transformar['puntos']
        
        puntos_a_transformar = puntos
        xs, ys = zip(*puntos_a_transformar)
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        
        T1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
        T2 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]])
        M = T2 @ matriz @ T1

        nuevos_puntos = [tuple((M @ np.array([x, y, 1]))[:2].astype(int)) for x, y in puntos]
        figura_a_transformar['puntos'] = nuevos_puntos
        self.redibujar_figura(figura_a_transformar)
        self.formas_deshechas.clear()

    def trasladar_figura(self):
        if not self.formas_dibujadas: return
        try:
            dx = int(self.entrada_dx.get()); dy = int(self.entrada_dy.get())
        except ValueError: return

        T = np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]])
        
        figura_a_transformar = self.formas_dibujadas.pop()
        for item_id in figura_a_transformar['ids']: self.lienzo.delete(item_id)
        puntos = figura_a_transformar['puntos']
        nuevos_puntos = [tuple((T @ np.array([x, y, 1]))[:2].astype(int)) for x, y in puntos]
        figura_a_transformar['puntos'] = nuevos_puntos
        self.redibujar_figura(figura_a_transformar)
        self.formas_deshechas.clear()

    def escalar_figura(self):
        try: factor = float(self.entrada_escala.get())
        except ValueError: return
        S = np.array([[factor, 0, 0], [0, factor, 0], [0, 0, 1]])
        self.aplicar_transformacion(S)

    def aplicar_simetria(self):
        eje = self.eje_simetria.get()
        if eje == "Eje X":
            matriz = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        elif eje == "Eje Y":
            matriz = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        else:
            return 
        
        self.aplicar_transformacion(matriz)

    def rotar_figura(self):
        try: angulo = float(self.entrada_angulo.get())
        except ValueError: return
        rad = math.radians(angulo)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        R = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
        self.aplicar_transformacion(R)

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionDibujo(raiz)
    raiz.mainloop()