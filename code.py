import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import os

class AplicacionDibujo:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Transformaciones Geometricas")
        self.raiz.geometry("1150x700") # Slightly wider for dark mode button

        self.modo_oscuro = False # State variable for dark mode

        # --- Style Configuration Object ---
        self.style = ttk.Style()

        # --- Create main frames FIRST ---
        self.marco_principal = tk.Frame(raiz)
        self.marco_principal.pack(fill=tk.BOTH, expand=True)

        self.barra_superior = tk.Frame(self.marco_principal, padx=5, pady=5)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X)

        self.barra_estado = tk.Frame(self.marco_principal, padx=5, pady=2, bd=1, relief=tk.SUNKEN)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Apply initial style AFTER frames are created ---
        self.configurar_estilo_claro() # Start with light mode style

        # --- Load Icons (using the specified names) ---
        self.cargar_iconos()

        # --- Status Bar Labels (created after style is set) ---
        self.etiqueta_estado = ttk.Label(self.barra_estado, text="Seleccione una figura para comenzar.")
        self.etiqueta_estado.pack(side=tk.LEFT, padx=5)

        self.etiqueta_coord = ttk.Label(self.barra_estado, text="Posición: ( , )")
        self.etiqueta_coord.pack(side=tk.RIGHT, padx=5)

        # --- Canvas (in the middle) ---
        self.lienzo = tk.Canvas(self.marco_principal, bg="white", highlightthickness=0)
        self.lienzo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- Toolbar Widgets ---
        self.crear_widgets_barra_superior()

        # --- Bindings and Initial State ---
        self.lienzo.bind("<Motion>", self.actualizar_pos_mouse)
        self.lienzo.bind("<Button-1>", self.al_clic)

        self.puntos = []
        self.formas_temporales = []
        self.formas_dibujadas = []
        self.formas_deshechas = []

        self.actualizar_estado() # Initial status message

    def cargar_iconos(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        media_dir = os.path.join(script_dir, "media")
        icon_files = {
            "undo": "previous.png",
            "redo": "next.png",
            "shape": "period.png",
            "color": "color-wheel.png",
            "move": "translate.png",
            "scale": "scale.png",
            "rotate": "view.png",
            "dark_mode": "dark-mode.png" # Make sure you have this icon
        }
        self.icons = {}
        missing_icons = []
        try:
            for name, filename in icon_files.items():
                path = os.path.join(media_dir, filename)
                if os.path.exists(path):
                     self.icons[name] = tk.PhotoImage(file=path)
                else:
                    missing_icons.append(filename)
                    self.icons[name] = None # Placeholder if missing

            # Assign to specific attributes for easier access later
            self.undo_icon = self.icons.get("undo")
            self.redo_icon = self.icons.get("redo")
            self.shape_icon = self.icons.get("shape")
            self.color_icon = self.icons.get("color")
            self.move_icon = self.icons.get("move")
            self.scale_icon = self.icons.get("scale")
            self.rotate_icon = self.icons.get("rotate")
            self.dark_mode_icon = self.icons.get("dark_mode")

            if missing_icons:
                print(f"Warning: Could not find the following icons in '{media_dir}': {', '.join(missing_icons)}")
                print("Buttons for missing icons might not display correctly.")

        except tk.TclError as e:
            print(f"Error loading icons: {e}")
            print("Please ensure image files are valid PNGs and the 'media' folder exists.")
            # Set all icons to None if there's a general loading error
            self.undo_icon = self.redo_icon = self.shape_icon = self.color_icon = None
            self.move_icon = self.scale_icon = self.rotate_icon = self.dark_mode_icon = None

    def crear_widgets_barra_superior(self):
        # --- Figure Type ---
        marco_figura = ttk.LabelFrame(self.barra_superior, text="Tipo de Figura")
        marco_figura.pack(side=tk.LEFT, padx=5, pady=2)
        # Only show icon if loaded
        if self.shape_icon:
            ttk.Label(marco_figura, image=self.shape_icon).pack(side=tk.LEFT, padx=(5,0), pady=5)
        self.tipo_figura = tk.StringVar(value="línea")
        figure_menu = ttk.Combobox(marco_figura, textvariable=self.tipo_figura,
                                   values=["línea", "circulo", "arco"], state="readonly", width=8)
        figure_menu.pack(side=tk.LEFT, padx=5, pady=5)
        figure_menu.bind("<<ComboboxSelected>>", self.on_figure_select)

        # --- Color ---
        marco_color = ttk.LabelFrame(self.barra_superior, text="Color")
        marco_color.pack(side=tk.LEFT, padx=5, pady=2)
        if self.color_icon:
            ttk.Label(marco_color, image=self.color_icon).pack(side=tk.LEFT, padx=(5,0), pady=5)
        self.color = tk.StringVar(value="Azul")
        self.colores_disponibles = ["Negro", "Azul", "Rojo", "Verde", "Amarillo", "Naranja", "Morado"]
        menu_color = ttk.Combobox(marco_color, textvariable=self.color,
                                  values=self.colores_disponibles, state="readonly", width=8)
        menu_color.current(1)
        menu_color.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Transformations ---
        self.crear_controles_transformacion()

        # --- History ---
        marco_historial = ttk.LabelFrame(self.barra_superior, text="Historial")
        marco_historial.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(marco_historial, image=self.undo_icon, command=self.deshacer, text="" if self.undo_icon else "Deshacer").pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(marco_historial, image=self.redo_icon, command=self.rehacer, text="" if self.redo_icon else "Rehacer").pack(side=tk.LEFT, padx=2, pady=5)

        # --- Dark Mode Toggle (at the far right) ---
        # Removed text and fallback text logic
        ttk.Button(self.barra_superior, image=self.dark_mode_icon, command=self.toggle_modo_oscuro).pack(side=tk.RIGHT, padx=5, pady=5)


    def configurar_estilo_claro(self):
        self.style.theme_use('clam')
        self.raiz.configure(bg="SystemButtonFace")

        self.style.configure(".", background="SystemButtonFace", foreground="black")
        self.style.configure("TFrame", background="SystemButtonFace")
        self.style.configure("TLabel", background="SystemButtonFace", foreground="black")
        self.style.configure("TButton", background="#e1e1e1", foreground="black", borderwidth=1)
        self.style.map("TButton", background=[('active', '#d1d1d1')])
        self.style.configure("TLabelframe", background="SystemButtonFace", bordercolor="#c1c1c1")
        self.style.configure("TLabelframe.Label", background="SystemButtonFace", foreground="black")
        
        # --- FIX: Explicitly reset Combobox and Entry styles for light mode ---
        self.style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")
        self.style.map('TCombobox', fieldbackground=[('readonly', 'white')]) # Reset readonly state
        self.style.configure("TEntry", fieldbackground="white", background="white", foreground="black", insertcolor="black") # Reset Entry and cursor color
        # --- End Fix ---

        # Configure non-ttk Frame backgrounds only if they exist
        if hasattr(self, 'barra_superior'):
            self.barra_superior.configure(bg="SystemButtonFace")
        if hasattr(self, 'barra_estado'):
             self.barra_estado.configure(bg="SystemButtonFace", relief=tk.SUNKEN)
             if hasattr(self, 'etiqueta_estado'):
                  self.etiqueta_estado.configure(background="SystemButtonFace", foreground="black")
             if hasattr(self, 'etiqueta_coord'):
                  self.etiqueta_coord.configure(background="SystemButtonFace", foreground="black")


    def configurar_estilo_oscuro(self):
        self.raiz.configure(bg="#2e2e2e")

        dark_bg = "#3c3c3c"
        dark_fg = "white"
        active_bg = "#555555"
        border_color = "#555555"
        entry_bg = "#505050" # Slightly different background for entry fields

        self.style.configure(".", background=dark_bg, foreground=dark_fg)
        self.style.configure("TFrame", background=dark_bg)
        self.style.configure("TLabel", background=dark_bg, foreground=dark_fg)
        self.style.configure("TButton", background=active_bg, foreground=dark_fg, borderwidth=1)
        self.style.map("TButton", background=[('active', '#666666')])
        self.style.configure("TLabelframe", background=dark_bg, bordercolor=border_color)
        self.style.configure("TLabelframe.Label", background=dark_bg, foreground=dark_fg)
        # Style Combobox for dark mode
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=entry_bg, foreground=dark_fg)
        self.style.map('TCombobox', fieldbackground=[('readonly', entry_bg)])
        # Style Entry for dark mode
        self.style.configure("TEntry", fieldbackground=entry_bg, background=entry_bg, foreground=dark_fg, insertcolor=dark_fg) # Added insertcolor


        # Configure non-ttk Frame backgrounds only if they exist
        if hasattr(self, 'barra_superior'):
            self.barra_superior.configure(bg=dark_bg)
        if hasattr(self, 'barra_estado'):
             self.barra_estado.configure(bg=dark_bg, relief=tk.FLAT, bd=0)
             if hasattr(self, 'etiqueta_estado'):
                  self.etiqueta_estado.configure(background=dark_bg, foreground=dark_fg)
             if hasattr(self, 'etiqueta_coord'):
                  self.etiqueta_coord.configure(background=dark_bg, foreground=dark_fg)


    def toggle_modo_oscuro(self):
        self.modo_oscuro = not self.modo_oscuro
        if self.modo_oscuro:
            self.configurar_estilo_oscuro()
            self.lienzo.config(bg="black")
        else:
            self.configurar_estilo_claro()
            self.lienzo.config(bg="white")

        self.redibujar_todo()

    def redibujar_todo(self):
        """Redraws all shapes on the canvas, usually after a theme change."""
        formas_actuales = self.formas_dibujadas[:]
        # Clear canvas BUT keep the shapes data
        for figura in formas_actuales:
             # Check if 'ids' exists and is not empty
             if 'ids' in figura and figura['ids']:
                 for item_id in figura['ids']:
                     # Check if item exists before deleting
                     if self.lienzo.winfo_exists() and item_id in self.lienzo.find_all():
                         self.lienzo.delete(item_id)
             else:
                 print(f"Skipping deletion for figure with missing/empty ids: {figura}")


        self.formas_dibujadas = [] # Clear the main list TEMPORARILY
        self.formas_deshechas = [] # Reset redo stack on theme change

        # Redraw each shape, which will add it back to formas_dibujadas
        for figura in formas_actuales:
            # Pass the original dictionary to maintain all info
            self.redibujar_figura(figura)

    def crear_controles_transformacion(self):
        """Helper function to create transformation controls in the top bar."""
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
        ttk.Button(marco_traslacion, text="Mover", image=self.move_icon, compound=tk.LEFT if self.move_icon else tk.NONE, command=self.trasladar_figura).pack(side=tk.LEFT, padx=5, pady=5)

        marco_escala = ttk.LabelFrame(self.barra_superior, text="Escalar")
        marco_escala.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_escala, text="Factor:").pack(side=tk.LEFT, pady=5)
        self.entrada_escala = ttk.Entry(marco_escala, width=5)
        self.entrada_escala.insert(0, "1.2")
        self.entrada_escala.pack(side=tk.LEFT, pady=5)
        ttk.Button(marco_escala, text="Escalar", image=self.scale_icon, compound=tk.LEFT if self.scale_icon else tk.NONE, command=self.escalar_figura).pack(side=tk.LEFT, padx=5, pady=5)

        marco_rotacion = ttk.LabelFrame(self.barra_superior, text="Rotar")
        marco_rotacion.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_rotacion, text="Ángulo(°):").pack(side=tk.LEFT, pady=5)
        self.entrada_angulo = ttk.Entry(marco_rotacion, width=4)
        self.entrada_angulo.insert(0, "15")
        self.entrada_angulo.pack(side=tk.LEFT, pady=5)
        ttk.Button(marco_rotacion, text="Rotar", image=self.rotate_icon, compound=tk.LEFT if self.rotate_icon else tk.NONE, command=self.rotar_figura).pack(side=tk.LEFT, padx=5, pady=5)

    def on_figure_select(self, event=None):
        self.puntos = []
        self.borrar_formas_temporales()
        self.actualizar_estado()

    def actualizar_estado(self):
        figura = self.tipo_figura.get()
        puntos_hechos = len(self.puntos)
        mensaje = ""
        if figura == 'línea':
            if puntos_hechos == 0: mensaje = "Haz clic para el punto de inicio de la línea."
            elif puntos_hechos == 1: mensaje = "Haz clic para el punto final de la línea."
        elif figura == 'circulo':
            if puntos_hechos == 0: mensaje = "Haz clic para definir el centro del círculo."
            elif puntos_hechos == 1: mensaje = "Haz clic para definir el radio del círculo."
        elif figura == 'arco':
            if puntos_hechos == 0: mensaje = "Haz clic para el punto de inicio del arco."
            elif puntos_hechos == 1: mensaje = "Haz clic para el punto final del arco."
            elif puntos_hechos == 2: mensaje = "Haz clic en un punto para definir la curvatura del arco."

        if hasattr(self, 'etiqueta_estado'):
             self.etiqueta_estado.config(text=mensaje)

    def actualizar_pos_mouse(self, evento):
        if hasattr(self, 'etiqueta_coord'):
             self.etiqueta_coord.config(text=f"Posición: ({evento.x}, {evento.y})")
        self.previsualizar_figura((evento.x, evento.y))

    def al_clic(self, evento):
        self.puntos.append((evento.x, evento.y))
        tipo = self.tipo_figura.get()
        puntos_necesarios = {"línea": 2, "circulo": 2, "arco": 3}.get(tipo) # Use .get for safety
        if puntos_necesarios is None: return # Should not happen with combobox

        if len(self.puntos) == puntos_necesarios:
            self.dibujar_figura(self.puntos)
            self.puntos = []
            self.borrar_formas_temporales()
        self.actualizar_estado()

    def borrar_formas_temporales(self):
        for forma in self.formas_temporales:
             # Check if item exists before deleting
             if self.lienzo.winfo_exists() and forma in self.lienzo.find_all():
                self.lienzo.delete(forma)
        self.formas_temporales = []

    def calcular_arco_desde_puntos(self, p1, p2, p3):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3
        area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if area < 1e-6:
             print("Points are collinear, cannot draw arc.")
             return None
        # Simplified center calculation using determinant approach
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(D) < 1e-10: return None # Robust check

        ux = ((x1**2 + y1**2)*(y2 - y3) + (x2**2 + y2**2)*(y3 - y1) + (x3**2 + y3**2)*(y1 - y2)) / D
        uy = ((x1**2 + y1**2)*(x3 - x2) + (x2**2 + y2**2)*(x1 - x3) + (x3**2 + y3**2)*(x2 - x1)) / D

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
        if abs(extent_ccw) < 1e-6 or abs(extent_ccw - 360) < 1e-6: # Handle full circle case if start ~= end
             angle_diff_sm = abs(m_norm - s_norm + 180) % 360 - 180
             angle_diff_me = abs(e_norm - m_norm + 180) % 360 - 180
             if abs(angle_diff_sm + angle_diff_me) < 1 : # If mid is roughly opposite start/end
                 extent_ccw = 359.99
                 is_in_ccw = True
             else:
                 is_in_ccw = True
                 extent_ccw = 0.01

        elif s_norm < e_norm:
            if s_norm < m_norm < e_norm: is_in_ccw = True
        else: # Arc crosses 0/360 degrees
            if m_norm > s_norm or m_norm < e_norm: is_in_ccw = True

        if is_in_ccw:
            return bbox, start_angle, extent_ccw if extent_ccw != 0 else 0.01
        else:
             extent_cw = (s_norm - e_norm + 360) % 360
             if extent_cw == 0 : extent_cw = 359.99
             return bbox, start_angle, -extent_cw if extent_cw !=0 else -0.01


    def previsualizar_figura(self, punto_actual):
        self.borrar_formas_temporales()
        if not self.puntos: return
        tipo = self.tipo_figura.get();
        color_previsualizacion = "gray" if self.modo_oscuro else "light gray"
        puntos = self.puntos + [punto_actual]

        for p in self.puntos:
            x, y = p
            # Check if canvas exists
            if self.lienzo.winfo_exists():
                self.formas_temporales.append(self.lienzo.create_oval(x-2, y-2, x+2, y+2, fill=color_previsualizacion, outline=""))

        # Check if canvas exists before drawing previews
        if not self.lienzo.winfo_exists(): return

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
        color_nombre = self.color.get()

        mapa_colores_normal = {"Negro": "black", "Azul": "blue", "Rojo": "red", "Verde": "green", "Amarillo": "yellow", "Naranja": "orange", "Morado": "purple"}
        mapa_colores_neon = {"Negro": "#cccccc", "Azul": "cyan", "Rojo": "magenta", "Verde": "lime", "Amarillo": "#FFFF00", "Naranja": "#FFA500", "Morado": "#DA70D6"}

        mapa_colores = mapa_colores_neon if self.modo_oscuro else mapa_colores_normal
        color_valor = mapa_colores.get(color_nombre, "black")

        ids = []
        figura_data = {'puntos': puntos, 'tipo': tipo, 'color_nombre': color_nombre}

        # Check if canvas exists
        if not self.lienzo.winfo_exists(): return

        if tipo == "línea": ids.append(self.lienzo.create_line(puntos, fill=color_valor, width=2))
        elif tipo == "circulo":
            x0, y0 = puntos[0]; x1, y1 = puntos[1]
            r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            ids.append(self.lienzo.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline=color_valor, width=2))
        elif tipo == "arco":
            arc_params = self.calcular_arco_desde_puntos(*puntos)
            if arc_params:
                bbox, start, extent = arc_params
                ids.append(self.lienzo.create_arc(bbox, start=start, extent=extent, style=tk.ARC, outline=color_valor, width=2))

        if ids:
            figura_data['ids'] = ids
            self.formas_dibujadas.append(figura_data)
            self.formas_deshechas.clear()

    def redibujar_figura(self, figura_dict):
        puntos = figura_dict.get('puntos'); tipo = figura_dict.get('tipo');
        color_nombre = figura_dict.get('color_nombre', 'Negro')

        # Check basic validity
        if not puntos or not tipo:
             print(f"Skipping redraw due to missing points or type: {figura_dict}")
             return

        mapa_colores_normal = {"Negro": "black", "Azul": "blue", "Rojo": "red", "Verde": "green", "Amarillo": "yellow", "Naranja": "orange", "Morado": "purple"}
        mapa_colores_neon = {"Negro": "#cccccc", "Azul": "cyan", "Rojo": "magenta", "Verde": "lime", "Amarillo": "#FFFF00", "Naranja": "#FFA500", "Morado": "#DA70D6"}

        mapa_colores = mapa_colores_neon if self.modo_oscuro else mapa_colores_normal
        color_valor = mapa_colores.get(color_nombre, "black")

        ids = []
        # Ensure points list is valid before drawing
        valid_points = False
        if tipo == "línea" and len(puntos) == 2: valid_points = True
        elif tipo == "circulo" and len(puntos) == 2: valid_points = True
        elif tipo == "arco" and len(puntos) == 3: valid_points = True

        if not valid_points:
             print(f"Skipping redraw due to incorrect number of points for type '{tipo}': {puntos}")
             return

        # Check if canvas exists
        if not self.lienzo.winfo_exists(): return

        if tipo == "línea": ids.append(self.lienzo.create_line(puntos, fill=color_valor, width=2))
        elif tipo == "circulo":
            x0, y0 = puntos[0]; x1, y1 = puntos[1]
            r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            # Basic check for valid radius
            if r > 0:
                 ids.append(self.lienzo.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, outline=color_valor, width=2))
        elif tipo == "arco":
             arc_params = self.calcular_arco_desde_puntos(*puntos)
             if arc_params:
                 bbox, start, extent = arc_params
                 # Basic check for valid arc parameters
                 if all(isinstance(v, (int, float)) for v in bbox) and \
                    isinstance(start, (int, float)) and isinstance(extent, (int, float)):
                      ids.append(self.lienzo.create_arc(bbox, start=start, extent=extent, style=tk.ARC, outline=color_valor, width=2))

        if ids:
            figura_dict['ids'] = ids
            # Prevent adding duplicates during redibujar_todo
            if figura_dict not in self.formas_dibujadas:
                 self.formas_dibujadas.append(figura_dict)


    def deshacer(self):
        if self.formas_dibujadas:
            figura = self.formas_dibujadas.pop()
            # Check if canvas and item ids exist
            if self.lienzo.winfo_exists() and 'ids' in figura:
                for item_id in figura['ids']:
                     if item_id in self.lienzo.find_all(): # Check if ID exists on canvas
                         self.lienzo.delete(item_id)
            self.formas_deshechas.append(figura)

    def rehacer(self):
        if self.formas_deshechas:
            figura = self.formas_deshechas.pop()
            self.redibujar_figura(figura)

    def aplicar_transformacion(self, matriz):
        if not self.formas_dibujadas: return
        figura_a_transformar = self.formas_dibujadas.pop()

        # Check if canvas and item ids exist before deleting
        if self.lienzo.winfo_exists() and 'ids' in figura_a_transformar:
             for item_id in figura_a_transformar['ids']:
                  if item_id in self.lienzo.find_all():
                     self.lienzo.delete(item_id)

        puntos = figura_a_transformar.get('puntos')
        if not puntos: return # Cannot transform if no points

        puntos_a_transformar = puntos
        try:
             xs, ys = zip(*puntos_a_transformar)
        except ValueError: # Handle case with potentially single point or invalid data
             print(f"Invalid points data for transformation: {puntos_a_transformar}")
             self.formas_dibujadas.append(figura_a_transformar) # Put it back if error
             return

        cx = sum(xs) / len(xs) if xs else 0
        cy = sum(ys) / len(ys) if ys else 0

        T1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
        T2 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]])
        M = T2 @ matriz @ T1

        # Apply transformation and convert to integers
        nuevos_puntos = [tuple(map(int,(M @ np.array([x, y, 1]))[:2])) for x, y in puntos]
        figura_a_transformar['puntos'] = nuevos_puntos

        self.redibujar_figura(figura_a_transformar)
        self.formas_deshechas.clear()

    def trasladar_figura(self):
        if not self.formas_dibujadas: return
        try:
            dx = int(self.entrada_dx.get())
            dy = -int(self.entrada_dy.get())
        except ValueError: return

        figura_a_transformar = self.formas_dibujadas.pop()
        # Check if canvas and item ids exist before deleting
        if self.lienzo.winfo_exists() and 'ids' in figura_a_transformar:
             for item_id in figura_a_transformar['ids']:
                 if item_id in self.lienzo.find_all():
                    self.lienzo.delete(item_id)

        puntos = figura_a_transformar.get('puntos')
        if not puntos: return

        nuevos_puntos = [ (p[0] + dx, p[1] + dy) for p in puntos ]

        figura_a_transformar['puntos'] = nuevos_puntos
        self.redibujar_figura(figura_a_transformar)
        self.formas_deshechas.clear()

    def escalar_figura(self):
        try: factor = float(self.entrada_escala.get())
        except ValueError: return
        if factor == 0: return
        S = np.array([[factor, 0, 0], [0, factor, 0], [0, 0, 1]])
        self.aplicar_transformacion(S)

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

