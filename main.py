# Aca importamos la libreria para usar SQLite.
import sqlite3
# Importamos diferentes tipos de anotaciones.
from typing import List, Tuple, Optional

# |||| Configuración de la base de datos ||||

# Instanciamos la BBDD.
DB_NAME = "contactos.db"

# Crear la tabla de contactos.
def crear_tabla_contactos():
    # Inicia la conexión a la BBDD.
    conn = sqlite3.connect(DB_NAME)
    # Crea un cursor para ejecutar sentencias SQL.
    cur = conn.cursor()

    # Ejecuta SQL para crear la tabla contactos si no existe.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            telefono TEXT,
            email TEXT
        );
    """)

    # Aca instanciamos un indice que vamos a utilizar para que no haya duplicados.
    try:
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_contacto_unico
            ON contactos(nombre, apellido, telefono, email);
        """)
    except Exception:
        # Esto sirve en el caso si llega a fallar, no se rompa la app.
        pass

    # Confirma todos los cambios en la BBDD.
    conn.commit()
    # Cierra la conexión con la BBDD.
    conn.close()

# |||| POO ||||

# Definimos la clase contacto.
class Contacto:
    # Las validaciones lo hace en la interfaz.
    def __init__(self, nombre: str, apellido: str = "", telefono: str = "", email: str = ""):
        # Asignamos el nombre.
        self.nombre = nombre
        # Asignamos el apellido.
        self.apellido = apellido
        # Asignamos el telefono.
        self.telefono = telefono
        # Asignamos el mail.
        self.email = email

    def __str__(self):
        # Devuelve un string que muestra nombre, apellido, teléfono y email.
        return f"{self.nombre} {self.apellido} | Tel: {self.telefono} | Email: {self.email}"

# |||| Repositorio, CRUD y Validaciones ||||

