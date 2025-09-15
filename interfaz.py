import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# Parámetros de validación en UI (ajustables)
# ============================================================
NAME_MAX = 50
LASTNAME_MAX = 50
PHONE_MAX = 15
EMAIL_MAX = 100

# ------------------------------------------------------------
# crear_interfaz
# Construye toda la UI (antes estaba en el mismo archivo).
# Mantenemos nombres y estructura parecida:
# - Entradas: Nombre / Apellido / Teléfono / Email
# - Botones: Agregar / Listar / Eliminar / Actualizar
# - Treeview para mostrar la lista de contactos
# Regla pedida: NO listar automáticamente al inicio.
# ------------------------------------------------------------
def crear_interfaz(root: tk.Tk, gestor):
    root.title("Gestor de Contactos")
    root.geometry("840x580")

    # ---------------------------
    # Variables de formulario
    # ---------------------------
    var_nombre = tk.StringVar()
    var_apellido = tk.StringVar()
    var_telefono = tk.StringVar()
    var_email = tk.StringVar()

    # ---------------------------
    # Validadores de entrada
    # Usamos 'validate="key"' + validatecommand por campo.
    # - Máximo de caracteres (nombre/apellido/email).
    # - Teléfono: solo dígitos + longitud máxima.
    # ---------------------------
    def vc_maxlen(maxlen: int, var: tk.StringVar):
        """Validador genérico de longitud máxima."""
        def _inner(proposed: str) -> bool:
            if len(proposed) <= maxlen:
                return True
            # Si se excede, recortamos de inmediato (comportamiento amigable)
            root.after(0, lambda: var.set(var.get()[:maxlen]))
            return False
        return _inner

    def vc_phone(maxlen: int, var: tk.StringVar):
        """Validador para teléfono: solo dígitos y límite."""
        def _inner(proposed: str) -> bool:
            if len(proposed) > maxlen:
                root.after(0, lambda: var.set(var.get()[:maxlen]))
                return False
            # Permitimos vacío mientras escribe; si hay contenido, solo dígitos
            if proposed == "" or proposed.isdigit():
                return True
            return False
        return _inner

    # ---------------------------
    # Form es válido (habilita "Agregar")
    # Reglas: nombre obligatorio; email si existe debe tener '@';
    # los límites ya se controlan en tiempo real.
    # ---------------------------
    def form_es_valido() -> bool:
        nombre = var_nombre.get().strip()
        telefono = var_telefono.get().strip()
        email = var_email.get().strip()

        if not nombre:
            return False
        if email and ("@" not in email):
            return False
        if len(nombre) > NAME_MAX or len(var_apellido.get()) > LASTNAME_MAX:
            return False
        if len(telefono) > PHONE_MAX or len(email) > EMAIL_MAX:
            return False
        return True

    def refrescar_estado_boton_agregar():
        btn_agregar.configure(state=("normal" if form_es_valido() else "disabled"))

    # Cada cambio en inputs reevalúa el estado del botón Agregar
    for var in (var_nombre, var_apellido, var_telefono, var_email):
        var.trace_add("write", lambda *_: refrescar_estado_boton_agregar())

    # ---------------------------
    # Layout: formulario
    # ---------------------------
    frm_inputs = tk.Frame(root)
    frm_inputs.pack(pady=10)

    tk.Label(frm_inputs, text="Nombre:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
    e_nombre = tk.Entry(frm_inputs, textvariable=var_nombre, validate="key")
    e_nombre["validatecommand"] = (root.register(vc_maxlen(NAME_MAX, var_nombre)), "%P")
    e_nombre.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(frm_inputs, text="Apellido:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
    e_apellido = tk.Entry(frm_inputs, textvariable=var_apellido, validate="key")
    e_apellido["validatecommand"] = (root.register(vc_maxlen(LASTNAME_MAX, var_apellido)), "%P")
    e_apellido.grid(row=1, column=1, padx=6, pady=6)

    tk.Label(frm_inputs, text="Teléfono:").grid(row=2, column=0, padx=6, pady=6, sticky="e")
    e_telefono = tk.Entry(frm_inputs, textvariable=var_telefono, validate="key")
    e_telefono["validatecommand"] = (root.register(vc_phone(PHONE_MAX, var_telefono)), "%P")
    e_telefono.grid(row=2, column=1, padx=6, pady=6)

    tk.Label(frm_inputs, text="Email:").grid(row=3, column=0, padx=6, pady=6, sticky="e")
    e_email = tk.Entry(frm_inputs, textvariable=var_email, validate="key")
    e_email["validatecommand"] = (root.register(vc_maxlen(EMAIL_MAX, var_email)), "%P")
    e_email.grid(row=3, column=1, padx=6, pady=6)

    # ---------------------------
    # Botones de acción
    # ---------------------------
    frm_buttons = tk.Frame(root)
    frm_buttons.pack(pady=8)

    btn_agregar = tk.Button(frm_buttons, text="Agregar")
    btn_agregar.grid(row=0, column=0, padx=6, pady=6)

    btn_listar = tk.Button(frm_buttons, text="Listar")
    btn_listar.grid(row=0, column=1, padx=6, pady=6)

    btn_eliminar = tk.Button(frm_buttons, text="Eliminar")
    btn_eliminar.grid(row=0, column=2, padx=6, pady=6)

    btn_actualizar = tk.Button(frm_buttons, text="Actualizar")
    btn_actualizar.grid(row=0, column=3, padx=6, pady=6)

    # Deshabilitamos Agregar al inicio hasta que el formulario sea válido
    btn_agregar.configure(state="disabled")

    # ---------------------------
    # Grilla (Treeview) para mostrar contactos
    # Regla: NO cargamos automáticamente al inicio.
    # ---------------------------
    frm_list = tk.Frame(root)
    frm_list.pack(padx=10, pady=10, fill="both", expand=True)

    columnas = ("id", "nombre", "apellido", "telefono", "email")
    tree = ttk.Treeview(frm_list, columns=columnas, show="headings", height=14)
    for c in columnas:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=150 if c != "id" else 60, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frm_list, orient="vertical", command=tree.yview)
    tree.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")

    # ---------------------------
    # Funciones de botones
    # Mantienen nombres/estilo cercano al original
    # ---------------------------
    def limpiar_inputs():
        var_nombre.set("")
        var_apellido.set("")
        var_telefono.set("")
        var_email.set("")
        refrescar_estado_boton_agregar()

    def listar_contactos_gui():
        """
        Limpia la grilla y carga los registros desde la BD.
        Se llama SOLO cuando se presiona el botón 'Listar'
        (cumpliendo tu requerimiento de no actualizar automáticamente).
        """
        try:
            registros = gestor.obtener_todos_los_contactos()
            # Limpiar grilla
            for r in tree.get_children():
                tree.delete(r)
            # Insertar filas
            for fila in registros:
                tree.insert("", "end", values=fila)
            # Limpiar campos del formulario
            limpiar_inputs()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar.\n{e}")

    def agregar_contacto_gui():
        """
        Valida y agrega un contacto.
        No refresca la grilla automáticamente (debe presionar 'Listar').
        """
        try:
            # Creamos Contacto para mantener la idea original de POO
            from main import Contacto  # import local para evitar ciclos
            c = Contacto(
                nombre=var_nombre.get().strip(),
                apellido=var_apellido.get().strip(),
                telefono=var_telefono.get().strip(),
                email=var_email.get().strip(),
            )
            nuevo_id = gestor.agregar_contacto(c)
            messagebox.showinfo("OK", f"Contacto agregado (ID {nuevo_id}).")
            limpiar_inputs()
        except ValueError as ve:
            # Errores de validación (formato, longitudes, duplicados, etc.)
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el contacto.\n{e}")

    def eliminar_contacto_gui():
        """
        Elimina el contacto seleccionado por ID.
        No refresca automáticamente la grilla.
        """
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Atención", "Seleccione un contacto en la tabla.")
            return
        item = tree.item(sel[0])
        contacto_id = int(item["values"][0])
        try:
            ok = gestor.eliminar_contacto(contacto_id)
            if ok:
                messagebox.showinfo("OK", "Contacto eliminado.")
                # Limpiar campos del formulario
                limpiar_inputs()
            else:
                messagebox.showwarning("Atención", "No se encontró el contacto para eliminar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar.\n{e}")

    def actualizar_contacto_gui():
        """
        Actualiza el contacto seleccionado con los datos de los inputs.
        No refresca automáticamente la grilla.
        """
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Atención", "Seleccione un contacto en la tabla.")
            return

        # Verificación rápida de formulario válido (coincidente con botón Agregar)
        if not form_es_valido():
            messagebox.showwarning("Validación", "Complete campos válidos antes de actualizar.")
            return

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
            ok = gestor.actualizar_contacto(contacto_id, c)
            if ok:
                messagebox.showinfo("OK", "Contacto actualizado.")
                # Limpiar campos del formulario
                limpiar_inputs()
            else:
                messagebox.showwarning("Atención", "No se encontró el contacto para actualizar.")
        except ValueError as ve:
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar.\n{e}")

    # ---------------------------
    # Bindings y wiring de botones
    # ---------------------------
    btn_agregar.configure(command=agregar_contacto_gui)
    btn_listar.configure(command=listar_contactos_gui)
    btn_eliminar.configure(command=eliminar_contacto_gui)
    btn_actualizar.configure(command=actualizar_contacto_gui)

    # Cuando seleccionamos una fila en la grilla, volcamos sus datos a los inputs
    def on_select_row(_evt):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        _id, nombre, apellido, telefono, email = item["values"]
        var_nombre.set(nombre)
        var_apellido.set(apellido)
        var_telefono.set(telefono)
        var_email.set(email)
        refrescar_estado_boton_agregar()

    tree.bind("<<TreeviewSelect>>", on_select_row)

    # Al inicio: NO listamos (cumple tu punto 4)
    refrescar_estado_boton_agregar()
