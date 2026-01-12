import tkinter as tk
from tkinter import ttk, messagebox, filedialog 
import csv
import os
import json 
from database import DataBase

# Inicializamos DB
db = DataBase()

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Jornales")
        self.state('zoomed') 
        
        # --- PANEL SUPERIOR ---
        frame_top = tk.Frame(self, pady=10, padx=10, bg="#e1e1e1")
        frame_top.pack(fill="x")
        
        # Botones Izquierda
        tk.Button(frame_top, text="+ CREAR EMPLEADO", command=self.modal_nuevo_empleado, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left")
        
        # Botón Eliminar
        tk.Button(frame_top, text="ELIMINAR SELECCIONADO", command=self.eliminar_empleado, bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        tk.Button(frame_top, text="ACTUALIZAR TABLA", command=self.cargar_tabla_principal, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(frame_top, text="IMPORTAR JSON", command=self.importar_desde_json, bg="#9C27B0", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # Botón Derecha (Exportar)
        tk.Button(frame_top, text="EXPORTAR EXCEL", command=self.exportar_global, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="right")

        # --- TABLA PRINCIPAL ---
        cols = ("ID", "CUIL", "Nombre", "Tareas", "Modalidad", "Remunerativo", "Valor Hora", "Hs 50%", "$ 50%", "Hs 100%", "$ 100%", "Total Hs")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        # Configuración de columnas
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=30, anchor="center")
        self.tree.heading("CUIL", text="CUIL")
        self.tree.column("CUIL", width=90, anchor="center")
        self.tree.heading("Nombre", text="APELLIDO Y NOMBRE")
        self.tree.column("Nombre", width=180)
        self.tree.heading("Tareas", text="TAREAS")
        self.tree.column("Tareas", width=80)
        self.tree.heading("Modalidad", text="MOD")
        self.tree.column("Modalidad", width=50, anchor="center")

        self.tree.heading("Remunerativo", text="TOT. REMUN.")
        self.tree.column("Remunerativo", width=90, anchor="e") 
        self.tree.heading("Valor Hora", text="VALOR HORA")
        self.tree.column("Valor Hora", width=80, anchor="e")
        
        self.tree.heading("Hs 50%", text="Hs 50")
        self.tree.column("Hs 50%", width=40, anchor="center")
        self.tree.heading("$ 50%", text="$ TOTAL 50%")
        self.tree.column("$ 50%", width=90, anchor="e")

        self.tree.heading("Hs 100%", text="Hs 100")
        self.tree.column("Hs 100%", width=40, anchor="center")
        self.tree.heading("$ 100%", text="$ TOTAL 100%")
        self.tree.column("$ 100%", width=90, anchor="e")
        
        self.tree.heading("Total Hs", text="TOTAL HS")
        self.tree.column("Total Hs", width=60, anchor="center") 
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", self.abrir_detalle_empleado)
        self.cargar_tabla_principal()

    def cargar_tabla_principal(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        datos = db.obtener_lista_empleados_completa()
        for d in datos:
            fmt_rem = f"$ {d[5]:,.2f}"
            fmt_val = f"$ {d[6]:,.2f}"
            fmt_d50 = f"$ {d[8]:,.2f}" 
            fmt_d100 = f"$ {d[10]:,.2f}"
            self.tree.insert("", "end", values=(d[0], d[1], d[2], d[3], d[4], fmt_rem, fmt_val, d[7], fmt_d50, d[9], fmt_d100, d[11]))

    def eliminar_empleado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un empleado.")
            return
        item = self.tree.item(seleccion)
        id_emp, nombre = item['values'][0], item['values'][2]
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {nombre}?"):
            db.borrar_empleado(id_emp)
            self.cargar_tabla_principal()

    def importar_desde_json(self):
        filename = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if not filename: return
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                datos = json.load(file)
            cantidad = db.importar_empleados_json(datos)
            self.cargar_tabla_principal()
            messagebox.showinfo("Éxito", f"Importados {cantidad} empleados.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def modal_nuevo_empleado(self):
        top = tk.Toplevel(self)
        top.title("Alta")
        top.geometry("300x350")
        tk.Label(top, text="CUIL:").pack()
        e_cuil = tk.Entry(top); e_cuil.pack()
        tk.Label(top, text="Nombre:").pack()
        e_nombre = tk.Entry(top, width=30); e_nombre.pack()
        tk.Label(top, text="Tareas:").pack()
        e_tareas = tk.Entry(top); e_tareas.pack()
        tk.Label(top, text="Modalidad:").pack()
        e_mod = ttk.Combobox(top, values=["C.T.I", "P.P", "MT"]); e_mod.pack()
        
        def guardar():
            if e_nombre.get():
                db.agregar_empleado(e_cuil.get(), e_nombre.get(), e_tareas.get(), e_mod.get())
                self.cargar_tabla_principal()
                top.destroy()
        tk.Button(top, text="GUARDAR", command=guardar, bg="green", fg="white").pack(pady=10)

    def abrir_detalle_empleado(self, event):
        item = self.tree.selection()
        if not item: return
        id_emp, nombre_emp = self.tree.item(item, "values")[0], self.tree.item(item, "values")[2]
        VentanaDetalle(self, id_emp, nombre_emp)

    # --- ESTA FUNCIÓN AHORA SÍ ESTÁ DENTRO DE LA CLASE ---
    def exportar_global(self):
        try:
            ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = filedialog.asksaveasfilename(
                initialdir=ruta_descargas,
                title="Guardar Planilla",
                defaultextension=".csv",
                filetypes=[("Excel CSV", "*.csv")],
                initialfile="Planilla_Horas_Octubre.csv"
            )
            if not filename: return

            with open(filename, "w", newline="", encoding='utf-8-sig') as f:
                f.write("sep=;\n") # Obliga a Excel a usar columnas
                writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["ID", "CUIL", "NOMBRE", "TAREAS", "MODALIDAD", "TOT. REMUNERATIVO", "VALOR HORA", "Hs 50%", "$ 50%", "Hs 100%", "$ 100%", "TOTAL HS", "TOTAL A PAGAR ($)"])
                
                datos = db.obtener_lista_empleados_completa()
                exportados = 0
                for d in datos:
                    if d[5] == 0 and d[11] == 0: continue # Salta vacíos
                    
                    fila = []
                    for item in d:
                        fila.append(f"{item:.2f}".replace('.', ',') if isinstance(item, float) else item)
                    
                    # Suma de dinero total ($50 + $100)
                    total_pagar = (d[8] + d[10])
                    fila.append(f"{total_pagar:.2f}".replace('.', ','))
                    
                    writer.writerow(fila)
                    exportados += 1
            
            messagebox.showinfo("Éxito", f"Exportados {exportados} agentes.")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", str(e))

class VentanaDetalle(tk.Toplevel):
    def __init__(self, parent, id_emp, nombre_emp):
        super().__init__(parent)
        self.parent, self.id_emp = parent, id_emp
        self.title(f"Detalle: {nombre_emp}")
        self.geometry("900x550")
        
        frame_form = tk.LabelFrame(self, text=" Carga de Ítems ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=5)
        self.entry_conc = tk.Entry(frame_form, width=30); self.entry_conc.grid(row=1, column=0, padx=5)
        self.entry_monto = tk.Entry(frame_form, width=15); self.entry_monto.grid(row=1, column=1, padx=5)
        self.entry_h50 = tk.Entry(frame_form, width=10); self.entry_h50.grid(row=1, column=2, padx=5)
        self.entry_h100 = tk.Entry(frame_form, width=10); self.entry_h100.grid(row=1, column=3, padx=5)
        tk.Button(frame_form, text="AGREGAR", command=self.agregar, bg="blue", fg="white").grid(row=1, column=4, padx=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Concepto", "Monto", "H50", "H100"), show="headings")
        self.tree.heading("Concepto", text="Concepto"); self.tree.heading("Monto", text="$ Remun")
        self.tree.heading("H50", text="Hs 50%"); self.tree.heading("H100", text="Hs 100%")
        self.tree.pack(fill="both", expand=True, padx=10)
        
        tk.Button(self, text="BORRAR", command=self.borrar, bg="red", fg="white").pack(pady=5)
        self.lbl_info = tk.Label(self, text="", font=("Arial", 10, "bold"), bg="#333", fg="white", pady=5)
        self.lbl_info.pack(fill="x")
        
        self.cargar_datos()
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def cerrar(self):
        self.parent.cargar_tabla_principal()
        self.destroy()

    def agregar(self):
        try:
            m, h5, h1 = float(self.entry_monto.get() or 0), float(self.entry_h50.get() or 0), float(self.entry_h100.get() or 0)
            _, ex5, ex1 = db.obtener_resumen_empleado(self.id_emp)
            if (ex5 + ex1 + h5 + h1) > 30:
                messagebox.showwarning("Límite", "Supera las 30hs.")
                return
            db.agregar_movimiento(self.id_emp, "", self.entry_conc.get() or "-", m, h5, h1)
            self.cargar_datos()
        except: messagebox.showerror("Error", "Datos inválidos")

    def borrar(self):
        sel = self.tree.selection()
        if sel:
            db.borrar_movimiento(self.tree.item(sel, "values")[0])
            self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for m in db.obtener_movimientos(self.id_emp):
            self.tree.insert("", "end", values=(m[0], m[3], f"$ {m[4]}", m[5], m[6]))
        rem, h5, h1 = db.obtener_resumen_empleado(self.id_emp)
        vh = rem / 160 if rem > 0 else 0
        self.lbl_info.config(text=f"REMUNERATIVO: $ {rem:,.2f} | VALOR HORA: $ {vh:,.2f} | HS: {h5+h1}/30")

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()