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

        # Initialize data structures
        self.puntos = []
        self.formas_temporales = []
        self.formas_dibujadas = []

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionDibujo(raiz)
    raiz.mainloop()
