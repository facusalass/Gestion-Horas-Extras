import sqlite3

class DataBase:
    def __init__(self, db_name="sistema_jornales.db"):
        self.db_name = db_name
        self.crear_tablas()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def crear_tablas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuil TEXT,
                nombre TEXT UNIQUE,
                tareas TEXT,
                modalidad TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER,
                fecha TEXT,
                concepto TEXT,
                monto_remunerativo REAL,
                hs_50 REAL,
                hs_100 REAL,
                FOREIGN KEY(id_empleado) REFERENCES empleados(id)
            )
        """)
        conn.commit()
        conn.close()

    def agregar_empleado(self, cuil, nombre, tareas, modalidad):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO empleados (cuil, nombre, tareas, modalidad) VALUES (?, ?, ?, ?)", 
                           (cuil, nombre, tareas, modalidad))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError: return False 

    def actualizar_nombre_empleado(self, id_emp, nuevo_nombre):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE empleados SET nombre = ? WHERE id = ?", (nuevo_nombre.strip(), id_emp))
            conn.commit()
            conn.close()
            return True
        except: return False

    def obtener_lista_empleados_completa(self):
        conn = self.conectar()
        cursor = conn.cursor()
        query = """
            SELECT 
                e.id, e.cuil, e.nombre, e.tareas, e.modalidad,
                IFNULL(SUM(m.monto_remunerativo), 0) as rem,
                IFNULL(SUM(m.hs_50), 0) as h50,
                IFNULL(SUM(m.hs_100), 0) as h100
            FROM empleados e
            LEFT JOIN movimientos m ON e.id = m.id_empleado
            GROUP BY e.id
            ORDER BY e.nombre
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        conn.close()
        
        resultado = []
        for f in filas:
            id_e, cuil, nom, tar, mod, rem, h50, h100 = f
            val_h = rem / 160 if rem > 0 else 0
            d50 = val_h * h50 * 1.5
            d100 = val_h * h100 * 2.0
            # Formato: ID, CUIL, Nombre, Tareas, Mod, Rem, ValH, Hs50, $50, Hs100, $100, TotHs, TOTAL DINERO
            resultado.append((id_e, cuil, nom, tar, mod, rem, val_h, h50, d50, h100, d100, h50+h100, d50+d100))
        return resultado

    def agregar_movimiento(self, id_emp, fecha, concepto, monto, h50, h100):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movimientos (id_empleado, fecha, concepto, monto_remunerativo, hs_50, hs_100) VALUES (?, ?, ?, ?, ?, ?)", 
                       (id_emp, fecha, concepto, monto, h50, h100))
        conn.commit()
        conn.close()

    def obtener_movimientos(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos WHERE id_empleado = ? ORDER BY id DESC", (id_emp,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def borrar_movimiento(self, id_mov):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimientos WHERE id = ?", (id_mov,))
        conn.commit()
        conn.close()

    def borrar_empleado(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimientos WHERE id_empleado = ?", (id_emp,))
        cursor.execute("DELETE FROM empleados WHERE id = ?", (id_emp,))
        conn.commit()
        conn.close()
        
    def obtener_resumen_empleado(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(monto_remunerativo), SUM(hs_50), SUM(hs_100) FROM movimientos WHERE id_empleado = ?", (id_emp,))
        res = cursor.fetchone()
        conn.close()
        return (res[0] or 0.0, res[1] or 0.0, res[2] or 0.0)
    
    def importar_empleados_json(self, lista_empleados):
        conn = self.conectar()
        cursor = conn.cursor()
        contador = 0
        for emp in lista_empleados:
            if emp.get("A") == "AGENTE CUIL": continue
            try:
                cuil = str(emp.get("A", "")).strip()
                # Reparación de codificación automática
                raw_n = str(emp.get("B", "")).strip()
                try: nombre = raw_n.encode('latin-1').decode('utf-8')
                except: nombre = raw_n
                mod = str(emp.get("C", "")).strip()
                if nombre:
                    cursor.execute("INSERT INTO empleados (cuil, nombre, tareas, modalidad) VALUES (?, ?, ?, ?)", 
                                   (cuil, nombre, "-", mod))
                    contador += 1
            except: pass
        conn.commit()
        conn.close()
        return contador

    def vaciar_movimientos_empleado(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimientos WHERE id_empleado = ?", (id_emp,))
        conn.commit()
        conn.close()

    def importar_movimientos_masivos(self, id_emp, lista_movimientos):
        """Inserta una lista de movimientos (horas) en un empleado específico."""
        conn = self.conectar()
        cursor = conn.cursor()
        contador = 0
        for mov in lista_movimientos:
            try:
                # Solo importamos concepto y horas. El remunerativo lo pone tu viejo.
                concepto = mov.get("concepto", "Carga Externa")
                h50 = float(mov.get("h50", 0))
                h100 = float(mov.get("h100", 0))
                # El monto remunerativo va en 0 porque eso lo controla el administrador
                cursor.execute("""
                    INSERT INTO movimientos (id_empleado, fecha, concepto, monto_remunerativo, hs_50, hs_100)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_emp, "", concepto, 0.0, h50, h100))
                contador += 1
            except: pass
        conn.commit()
        conn.close()
        return contador