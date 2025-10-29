import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import os

class AplicacionDibujo:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Transformaciones Geometricas")
        self.raiz.geometry("1150x700")

        self.modo_oscuro = False

        self.style = ttk.Style()

        self.marco_principal = tk.Frame(raiz)
        self.marco_principal.pack(fill=tk.BOTH, expand=True)

        self.barra_superior = tk.Frame(self.marco_principal, padx=5, pady=5)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X)

        self.barra_estado = tk.Frame(self.marco_principal, padx=5, pady=2, bd=1, relief=tk.SUNKEN)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)

        self.configurar_estilo_claro()

        self.cargar_iconos()

        self.etiqueta_estado = ttk.Label(self.barra_estado, text="Seleccione una figura para comenzar.")
        self.etiqueta_estado.pack(side=tk.LEFT, padx=5)

        self.etiqueta_coord = ttk.Label(self.barra_estado, text="Posición: ( , )")
        self.etiqueta_coord.pack(side=tk.RIGHT, padx=5)

        self.lienzo = tk.Canvas(self.marco_principal, bg="white", highlightthickness=0)
        self.lienzo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.crear_widgets_barra_superior()

        self.lienzo.bind("<Motion>", self.actualizar_pos_mouse)
        self.lienzo.bind("<Button-1>", self.al_clic)

        self.puntos = []
        self.formas_temporales = []
        self.formas_dibujadas = []
        self.formas_deshechas = []

        self.actualizar_estado()

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
            "dark_mode": "dark-mode.png"
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
                    self.icons[name] = None

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
            self.undo_icon = self.redo_icon = self.shape_icon = self.color_icon = None
            self.move_icon = self.scale_icon = self.rotate_icon = self.dark_mode_icon = None

    def crear_widgets_barra_superior(self):
        marco_figura = ttk.LabelFrame(self.barra_superior, text="Tipo de Figura")
        marco_figura.pack(side=tk.LEFT, padx=5, pady=2)
        if self.shape_icon:
            ttk.Label(marco_figura, image=self.shape_icon).pack(side=tk.LEFT, padx=(5,0), pady=5)
        self.tipo_figura = tk.StringVar(value="línea")
        figure_menu = ttk.Combobox(marco_figura, textvariable=self.tipo_figura,
                                   values=["línea", "circulo", "arco"], state="readonly", width=8)
        figure_menu.pack(side=tk.LEFT, padx=5, pady=5)
        figure_menu.bind("<<ComboboxSelected>>", self.on_figure_select)

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

        self.crear_controles_transformacion()

        marco_historial = ttk.LabelFrame(self.barra_superior, text="Historial")
        marco_historial.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(marco_historial, image=self.undo_icon, command=self.deshacer, text="" if self.undo_icon else "Deshacer").pack(side=tk.LEFT, padx=2, pady=5)
        ttk.Button(marco_historial, image=self.redo_icon, command=self.rehacer, text="" if self.redo_icon else "Rehacer").pack(side=tk.LEFT, padx=2, pady=5)

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
        
        self.style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")
        self.style.map('TCombobox', fieldbackground=[('readonly', 'white')])
        self.style.configure("TEntry", fieldbackground="white", background="white", foreground="black", insertcolor="black")

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
        entry_bg = "#505050"

        self.style.configure(".", background=dark_bg, foreground=dark_fg)
        self.style.configure("TFrame", background=dark_bg)
        self.style.configure("TLabel", background=dark_bg, foreground=dark_fg)
        self.style.configure("TButton", background=active_bg, foreground=dark_fg, borderwidth=1)
        self.style.map("TButton", background=[('active', '#666666')])
        self.style.configure("TLabelframe", background=dark_bg, bordercolor=border_color)
        self.style.configure("TLabelframe.Label", background=dark_bg, foreground=dark_fg)
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=entry_bg, foreground=dark_fg)
        self.style.map('TCombobox', fieldbackground=[('readonly', entry_bg)])
        self.style.configure("TEntry", fieldbackground=entry_bg, background=entry_bg, foreground=dark_fg, insertcolor=dark_fg)


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
        formas_actuales = self.formas_dibujadas[:]
        for figura in formas_actuales:
             if 'ids' in figura and figura['ids']:
                 for item_id in figura['ids']:
                     if self.lienzo.winfo_exists() and item_id in self.lienzo.find_all():
                         self.lienzo.delete(item_id)
             else:
                 print(f"Skipping deletion for figure with missing/empty ids: {figura}")


        self.formas_dibujadas = []
        self.formas_deshechas = []

        for figura in formas_actuales:
            self.redibujar_figura(figura)

    def crear_controles_transformacion(self):
        marco_traslacion = ttk.LabelFrame(self.barra_superior, text="Trasladar")
        marco_traslacion.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(marco_traslacion, text="X:").pack(side=tk.LEFT, pady=5)
        self.entrada_dx = ttk.Entry(marco_traslacion, width=4)
        self.entrada_dx.insert(0, "10")
        self.entrada_dx.pack(side=tk.LEFT, pady=5)
        ttk.Label(marco_traslacion, text="Y:").pack(side=tk.LEFT, pady=5)
        self.entrada

