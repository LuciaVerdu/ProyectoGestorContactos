# Importa Tkinter.
import tkinter as tk
# Importa complementos de Tkinter.
from tkinter import ttk, messagebox

# |||| Validacion de campos en la interfaz ||||

# Límite maximo de caracteres para nombre.
NAME_MAX = 50
# Límite maximo de caracteres para apellido.
LASTNAME_MAX = 50
# Límite maximo de caracteres para teléfono.
PHONE_MAX = 15
# Límite maximo de caracteres para email.
EMAIL_MAX = 100

# Aca crea la interfaz.
def crear_interfaz(root: tk.Tk, gestor):
    # Título de la ventana.
    root.title("Gestor de Contactos")
    # Dimensiones.
    root.geometry("840x580")
    # Campo “Nombre”.
    var_nombre = tk.StringVar()
    # Campo “Apellido”.
    var_apellido = tk.StringVar()
    # Campo “Telefono”.
    var_telefono = tk.StringVar()
    # Campo “Email”.
    var_email = tk.StringVar()

    # Validacion para longitud maxima.
    def vc_maxlen(maxlen: int, var: tk.StringVar):
        def _inner(proposed: str) -> bool:
            # Habilita cargar mientras no supere el max.
            if len(proposed) <= maxlen:
                return True
            # Si pasa el limite borra el resto.
            root.after(0, lambda: var.set(var.get()[:maxlen]))
            return False
        return _inner

    # Validacion para teléfono.
    def vc_phone(maxlen: int, var: tk.StringVar):
        def _inner(proposed: str) -> bool:
            # Si se pasa del max, borra y rechaza.
            if len(proposed) > maxlen:
                root.after(0, lambda: var.set(var.get()[:maxlen]))
                return False
            # Acepta solo dígitos.
            if proposed == "" or proposed.isdigit():
                return True
            # Rechaza si contiene datos no numericos.
            return False
        return _inner

    # Valida el formulario.
    def form_es_valido() -> bool:
        # Lee nombre, telefono y email.
        nombre = var_nombre.get().strip()
        telefono = var_telefono.get().strip()
        email = var_email.get().strip()

        # Valida que no este vacío.
        if not nombre:
            return False
        # Email opcional, pero si existed debe tener @.
        if email and ("@" not in email):
            return False
        # Valida longitudes.
        if len(nombre) > NAME_MAX or len(var_apellido.get()) > LASTNAME_MAX:
            return False
        if len(telefono) > PHONE_MAX or len(email) > EMAIL_MAX:
            return False
        return True

    # Si el formulario es valido habilita el boton Agregar.
    def refrescar_estado_boton_agregar():
        btn_agregar.configure(state=("normal" if form_es_valido() else "disabled"))

    # Cada cambio revalida el estado del botón Agregar.
    for var in (var_nombre, var_apellido, var_telefono, var_email):
        var.trace_add("write", lambda *_: refrescar_estado_boton_agregar())

    # |||| Formulario ||||

    # Campos de entrada.
    frm_inputs = tk.Frame(root)
    frm_inputs.pack(pady=10)

    # Etiqueta “Nombre”.
    tk.Label(frm_inputs, text="Nombre:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
    e_nombre = tk.Entry(frm_inputs, textvariable=var_nombre, validate="key")
    # Registra el validador de longitud max.
    e_nombre["validatecommand"] = (root.register(vc_maxlen(NAME_MAX, var_nombre)), "%P")
    # Coloca el Entry en la grilla.
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    # Etiqueta “Apellido”.
    tk.Label(frm_inputs, text="Apellido:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
    e_apellido = tk.Entry(frm_inputs, textvariable=var_apellido, validate="key")
    # Registra el validador de longitud max.
    e_apellido["validatecommand"] = (root.register(vc_maxlen(LASTNAME_MAX, var_apellido)), "%P")
    # Coloca el Entry en la grilla.
    e_apellido.grid(row=1, column=1, padx=6, pady=6)

    # Etiqueta “Teléfono”.
    tk.Label(frm_inputs, text="Teléfono:").grid(row=2, column=0, padx=6, pady=6, sticky="e")
    e_telefono = tk.Entry(frm_inputs, textvariable=var_telefono, validate="key")
    # Registra el validador de longitud max.
    e_telefono["validatecommand"] = (root.register(vc_phone(PHONE_MAX, var_telefono)), "%P")
    # Coloca el Entry en la grilla.
    e_telefono.grid(row=2, column=1, padx=6, pady=6)

    # Etiqueta “Email”.
    tk.Label(frm_inputs, text="Email:").grid(row=3, column=0, padx=6, pady=6, sticky="e")
    e_email = tk.Entry(frm_inputs, textvariable=var_email, validate="key")
    # Registra el validador de longitud max.
    e_email["validatecommand"] = (root.register(vc_maxlen(EMAIL_MAX, var_email)), "%P")
    # Coloca el Entry en la grilla.
    e_email.grid(row=3, column=1, padx=6, pady=6)

    # |||| Botones ||||

    # Cntenedor de los botones principales.
    frm_buttons = tk.Frame(root)
    frm_buttons.pack(pady=8)

    # Crea el botón “Agregar”.
    btn_agregar = tk.Button(frm_buttons, text="Agregar")
    # Ubica el botón Agregar.
    btn_agregar.grid(row=0, column=0, padx=6, pady=6)

    # Crea el botón “Listar”.
    btn_listar = tk.Button(frm_buttons, text="Listar")
    # Ubica el botón Listar.
    btn_listar.grid(row=0, column=1, padx=6, pady=6)

    # Crea el botón “Eliminar”.
    btn_eliminar = tk.Button(frm_buttons, text="Eliminar")
    # Ubica el botón Eliminar.
    btn_eliminar.grid(row=0, column=2, padx=6, pady=6)

    # Crea el botón “Actualizar”.
    btn_actualizar = tk.Button(frm_buttons, text="Actualizar")
    # Ubica el botón Actualizar.
    btn_actualizar.grid(row=0, column=3, padx=6, pady=6)

    # El boton “Agregar” su estado inicial es deshabilitado.
    btn_agregar.configure(state="disabled")

    # |||| Grilla ||||

    # Contenedor de la grilla y un scroll.
    frm_list = tk.Frame(root)
    frm_list.pack(padx=10, pady=10, fill="both", expand=True)

    # Define las columnas de la grilla.
    columnas = ("id", "nombre", "apellido", "telefono", "email")
    # Crea la grilla mostrando los encabezados.
    tree = ttk.Treeview(frm_list, columns=columnas, show="headings", height=14)
    # Configura encabezados y anchos de columna.
    for c in columnas:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=150 if c != "id" else 60, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Crea una barra de scroll
    sb = ttk.Scrollbar(frm_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")

    # |||| Funciones de los Botones ||||

    # Limpia los campos y valida el boton Agregar.
    def limpiar_inputs():
        var_nombre.set("")
        var_apellido.set("")
        var_telefono.set("")
        var_email.set("")
        refrescar_estado_boton_agregar()

    # Actualiza la grilla desde la BD cuando se presiona Listar.
    def listar_contactos_gui():
        try:
            # Pide todos los contactos.
            registros = gestor.obtener_todos_los_contactos()
            # Limpia todas las filas.
            for r in tree.get_children():
                tree.delete(r)
            # Inserta cada fila.
            for fila in registros:
                tree.insert("", "end", values=fila)
            # Limpia los campos del formulario después de listar.
            limpiar_inputs()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar.\n{e}")

    # Agrega un nuevo contacto cuando se presiona Agregar.
    def agregar_contacto_gui():
        try:
            from main import Contacto
            # Construye el Contacto con los datos de los campos.
            c = Contacto(
                nombre=var_nombre.get().strip(),
                apellido=var_apellido.get().strip(),
                telefono=var_telefono.get().strip(),
                email=var_email.get().strip(),
            )
            # Llama al repositorio para insertar y obtiene el ID del nuevo contacto.
            nuevo_id = gestor.agregar_contacto(c)
            # Notifica que se agregó correctamente.
            messagebox.showinfo("OK", f"Contacto agregado (ID {nuevo_id}).")
            # Limpia los campos.
            limpiar_inputs()
        except ValueError as ve:
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el contacto.\n{e}")

    # Elimina el contacto seleccionado cuando se presiona Eliminar.
    def eliminar_contacto_gui():
        # Obtiene la selección actual de la grilla.
        sel = tree.selection()
        # Si no hay selección nos avisa.
        if not sel:
            messagebox.showinfo("Atención", "Seleccione un contacto en la tabla.")
            return
        # Obtiene el ítem seleccionado y el ID.
        item = tree.item(sel[0])
        contacto_id = int(item["values"][0])
        try:
            # Llama al repositorio.
            ok = gestor.eliminar_contacto(contacto_id)
            if ok:
                # Si borró lo notifica.
                messagebox.showinfo("OK", "Contacto eliminado.")
                # Limpia los campos.
                limpiar_inputs()
            else:
                messagebox.showwarning("Atención", "No se encontró el contacto para eliminar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\n{e}")

    # Actualiza el contacto seleccionado cuando se presiona Actualizar.
    def actualizar_contacto_gui():
        # Verifica que haya una fila seleccionada en la grilla.
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Atención", "Seleccione un contacto en la tabla.")
            return

        # Verifica que el formulario sea valido.
        if not form_es_valido():
            messagebox.showwarning("Validación", "Complete campos válidos antes de actualizar.")
            return

        # Obtiene el ID de la fila seleccionada.
        item = tree.item(sel[0])
        contacto_id = int(item["values"][0])

        try:
            from main import Contacto
            c = Contacto(
                nombre=var_nombre.get().strip(),
                apellido=var_apellido.get().strip(),
                telefono=var_telefono.get().strip(),
                email=var_email.get().strip(),
            )
            # Llama al repositorio para actualizar.
            ok = gestor.actualizar_contacto(contacto_id, c)
            if ok:
                messagebox.showinfo("OK", "Contacto actualizado.")
                # Limpia los campos.
                limpiar_inputs()
            else:
                messagebox.showwarning("Atención", "No se encontró el contacto para actualizar.")
        except ValueError as ve:
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar.\n{e}")

    # Asocia el botón “Agregar” con su función.
    btn_agregar.configure(command=agregar_contacto_gui)
    # Asocia el botón “Listar” con su función.
    btn_listar.configure(command=listar_contactos_gui)
    # Asocia el botón “Eliminar” con su función.
    btn_eliminar.configure(command=eliminar_contacto_gui)
    # Asocia el botón “Actualizar” con su función.
    btn_actualizar.configure(command=actualizar_contacto_gui)

    # Esto permite que cuando seleccionamos un registro carge sus datos en los campos, para que si deseamos actualizar sea mas facil.
    def on_select_row(_evt):
        # Toma la selección actual de la grilla.
        sel = tree.selection()
        # Si no hay selección, no hace nada.
        if not sel:
            return
        # Obtiene el contenido del item seleccionado.
        item = tree.item(sel[0])
        _id, nombre, apellido, telefono, email = item["values"]
        # Pasa los valores a los campos.
        var_nombre.set(nombre)
        var_apellido.set(apellido)
        var_telefono.set(telefono)
        var_email.set(email)
        refrescar_estado_boton_agregar()

    tree.bind("<<TreeviewSelect>>", on_select_row)

    # Al iniciar se evalua el boton Agregar.
    refrescar_estado_boton_agregar()
