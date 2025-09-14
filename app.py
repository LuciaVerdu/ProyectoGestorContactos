import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
# Nombre del archivo de la base de datos que estoy creando
DB_NAME = 'contactos.db'
#esta funcion hace que se conecte python con la base y si no existe la crea con execute y create table
def crear_tabla_contactos():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            telefono TEXT,
            email TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos y tabla 'contactos' creadas con éxito.")

#Comienzo a crear la clase CONTACTOS
class Contacto:
    
#metodo INIT que se ejecuta cada vez que se crea un nuevo objeto (contacto)
    def __init__(self, nombre, apellido, telefono, email):
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
#metodo que ayuda a mostrar en cadena la informacion que registra de cada contacto agregado
    def __str__(self):  #el metodo STR hace que al retornar la informacion de cada objeto sea en formato texto 
        return f"Nombre: {self.nombre} {self.apellido}\nTeléfono: {self.telefono}\nEmail: {self.email}"

#creo la clase gestor de contactos que contendra los metodos a realizar
class GestorDeContactos:
    def __init__(self):   #conexion con la base de datos
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
#metodo para agregar contactos. Va a recibir un objeto generado en la clase CONTACTOS.
    def agregar_contacto(self, contacto):
     #sentencia SQL INSERT para guardar los atributos en la tabla de la base de datos de cada objeto recibido
        try:
            self.cursor.execute('''
                INSERT INTO contactos (nombre, apellido, telefono, email)
                VALUES (?, ?, ?, ?)
            ''', (contacto.nombre, contacto.apellido, contacto.telefono, contacto.email))
            self.conn.commit()
            print("Contacto agregado con éxito.")
        except sqlite3.Error as e:
            print(f"Error al agregar contacto: {e}")
#este metodo es para listar todos los objetos la tabla de contactos que fueron agregandose.
    def obtener_todos_los_contactos(self):
       
        self.cursor.execute("SELECT * FROM contactos") #utilizo sentencia SELECT para seleccionar de esta tabla y listarlos
        contactos = self.cursor.fetchall()
        return contactos
#se cierra la conexion con la base de datos
    def cerrar_conexion(self):
       
        self.conn.close()
