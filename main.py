import sqlite3
from typing import List, Tuple, Optional

# ============================================================
# Configuración de la base de datos
# ============================================================
DB_NAME = "contactos.db"  # Nombre del archivo SQLite (se crea si no existe)

# ------------------------------------------------------------
# crear_tabla_contactos
# Crea la tabla 'contactos' si no existe. Se intenta además
# crear un índice único para impedir duplicados EXACTOS.
# NOTA: si ya hay duplicados en la BD, la creación del índice
# puede fallar; por eso se hace un try/except para no romper
# la app. La app igualmente valida duplicados antes de insertar.
# ------------------------------------------------------------
def crear_tabla_contactos():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Estructura base de la tabla
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT,
            telefono TEXT,
            email TEXT
        );
    """)

    # Índice único para impedir duplicados EXACTOS (nombre+apellido+telefono+email)
    # Si ya existen duplicados, esta creación puede fallar: lo toleramos.
    try:
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_contacto_unique
            ON contactos(nombre, apellido, telefono, email);
        """)
    except Exception:
        # No detenemos la app; igual validamos duplicados a nivel aplicación.
        pass

    conn.commit()
    conn.close()


# ============================================================
# Modelo (POO simple)
# ============================================================
class Contacto:
    """
    Representa un contacto en memoria. Mantengo esta clase por
    compatibilidad con el enfoque original (POO simple), aunque
    la inserción/actualización la haga el repositorio.
    """
    def __init__(self, nombre: str, apellido: str = "", telefono: str = "", email: str = ""):
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email

    def __str__(self):
        # Representación amigable (útil para logs/debug)
        return f"{self.nombre} {self.apellido} | Tel: {self.telefono} | Email: {self.email}"


