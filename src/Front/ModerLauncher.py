import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib
import os
import subprocess
from datetime import datetime
import requests
import json
from PIL import Image, ImageTk
from io import BytesIO

class ModsWindow(tk.Toplevel):
    def __init__(self, parent, minecraft_directory):
        super().__init__(parent)
        self.minecraft_directory = minecraft_directory
        
        # Configuración básica de la ventana
        self.title("Gestión de Mods")
        self.geometry("1000x700")
        self.configure(bg='#111111')
        
        # Variables
        self.selected_version = tk.StringVar()
        self.search_query = tk.StringVar()
        self.selected_category = tk.StringVar(value="Todas")
        self.mod_data = {}  # Almacena información detallada de los mods
        
        # Crear la interfaz
        self.create_interface()
        
        # Cargar versiones instaladas
        self.load_installed_versions()

    def create_interface(self):
        # Frame principal
        main_frame = tk.Frame(self, bg='#111111')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior
        top_frame = tk.Frame(main_frame, bg='#111111')
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de versión
        version_label = tk.Label(top_frame, text="Versión:", fg='white', bg='#111111')
        version_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.version_combo = ttk.Combobox(top_frame, textvariable=self.selected_version)
        self.version_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.version_combo.bind('<<ComboboxSelected>>', self.on_version_selected)
        
        # Selector de categoría
        category_label = tk.Label(top_frame, text="Categoría:", fg='white', bg='#111111')
        category_label.pack(side=tk.LEFT, padx=(0, 5))
        
        categories = ["Todas", "Tecnología", "Magia", "Aventura", "Mejoras", "Optimización"]
        self.category_combo = ttk.Combobox(top_frame, textvariable=self.selected_category, values=categories)
        self.category_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.category_combo.bind('<<ComboboxSelected>>', self.filter_mods)
        
        # Barra de búsqueda
        search_label = tk.Label(top_frame, text="Buscar mods:", fg='white', bg='#111111')
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        search_entry = tk.Entry(top_frame, textvariable=self.search_query)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        search_button = tk.Button(top_frame, text="Buscar", command=self.search_mods)
        search_button.pack(side=tk.LEFT)
        
        # Panel principal dividido
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo (mods instalados)
        installed_frame = tk.Frame(self.paned_window, bg='#1f2937')
        self.paned_window.add(installed_frame)
        
        installed_label = tk.Label(installed_frame, text="Mods Instalados", 
                                 fg='white', bg='#1f2937', font=('Arial', 10, 'bold'))
        installed_label.pack(pady=5)
        
        # Frame para la lista y la barra de desplazamiento
        installed_list_frame = tk.Frame(installed_frame, bg='#1f2937')
        installed_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.installed_listbox = tk.Listbox(installed_list_frame, bg='#1f2937', fg='white',
                                          selectmode=tk.SINGLE, height=20)
        self.installed_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.installed_listbox.bind('<<ListboxSelect>>', self.show_mod_details)
        
        installed_scrollbar = ttk.Scrollbar(installed_list_frame, orient=tk.VERTICAL,
                                          command=self.installed_listbox.yview)
        installed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.installed_listbox.configure(yscrollcommand=installed_scrollbar.set)
        
        # Panel de actualización
        update_frame = tk.Frame(installed_frame, bg='#1f2937')
        update_frame.pack(fill=tk.X, pady=5)
        
        check_updates_button = tk.Button(update_frame, text="Buscar actualizaciones",
                                       command=self.check_updates)
        check_updates_button.pack(pady=5)
        
        self.update_label = tk.Label(update_frame, text="", fg='white', bg='#1f2937')
        self.update_label.pack()
        
        # Panel central (búsqueda de mods)
        search_frame = tk.Frame(self.paned_window, bg='#1f2937')
        self.paned_window.add(search_frame)
        
        search_label = tk.Label(search_frame, text="Resultados de Búsqueda", 
                              fg='white', bg='#1f2937', font=('Arial', 10, 'bold'))
        search_label.pack(pady=5)
        
        # Frame para la lista y la barra de desplazamiento
        search_list_frame = tk.Frame(search_frame, bg='#1f2937')
        search_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.search_listbox = tk.Listbox(search_list_frame, bg='#1f2937', fg='white',
                                       selectmode=tk.SINGLE, height=20)
        self.search_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.search_listbox.bind('<<ListboxSelect>>', self.show_mod_details)
        
        search_scrollbar = ttk.Scrollbar(search_list_frame, orient=tk.VERTICAL,
                                       command=self.search_listbox.yview)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_listbox.configure(yscrollcommand=search_scrollbar.set)
        
        # Panel derecho (detalles del mod)
        details_frame = tk.Frame(self.paned_window, bg='#1f2937', width=300)
        self.paned_window.add(details_frame)
        
        details_label = tk.Label(details_frame, text="Detalles del Mod", 
                               fg='white', bg='#1f2937', font=('Arial', 10, 'bold'))
        details_label.pack(pady=5)
        
        self.details_text = tk.Text(details_frame, bg='#1f2937', fg='white',
                                  wrap=tk.WORD, height=20, width=40)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.details_text.config(state=tk.DISABLED)
        
        # Panel de dependencias
        dep_frame = tk.Frame(details_frame, bg='#1f2937')
        dep_frame.pack(fill=tk.X, pady=5)
        
        dep_label = tk.Label(dep_frame, text="Dependencias:", 
                           fg='white', bg='#1f2937', font=('Arial', 9, 'bold'))
        dep_label.pack(pady=2)
        
        self.dep_listbox = tk.Listbox(dep_frame, bg='#1f2937', fg='white',
                                    height=4)
        self.dep_listbox.pack(fill=tk.X, padx=5)
        
        # Botones de acción
        button_frame = tk.Frame(main_frame, bg='#111111')
        button_frame.pack(fill=tk.X, pady=10)
        
        install_button = tk.Button(button_frame, text="Instalar Mod Seleccionado",
                                 command=self.install_selected_mod)
        install_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = tk.Button(button_frame, text="Eliminar Mod Seleccionado",
                                command=self.remove_selected_mod)
        remove_button.pack(side=tk.LEFT, padx=5)
        
        update_selected_button = tk.Button(button_frame, text="Actualizar Mod Seleccionado",
                                         command=self.update_selected_mod)
        update_selected_button.pack(side=tk.LEFT, padx=5)

    def show_mod_details(self, event=None):
        # Obtener el mod seleccionado de cualquiera de las dos listas
        selected_listbox = None
        if event and event.widget.curselection():
            selected_listbox = event.widget
        
        if not selected_listbox:
            return
            
        mod_name = selected_listbox.get(selected_listbox.curselection())
        
        # Actualizar el panel de detalles
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        if mod_name in self.mod_data:
            mod_info = self.mod_data[mod_name]
            details = f"""Nombre: {mod_name}
Versión: {mod_info.get('version', 'N/A')}
Autor: {mod_info.get('author', 'N/A')}
Categoría: {mod_info.get('category', 'N/A')}
Descargas: {mod_info.get('downloads', 'N/A')}
Última actualización: {mod_info.get('last_updated', 'N/A')}

Descripción:
{mod_info.get('description', 'No hay descripción disponible.')}
"""
            self.details_text.insert(1.0, details)
            
            # Actualizar lista de dependencias
            self.dep_listbox.delete(0, tk.END)
            for dep in mod_info.get('dependencies', []):
                self.dep_listbox.insert(tk.END, dep)
        else:
            self.details_text.insert(1.0, "No hay información disponible para este mod.")
            self.dep_listbox.delete(0, tk.END)
        
        self.details_text.config(state=tk.DISABLED)

    def check_updates(self):
        # Simular verificación de actualizaciones
        updates_available = []
        for mod in self.installed_listbox.get(0, tk.END):
            if mod in self.mod_data:
                current_version = self.mod_data[mod].get('version', '1.0')
                # Simular que hay una actualización disponible
                if current_version.endswith('.0'):
                    updates_available.append(mod)
        
        if updates_available:
            self.update_label.config(text=f"Actualizaciones disponibles: {len(updates_available)} mods",
                                   fg='#22c55e')
        else:
            self.update_label.config(text="Todos los mods están actualizados",
                                   fg='white')

    def update_selected_mod(self):
        selection = self.installed_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un mod para actualizar")
            return
            
        mod_name = self.installed_listbox.get(selection[0])
        # Aquí implementarías la actualización real del mod
        messagebox.showinfo("Actualización", f"Actualizando {mod_name}...")
        self.check_updates()

    def filter_mods(self, event=None):
        category = self.selected_category.get()
        self.search_listbox.delete(0, tk.END)
        
        for mod_name, mod_info in self.mod_data.items():
            if category == "Todas" or mod_info.get('category') == category:
                self.search_listbox.insert(tk.END, mod_name)

    def load_installed_versions(self):
        try:
            installed_versions = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_directory)
            versions = [version['id'] for version in installed_versions]
            self.version_combo['values'] = versions
            if versions:
                self.version_combo.set(versions[0])
                self.load_installed_mods()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar versiones: {e}")

    def load_installed_mods(self):
        version = self.selected_version.get()
        if not version:
            return
            
        mods_directory = os.path.join(self.minecraft_directory, "versions", version, "mods")
        self.installed_listbox.delete(0, tk.END)
        
        if os.path.exists(mods_directory):
            for mod_file in os.listdir(mods_directory):
                if mod_file.endswith(".jar"):
                    self.installed_listbox.insert(tk.END, mod_file)
                    # Simular información del mod
                    self.mod_data[mod_file] = {
                        'version': '1.0',
                        'author': 'Autor Example',
                        'category': 'Tecnología',
                        'downloads': '100,000+',
                        'last_updated': '2024-01-01',
                        'description': 'Este es un mod de ejemplo que hace cosas increíbles.',
                        'dependencies': ['Forge', 'Biblioteca Example']
                    }

    def search_mods(self):
        self.search_listbox.delete(0, tk.END)
        query = self.search_query.get().lower()
        
        # Simulación de resultados de búsqueda con información detallada
        example_mods = {
            "JEI (Just Enough Items)": {
                'version': '2.0',
                'author': 'mezz',
                'category': 'Mejoras',
                'downloads': '1,000,000+',
                'last_updated': '2024-02-15',
                'description': 'JEI es una mod de interfaz de usuario que muestra la lista de items y sus recetas.',
                'dependencies': ['Forge']
            },
            "Optifine": {
                'version': '1.5',
                'author': 'sp614x',
                'category': 'Optimización',
                'downloads': '5,000,000+',
                'last_updated': '2024-01-30',
                'description': 'OptiFine es un mod de optimización que aumenta el FPS y permite texturas HD.',
                'dependencies': []
            },
            "Create Mod": {
                'version': '3.0',
                'author': 'simibubi',
                'category': 'Tecnología',
                'downloads': '800,000+',
                'last_updated': '2024-02-01',
                'description': 'Create añade máquinas y mecanismos rotatorios al juego.',
                'dependencies': ['Forge', 'Flywheel']
            },
            "Botania": {
                'version': '4.0',
                'author': 'Vazkii',
                'category': 'Magia',
                'downloads': '600,000+',
                'last_updated': '2024-02-10',
                'description': 'Botania es un mod de magia técnica basado en la naturaleza.',
                'dependencies': ['Forge', 'Patchouli']
            }
        }
        
        for mod_name, mod_info in example_mods.items():
            if query in mod_name.lower() or query in mod_info['description'].lower():
                self.search_listbox.insert(tk.END, mod_name)
                self.mod_data[mod_name] = mod_info

    def install_selected_mod(self):
        selection = self.search_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un mod para instalar")
            return
            
        mod_name = self.search_listbox.get(selection[0])
        version = self.selected_version.get()
        
        # Verificar dependencias
        if mod_name in self.mod_data:
            dependencies = self.mod_data[mod_name].get('dependencies', [])
            if dependencies:
                missing_deps = []
                for dep in dependencies:
                    # Aquí deberías verificar si las dependencias están instaladas
                    # Por ahora solo simulamos
                    if dep not in [self.installed_listbox.get(i) for i in range(self.installed_listbox.size())]:
                        missing_deps.append(dep)
                
                if missing_deps:
                    if messagebox.askyesno("Dependencias faltantes",
                                         f"Este mod requiere las siguientes dependencias:\n" +
                                         "\n".join(missing_deps) +
                                         "\n\n¿Deseas instalarlas también?"):
                        # Aquí implementarías la instalación de dependencias
                        pass
                    else:
                        return
        
        # Simular instalación
        messagebox.showinfo("Instalación", f"Instalando {mod_name}...")
        self.installed_listbox.insert(tk.END, mod_name)
        self.load_installed_mods()

    def remove_selected_mod(self):
        selection = self.installed_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un mod para eliminar")
            return
            
        mod_name = self.installed_listbox.get(selection[0])
        
        # Verificar si otros mods dependen de este
        dependent_mods = []
        for name, info in self.mod_data.items():
            if mod_name in info.get('dependencies', []):
                dependent_mods.append(name)
        
        if dependent_mods:
            if not messagebox.askyesno("Advertencia",
                                     f"Los siguientes mods dependen de {mod_name}:\n" +
                                     "\n".join(dependent_mods) +
                                     "\n\n¿Deseas eliminar este mod y los que dependen de él?"):
                return
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar {mod_name}?"):
            version = self.selected_version.get()
            mod_path = os.path.join(self.minecraft_directory, "versions", version, "mods", mod_name)
            try:
                # Simular eliminación
                self.installed_listbox.delete(selection)
                messagebox.showinfo("Éxito", f"Mod {mod_name} eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar el mod: {e}")

    def on_version_selected(self, event=None):
        self.load_installed_mods()

class MinecraftLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración básica
        self.title("Minecraft Launcher")
        self.geometry("1024x620")
        self.configure(bg='#111111')
        
        # Configurar directorio de Minecraft
        self.user_windows = os.environ['USERNAME']
        self.minecraft_directory = os.path.join("C:\\Users", self.user_windows, "AppData", "Roaming", ".mcmoder")
        
        # Asegurar que el directorio existe
        if not os.path.exists(self.minecraft_directory):
            os.makedirs(self.minecraft_directory)
        
        # Variables de control
        self.selected_version = tk.StringVar()
        self.new_version = tk.StringVar()
        
        # Crear el contenedor principal
        self.main_container = tk.Frame(self, bg='#111111')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Crear sidebar y contenido principal
        self.create_sidebar()
        self.create_main_content()
        
        # Cargar versiones instaladas
        self.update_installed_versions()

    def update_installed_versions(self):
        try:
            self.installed_versions = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_directory)
            versions = [version['id'] for version in self.installed_versions]
            self.version_selector['values'] = versions
            if versions:
                self.version_selector.set(versions[0])
        except Exception as e:
            print(f"Error al cargar versiones: {e}")

    def install_version(self):
        version = self.new_version.get()
        if version:
            try:
                callback = {
                    "setStatus": lambda text: self.version_status_label.config(text=text),
                    "setProgress": lambda value: None,
                }
                minecraft_launcher_lib.install.install_minecraft_version(version, self.minecraft_directory, callback=callback)
                self.update_installed_versions()
                self.version_status_label.config(text=f"Versión {version} instalada correctamente", fg='#22c55e')
            except Exception as e:
                self.version_status_label.config(text=f"Error al instalar: {e}", fg='red')

    def launch_minecraft(self):
        version = self.selected_version.get()
        if not version:
            return
            
        try:
            options = {
                "username": "moderlauncher",
                "uuid": "123456789",
                "token": "token123",
                "jvmArguments": ["-Xmx2G"],
                "version": version,
                "launcherName": "CustomLauncher",
                "launcherVersion": "1.0"
            }
            
            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                version,
                self.minecraft_directory,
                options
            )
            
            subprocess.Popen(minecraft_command)
            
        except Exception as e:
            print(f"Error al lanzar Minecraft: {e}")
            self.version_status_label.config(text=f"Error al lanzar: {e}", fg='red')

    def create_sidebar(self):
        sidebar = tk.Frame(self.main_container, bg='black', width=256)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Logo y título
        header_frame = tk.Frame(sidebar, bg='black')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(header_frame, text="Minecraft Launcher", 
                             fg='white', bg='black', font=('Arial', 10))
        title_label.pack(side=tk.LEFT)

        # Usuario
        user_frame = tk.Frame(sidebar, bg='black')
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        status_label = tk.Label(user_frame, text="●", fg='#22c55e', bg='black')
        status_label.pack(side=tk.LEFT)
        
        username_label = tk.Label(user_frame, text="ModerLuancher", 
                                fg='white', bg='black', font=('Arial', 10))
        username_label.pack(side=tk.LEFT, padx=5)

        # Estado de conexión
        connection_label = tk.Label(sidebar, text="Conectado", 
                                  fg='gray', bg='black', font=('Arial', 8))
        connection_label.pack(anchor=tk.W, padx=10)

        # Novedades
        news_button = tk.Button(sidebar, text="Novedades", 
                              fg='white', bg='black', bd=0,
                              font=('Arial', 10), relief=tk.FLAT)
        news_button.pack(anchor=tk.W, padx=10, pady=20)

        # Botón de Mods
        mods_button = tk.Button(sidebar, text="Mods", 
                              fg='white', bg='black', bd=0,
                              font=('Arial', 10), relief=tk.FLAT,
                              command=self.open_mods_window)
        mods_button.pack(anchor=tk.W, padx=10, pady=5)

        # Ajustes
        settings_button = tk.Button(sidebar, text="Ajustes", 
                                  fg='white', bg='black', bd=0,
                                  font=('Arial', 10), relief=tk.FLAT)
        settings_button.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=20)

    def create_main_content(self):
        main_content = tk.Frame(self.main_container, bg='#111111')
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de navegación superior
        nav_frame = tk.Frame(main_content, bg='#1f2937')
        nav_frame.pack(fill=tk.X)

        nav_buttons = ['Jugar', 'Instalaciones', 'Aspectos', 'Notas de actualización']
        for i, text in enumerate(nav_buttons):
            color = '#22c55e' if text == 'Jugar' else 'white'
            btn = tk.Button(nav_frame, text=text, fg=color, bg='#1f2937',
                          bd=0, font=('Arial', 10, 'bold' if text == 'Jugar' else 'normal'))
            btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Panel de versiones
        version_frame = tk.Frame(main_content, bg='#111111')
        version_frame.pack(fill=tk.X, padx=20, pady=10)

        # Selector de versión instalada
        version_label = tk.Label(version_frame, text="Versión instalada:", 
                               fg='white', bg='#111111')
        version_label.pack(side=tk.LEFT, padx=5)

        self.version_selector = ttk.Combobox(version_frame, 
                                           textvariable=self.selected_version)
        self.version_selector.pack(side=tk.LEFT, padx=5)

        # Instalador de nueva versión
        install_frame = tk.Frame(version_frame, bg='#111111')
        install_frame.pack(side=tk.RIGHT)

        version_entry = tk.Entry(install_frame, textvariable=self.new_version)
        version_entry.pack(side=tk.LEFT, padx=5)

        install_button = tk.Button(install_frame, text="Instalar versión",
                                 command=self.install_version)
        install_button.pack(side=tk.LEFT, padx=5)

        self.version_status_label = tk.Label(version_frame, text="", 
                                           bg='#111111', fg='white')
        self.version_status_label.pack(side=tk.RIGHT, padx=10)

        # Área de imagen principal
        image_frame = tk.Frame(main_content, bg='#111111')
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        image_label = tk.Label(image_frame, bg='#333333')
        image_label.pack(fill=tk.BOTH, expand=True)

        # Barra inferior
        bottom_frame = tk.Frame(main_content, bg='#1f2937')
        bottom_frame.pack(fill=tk.X)

        # Información de versión seleccionada
        version_info_frame = tk.Frame(bottom_frame, bg='#1f2937')
        version_info_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        version_info_label = tk.Label(version_info_frame, 
                                    textvariable=self.selected_version,
                                    fg='white', bg='#1f2937', font=('Arial', 10))
        version_info_label.pack(anchor=tk.W)

        # Botón de JUGAR
        play_button = tk.Button(bottom_frame, text="JUGAR",
                              fg='black', bg='#22c55e',
                              font=('Arial', 10, 'bold'),
                              padx=20, pady=5,
                              command=self.launch_minecraft)
        play_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Username en la barra inferior
        user_label = tk.Label(bottom_frame, text="Lanzar ➤",
                            fg='white', bg='#1f2937', font=('Arial', 10))
        user_label.pack(side=tk.RIGHT, padx=10)

    def open_mods_window(self):
        mods_window = ModsWindow(self, self.minecraft_directory)
        mods_window.transient(self)
        mods_window.grab_set()

if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()

    