#metodo para eliminar un contacto por su ID.
    def eliminar_contacto(self, contacto_id):
        
        try:
            self.cursor.execute("DELETE FROM contactos WHERE id = ?", (contacto_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"Contacto con ID {contacto_id} eliminado con éxito.")
                return True
            else:
                print(f"No se encontró un contacto con ID {contacto_id}.")
                return False
        except sqlite3.Error as e:
            print(f"Error al eliminar contacto: {e}")
            return False
#metodo para modificar un objeto contacto ya agregado
    def actualizar_contacto(self, contacto_id, nuevos_datos): #recibe el ID y una tupla/lista de los nuevos datos.
        
        try:
            self.cursor.execute('''
                UPDATE contactos
                SET nombre = ?, apellido = ?, telefono = ?, email = ?
                WHERE id = ?
            ''', (nuevos_datos.nombre, nuevos_datos.apellido, nuevos_datos.telefono, nuevos_datos.email, contacto_id))
            self.conn.commit()
            if self.cursor.rowcount > 0:    #rowcount confirma si el contacto existia o no
                print(f"Contacto con ID {contacto_id} actualizado con éxito.")
                return True
            else:
                print(f"No se encontró un contacto con ID {contacto_id} para actualizar.")
                return False
        except sqlite3.Error as e:
            print(f"Error al actualizar contacto: {e}")
            return False

# Función principal para crear la ventana y los widgets de la GUI.

def crear_interfaz():
   
    root = tk.Tk()
    root.title("Gestor de Contactos")
    root.geometry("800x600")

    # 1. Crear el gestor de contactos
    gestor = GestorDeContactos()

    # --- Funciones de la Lógica del Botón ---

    def agregar_contacto_gui():
        nombre = nombre_entry.get()
        apellido = apellido_entry.get()
        telefono = telefono_entry.get()
        email = email_entry.get()

        if nombre and telefono:
            nuevo_contacto = Contacto(nombre, apellido, telefono, email)
            gestor.agregar_contacto(nuevo_contacto)
            # Limpiar los campos después de agregar
            nombre_entry.delete(0, tk.END)
            apellido_entry.delete(0, tk.END)
            telefono_entry.delete(0, tk.END)
            email_entry.delete(0, tk.END)
            messagebox.showinfo("Éxito", "Contacto agregado con éxito.")
            listar_contactos_gui() # Actualizar la lista
        else:
            messagebox.showerror("Error", "Los campos Nombre y Teléfono son obligatorios.")

    def listar_contactos_gui():
        # Limpiar la tabla Treeview antes de insertar nuevos datos
        for item in tree.get_children():
            tree.delete(item)

        contactos = gestor.obtener_todos_los_contactos()
        for contacto in contactos:
            tree.insert('', tk.END, values=contacto)

    def eliminar_contacto_gui():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione un contacto para eliminar.")
            return

        respuesta = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar el contacto seleccionado?")
        if respuesta:
            contacto_id = tree.item(seleccion, 'values')[0]
            if gestor.eliminar_contacto(contacto_id):
                messagebox.showinfo("Éxito", "Contacto eliminado con éxito.")
                listar_contactos_gui()

    def actualizar_contacto_gui():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione un contacto para actualizar.")
            return
        
        contacto_id = tree.item(seleccion, 'values')[0]
        nombre = nombre_entry.get()
        apellido = apellido_entry.get()
        telefono = telefono_entry.get()
        email = email_entry.get()

        if nombre and telefono:
            nuevos_datos = Contacto(nombre, apellido, telefono, email)
            if gestor.actualizar_contacto(contacto_id, nuevos_datos):
                messagebox.showinfo("Éxito", "Contacto actualizado con éxito.")
                listar_contactos_gui()
                # Limpiar los campos después de actualizar
                nombre_entry.delete(0, tk.END)
                apellido_entry.delete(0, tk.END)
                telefono_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Los campos Nombre y Teléfono son obligatorios.")

    # --- Widgets de la Interfaz ---
    # (Mantenemos los mismos widgets que ya tienes, solo agregamos un ListView)

    # Contenedor para los campos de entrada
    frame_entradas = tk.Frame(root)
    frame_entradas.pack(pady=10)

    # Widgets de entrada (mantener)
    nombre_label = tk.Label(frame_entradas, text="Nombre:")
    nombre_label.grid(row=0, column=0, padx=5, pady=5)
    nombre_entry = tk.Entry(frame_entradas)
    nombre_entry.grid(row=0, column=1, padx=5, pady=5)

    # ... (El resto de los widgets de entrada como apellido, telefono, email) ...
    apellido_label = tk.Label(frame_entradas, text="Apellido:")
    apellido_label.grid(row=1, column=0, padx=5, pady=5)
    apellido_entry = tk.Entry(frame_entradas)
    apellido_entry.grid(row=1, column=1, padx=5, pady=5)

    telefono_label = tk.Label(frame_entradas, text="Teléfono:")
    telefono_label.grid(row=2, column=0, padx=5, pady=5)
    telefono_entry = tk.Entry(frame_entradas)
    telefono_entry.grid(row=2, column=1, padx=5, pady=5)

    email_label = tk.Label(frame_entradas, text="Email:")
    email_label.grid(row=3, column=0, padx=5, pady=5)
    email_entry = tk.Entry(frame_entradas)
    email_entry.grid(row=3, column=1, padx=5, pady=5)

    # Contenedor para los botones
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Botones
    agregar_button = tk.Button(button_frame, text="Agregar Contacto", command=agregar_contacto_gui)
    agregar_button.grid(row=0, column=0, padx=5)

    listar_button = tk.Button(button_frame, text="Listar Contactos", command=listar_contactos_gui)
    listar_button.grid(row=0, column=1, padx=5)

    eliminar_button = tk.Button(button_frame, text="Eliminar Contacto", command=eliminar_contacto_gui)
    eliminar_button.grid(row=0, column=2, padx=5)

    actualizar_button = tk.Button(button_frame, text="Actualizar Contacto", command=actualizar_contacto_gui)
    actualizar_button.grid(row=0, column=3, padx=5)

    # Tabla para mostrar los contactos (Treeview)
    lista_frame = tk.Frame(root)
    lista_frame.pack(pady=10)

    columnas = ("ID", "Nombre", "Apellido", "Teléfono", "Email")
    tree = ttk.Treeview(lista_frame, columns=columnas, show='headings')

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(side="left", fill="y")

    # Scrollbar
    scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # --- Bucle Principal de la GUI ---
    listar_contactos_gui() # Cargar la lista al inicio
    root.mainloop()

    # Cerrar la conexión de la BD al salir de la GUI
    gestor.cerrar_conexion()





# la llamada a funcion de la interfaz y a la crear tabla de contactos
if __name__ == "__main__":
    crear_tabla_contactos()
    crear_interfaz()