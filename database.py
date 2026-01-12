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
            cursor.execute("""
                INSERT INTO empleados (cuil, nombre, tareas, modalidad) 
                VALUES (?, ?, ?, ?)
            """, (cuil, nombre, tareas, modalidad))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False 

    # --- NUEVA FUNCIÓN DE BORRADO ---
    def borrar_empleado(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        
        # 1. Primero borramos sus movimientos (historial)
        cursor.execute("DELETE FROM movimientos WHERE id_empleado = ?", (id_emp,))
        
        # 2. Luego borramos al empleado
        cursor.execute("DELETE FROM empleados WHERE id = ?", (id_emp,))
        
        conn.commit()
        conn.close()

    def obtener_lista_empleados_completa(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empleados ORDER BY nombre")
        empleados = cursor.fetchall()
        conn.close()
        
        datos_procesados = []
        
        for emp in empleados:
            id_emp = emp[0]
            rem, h50, h100 = self.obtener_resumen_empleado(id_emp)
            
            valor_hora = rem / 160 if rem > 0 else 0
            dinero_50 = valor_hora * h50 * 1.5
            dinero_100 = valor_hora * h100 * 2.0
            total_horas_cantidad = h50 + h100

            fila = (
                id_emp, emp[1], emp[2], emp[3], emp[4], 
                rem, valor_hora, 
                h50, dinero_50, 
                h100, dinero_100, 
                total_horas_cantidad
            )
            datos_procesados.append(fila)
            
        return datos_procesados

    def agregar_movimiento(self, id_emp, fecha, concepto, monto, h50, h100):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movimientos (id_empleado, fecha, concepto, monto_remunerativo, hs_50, hs_100)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_emp, fecha, concepto, monto, h50, h100))
        conn.commit()
        conn.close()

    def obtener_movimientos(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos WHERE id_empleado = ? ORDER BY id DESC", (id_emp,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def borrar_movimiento(self, id_movimiento):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimientos WHERE id = ?", (id_movimiento,))
        conn.commit()
        conn.close()
        
    def obtener_resumen_empleado(self, id_emp):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUM(monto_remunerativo), 
                SUM(hs_50), 
                SUM(hs_100) 
            FROM movimientos WHERE id_empleado = ?
        """, (id_emp,))
        res = cursor.fetchone()
        conn.close()
        return (res[0] or 0.0, res[1] or 0.0, res[2] or 0.0)
    
    def importar_empleados_json(self, lista_empleados):
        conn = self.conectar()
        cursor = conn.cursor()
        contador_exitos = 0
        
        for i, emp in enumerate(lista_empleados):
            if emp.get("A") == "AGENTE CUIL":
                continue
                
            try:
                cuil = str(emp.get("A", "")).strip() 
                nombre = str(emp.get("B", "")).strip()
                modalidad = str(emp.get("C", "")).strip()
                tareas = "-" 
                
                if nombre: 
                    cursor.execute("""
                        INSERT INTO empleados (cuil, nombre, tareas, modalidad) 
                        VALUES (?, ?, ?, ?)
                    """, (cuil, nombre, tareas, modalidad))
                    contador_exitos += 1
                    
            except sqlite3.IntegrityError:
                pass
            except Exception as e:
                print(f"Error en fila {i}: {e}")
                
        conn.commit()
        conn.close()
        return contador_exitos