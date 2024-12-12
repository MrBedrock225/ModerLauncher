import tkinter as tk
from itertools import cycle
import os
import sys
import importlib.util

class ModerLauncherAnimation:
    def __init__(self, root):
        self.root = root
        self.root.title("ModerLauncher")
        self.root.configure(bg="#1a202c")

        # Centrar la ventana
        self.window_width = 400
        self.window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (self.window_width // 2)
        y_position = (screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_position}+{y_position}")

        # Canvas para el spinner
        self.canvas = tk.Canvas(root, width=200, height=200, bg="#1a202c", highlightthickness=0)
        self.canvas.pack(pady=30)

        # Spinner inicial
        self.spinner = self.canvas.create_arc(20, 20, 180, 180, start=0, extent=90, outline="#ffffff", width=4, style="arc")

        # Título estético
        self.label = tk.Label(root, text="ModerLauncher", font=("Helvetica", 24, "bold"), bg="#1a202c", fg="white")
        self.label.pack()

        # Texto dinámico de "Cargando..."
        self.loading_text = tk.Label(root, text="Cargando...", font=("Helvetica", 16, "italic"), bg="#1a202c", fg="white")
        self.loading_text.pack()

        # Variables de animación
        self.angle = 0
        self.rgb_colors = cycle(["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"])
        self.current_color = next(self.rgb_colors)
        self.loading_dots = cycle(["", ".", "..", "..."])

        # Iniciar animación
        self.animate_spinner()
        self.update_loading_text()

        # Transición al launcher principal después de 6 segundos
        self.root.after(6000, self.transition_to_main_launcher)

    def animate_spinner(self):
        """Rotar el círculo y cambiar su color para simular carga."""
        self.angle = (self.angle + 10) % 360
        self.current_color = next(self.rgb_colors)
        self.canvas.itemconfig(self.spinner, start=self.angle, outline=self.current_color)
        self.root.after(50, self.animate_spinner)

    def update_loading_text(self):
        """Actualizar el texto de cargando con puntos animados."""
        self.loading_text.config(text=f"Cargando{next(self.loading_dots)}")
        self.root.after(500, self.update_loading_text)

    def transition_to_main_launcher(self):
        """Cargar y mostrar el launcher principal."""
        try:
            # Obtener la ruta del ModerLauncher.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            launcher_path = os.path.join(current_dir, "ModerLauncher.py")

            # Verificar si el archivo existe
            if not os.path.exists(launcher_path):
                raise FileNotFoundError(f"No se encontró ModerLauncher.py en {launcher_path}")

            # Cargar el módulo ModerLauncher dinámicamente
            spec = importlib.util.spec_from_file_location("ModerLauncher", launcher_path)
            launcher_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(launcher_module)

            # Destruir la ventana de carga
            self.root.destroy()

            # Crear una nueva instancia del launcher principal
            launcher_app = launcher_module.MinecraftLauncher()
            launcher_app.mainloop()

        except Exception as e:
            # Si hay un error, mostrar una ventana de error
            error_window = tk.Tk()
            error_window.title("Error")
            error_window.geometry("400x200")
            tk.Label(error_window, text=f"Error al cargar el launcher:\n{str(e)}").pack(pady=20)
            tk.Button(error_window, text="Cerrar", command=error_window.destroy).pack()
            error_window.mainloop()

# Iniciar la animación de carga
if __name__ == "__main__":
    root = tk.Tk()
    app = ModerLauncherAnimation(root)
    root.mainloop()