# Instanciamos la clase que habla con la BBDD.
class GestorDeContactos:
    # Definimos la ruta de la BBDD.
    def __init__(self, db_path: str = DB_NAME):
        # Abre la conexión.
        self.conn = sqlite3.connect(db_path)
        # Crea el cursor para ejecutar SQL.
        self.cur = self.conn.cursor()

    # Valida el limite de caracteres de los campos.
    @staticmethod
    def _validar_longitudes(nombre: str, apellido: str, telefono: str, email: str):
        # Si el nombre supera 50 caracteres, error.
        if len(nombre) > 50:
            raise ValueError("El nombre supera el máximo de 50 caracteres.")
        # Si el apellido supera 50 caracteres, error.
        if len(apellido) > 50:
            raise ValueError("El apellido supera el máximo de 50 caracteres.")
        # Si el teléfono supera 15 caracteres, error.
        if len(telefono) > 15:
            raise ValueError("El teléfono supera el máximo de 15 caracteres.")
        # Si el email supera 100 caracteres, error.
        if len(email) > 100:
            raise ValueError("El email supera el máximo de 100 caracteres.")

    # Valida campos obligatorios y formats.
    @staticmethod
    def _validar_campos_obligatorios_y_formato(nombre: str, telefono: str, email: str):
        # Verifica que el nombre no este vacio.
        if not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        # Campo teléfono solo usa numeros.
        if telefono and not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        # Campo mail debe tener el @.
        if email and "@" not in email:
            raise ValueError("El email debe contener '@'.")

    # Valida que no se dupliquen los datos.
    def _existe_duplicado(
        self,
        nombre: str,
        apellido: str,
        telefono: str,
        email: str,
        excluir_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        # Estos son los parametros a consultar.
        params = [nombre, apellido, telefono, email]
        # Con SQL buscamos si hay coincidencias.
        sql = (
            "SELECT id FROM contactos "
            "WHERE nombre = ? AND apellido = ? AND telefono = ? AND email = ?"
        )
        # Esto es para que cuando actualicemos no tenga en cuenta el ID ya que se mantiene.
        if excluir_id is not None:
            sql += " AND id <> ?"
            params.append(excluir_id)

        # Lo ejecuta, si hay un resultado es porque es un duplicado exacto.
        rows = self.cur.execute(sql, params).fetchall()
        if rows:
            return True, "Existe un contacto con exactamente los mismos datos."

        # Verifica que el mail no este duplicado.
        if email.strip():
            params_email = [email]
            sql_email = "SELECT id FROM contactos WHERE email = ?"
            if excluir_id is not None:
                sql_email += " AND id <> ?"
                params_email.append(excluir_id)
            rows = self.cur.execute(sql_email, params_email).fetchall()
            if rows:
                return True, "Ya existe un contacto con el mismo email."

        # Verifica que el telefono no este duplicado.
        if telefono.strip():
            params_tel = [telefono]
            sql_tel = "SELECT id FROM contactos WHERE telefono = ?"
            if excluir_id is not None:
                sql_tel += " AND id <> ?"
                params_tel.append(excluir_id)
            rows = self.cur.execute(sql_tel, params_tel).fetchall()
            if rows:
                return True, "Ya existe un contacto con el mismo teléfono."
        return False, ""

    # Agrega un contaco y nos devuelve un ID.
    def agregar_contacto(self, contacto: Contacto) -> int:
        # Valida longitudes.
        self._validar_longitudes(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        # Valida campos.
        self._validar_campos_obligatorios_y_formato(contacto.nombre, contacto.telefono, contacto.email)

        # Verifica que no sea duplicado.
        dup, motivo = self._existe_duplicado(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        if dup:
            raise ValueError(motivo)
        self.cur.execute(
            "INSERT INTO contactos(nombre, apellido, telefono, email) VALUES(?, ?, ?, ?)",
            (contacto.nombre.strip(), contacto.apellido.strip(), contacto.telefono.strip(), contacto.email.strip())
        )
        self.conn.commit()
        # Devuelve el ID.
        return self.cur.lastrowid

    # Obtiene todos los contactos, ordenados por ID del mas nuevo al mas viejo.
    def obtener_todos_los_contactos(self) -> List[Tuple]:
        return self.cur.execute(
            "SELECT id, nombre, apellido, telefono, email FROM contactos ORDER BY id DESC"
        ).fetchall()

    # Elimina un contacto por ID.
    def eliminar_contacto(self, contacto_id: int) -> bool:
        # Ejecuta DELETE para el id seleccionado.
        self.cur.execute("DELETE FROM contactos WHERE id = ?", (contacto_id,))
        # Confirma el cambio.
        self.conn.commit()
        # Valida con rowcount que se elimino.
        return self.cur.rowcount > 0

    # Actualiza un contacto por ID.
    def actualizar_contacto(self, contacto_id: int, contacto: Contacto) -> bool:
        # Valida longitudes.
        self._validar_longitudes(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        # Valida campos.
        self._validar_campos_obligatorios_y_formato(contacto.nombre, contacto.telefono, contacto.email)

        # Verifica que no sea duplicado sin contar el ID.
        dup, motivo = self._existe_duplicado(
            contacto.nombre, contacto.apellido, contacto.telefono, contacto.email,
            excluir_id=contacto_id
        )
        if dup:
            raise ValueError(motivo)

        # Ejecuta el UPDATE.
        self.cur.execute(
            "UPDATE contactos SET nombre = ?, apellido = ?, telefono = ?, email = ? WHERE id = ?",
            (contacto.nombre.strip(), contacto.apellido.strip(), contacto.telefono.strip(), contacto.email.strip(), contacto_id)
        )
        self.conn.commit()
        # Valida con rowcount que se actualizo.
        return self.cur.rowcount > 0

    # Cierra la conexión a la BBDD.
    def cerrar_conexion(self):
        try:
            self.conn.close()
        except Exception:
            pass

# |||| Llamado a la interfaz ||||

# Función principal.
def main():
    # Se asegura que la tabla exista.
    crear_tabla_contactos()

    # Importa lo necesario para la interfaz.
    import tkinter as tk
    from interfaz import crear_interfaz

    # Instancia el repositorio.
    repo = GestorDeContactos(DB_NAME)
    root = tk.Tk()
    # Construye la UI.
    crear_interfaz(root, repo)
    root.mainloop()
    # Se cierra la conexion a la BBDD cuando salimos.
    repo.cerrar_conexion()

# Esto es un seguro cuando usamos modulos
if __name__ == "__main__":
    main()