# ============================================================
# Repositorio / DAO (acceso a datos)
# Mantiene los mismos nombres para las operaciones CRUD:
#   - agregar_contacto
#   - obtener_todos_los_contactos
#   - eliminar_contacto
#   - actualizar_contacto
# Agregamos validaciones y chequeos de duplicados aquí.
# ============================================================
class GestorDeContactos:
    def __init__(self, db_path: str = DB_NAME):
        # Abrimos una conexión simple a SQLite.
        # En apps Tkinter de escritorio suele ser suficiente.
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    # ---------------------------
    # Validaciones de negocio
    # ---------------------------
    @staticmethod
    def _validar_longitudes(nombre: str, apellido: str, telefono: str, email: str):
        """
        Limita los tamaños para evitar datos extra largos.
        Ajustá estos límites si tu consigna lo requiere.
        """
        if len(nombre) > 50:
            raise ValueError("El nombre supera el máximo de 50 caracteres.")
        if len(apellido) > 50:
            raise ValueError("El apellido supera el máximo de 50 caracteres.")
        if len(telefono) > 15:
            raise ValueError("El teléfono supera el máximo de 15 caracteres.")
        if len(email) > 100:
            raise ValueError("El email supera el máximo de 100 caracteres.")

    @staticmethod
    def _validar_campos_obligatorios_y_formato(nombre: str, telefono: str, email: str):
        """
        - Nombre es obligatorio.
        - Teléfono: si se completa, solo números (isDigit).
        - Email: si se completa, debe contener '@'.
        """
        if not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if telefono and not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        if email and "@" not in email:
            raise ValueError("El email debe contener '@'.")

    def _existe_duplicado(
        self,
        nombre: str,
        apellido: str,
        telefono: str,
        email: str,
        excluir_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Reglas de duplicidad (simples y claras):
        - Duplicado EXACTO: (nombre, apellido, telefono, email) idénticos.
        - Duplicado por email: si 'email' no está vacío y ya existe en otro registro.
        - Duplicado por teléfono: si 'telefono' no está vacío y ya existe en otro registro.
        """
        # 1) Duplicado exacto
        params = [nombre, apellido, telefono, email]
        sql = (
            "SELECT id FROM contactos "
            "WHERE nombre = ? AND apellido = ? AND telefono = ? AND email = ?"
        )
        if excluir_id is not None:
            sql += " AND id <> ?"
            params.append(excluir_id)

        rows = self.cur.execute(sql, params).fetchall()
        if rows:
            return True, "Existe un contacto con exactamente los mismos datos."

        # 2) Mismo email (si no está vacío)
        if email.strip():
            params_email = [email]
            sql_email = "SELECT id FROM contactos WHERE email = ?"
            if excluir_id is not None:
                sql_email += " AND id <> ?"
                params_email.append(excluir_id)
            rows = self.cur.execute(sql_email, params_email).fetchall()
            if rows:
                return True, "Ya existe un contacto con el mismo email."

        # 3) Mismo teléfono (si no está vacío)
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

    # ---------------------------
    # CRUD
    # ---------------------------
    def agregar_contacto(self, contacto: Contacto) -> int:
        """
        Inserta un contacto en la base.
        Mantengo la firma usando un objeto Contacto (estilo original).
        """
        # Validaciones previas
        self._validar_longitudes(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        self._validar_campos_obligatorios_y_formato(contacto.nombre, contacto.telefono, contacto.email)

        # Chequeo de duplicados
        dup, motivo = self._existe_duplicado(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        if dup:
            raise ValueError(motivo)

        # Insert simple
        self.cur.execute(
            "INSERT INTO contactos(nombre, apellido, telefono, email) VALUES(?, ?, ?, ?)",
            (contacto.nombre.strip(), contacto.apellido.strip(), contacto.telefono.strip(), contacto.email.strip())
        )
        self.conn.commit()
        return self.cur.lastrowid

    def obtener_todos_los_contactos(self) -> List[Tuple]:
        # Devuelve lista de tuplas (id, nombre, apellido, telefono, email)
        return self.cur.execute(
            "SELECT id, nombre, apellido, telefono, email FROM contactos ORDER BY id DESC"
        ).fetchall()

    def eliminar_contacto(self, contacto_id: int) -> bool:
        self.cur.execute("DELETE FROM contactos WHERE id = ?", (contacto_id,))
        self.conn.commit()
        return self.cur.rowcount > 0  # True si borró algo

    def actualizar_contacto(self, contacto_id: int, contacto: Contacto) -> bool:
        """
        Actualiza un registro por ID.
        Se aplican las mismas validaciones y reglas de duplicados,
        excluyendo el propio ID (para que permita "re-guardar" igual).
        """
        self._validar_longitudes(contacto.nombre, contacto.apellido, contacto.telefono, contacto.email)
        self._validar_campos_obligatorios_y_formato(contacto.nombre, contacto.telefono, contacto.email)

        dup, motivo = self._existe_duplicado(
            contacto.nombre, contacto.apellido, contacto.telefono, contacto.email,
            excluir_id=contacto_id
        )
        if dup:
            raise ValueError(motivo)

        self.cur.execute(
            "UPDATE contactos SET nombre = ?, apellido = ?, telefono = ?, email = ? WHERE id = ?",
            (contacto.nombre.strip(), contacto.apellido.strip(), contacto.telefono.strip(), contacto.email.strip(), contacto_id)
        )
        self.conn.commit()
        return self.cur.rowcount > 0

    def cerrar_conexion(self):
        # Cerrar conexión al salir de la app
        try:
            self.conn.close()
        except Exception:
            pass


# ============================================================
# Punto de entrada (main)
# Llama a la interfaz Tkinter que movimos a 'interfaz.py'
# ============================================================
def main():
    # Creamos la tabla si no existe (idempotente)
    crear_tabla_contactos()

    # Import tardío de la UI para no crear dependencias circulares
    import tkinter as tk
    from interfaz import crear_interfaz

    # Creamos el repositorio y lanzamos la ventana principal
    repo = GestorDeContactos(DB_NAME)
    root = tk.Tk()
    crear_interfaz(root, repo)  # Construye la UI y deja todo listo
    root.mainloop()
    repo.cerrar_conexion()      # Cerramos la conexión al salir


if __name__ == "__main__":
    main()
