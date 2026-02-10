import tkinter as tk
from tkinter import ttk, messagebox, filedialog 
import csv, os, json 
from database import DataBase

db = DataBase()

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Jornales - Vialidad Nacional")
        self.state('zoomed') 
        
        frame_top = tk.Frame(self, pady=10, padx=10, bg="#e1e1e1")
        frame_top.pack(fill="x")
        
        tk.Button(frame_top, text="+ CREAR", command=self.modal_nuevo_empleado, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(frame_top, text="EDITAR NOMBRE", command=self.modal_editar_nombre, bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Button(frame_top, text="ELIMINAR", command=self.eliminar_empleado, bg="#F44336", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(frame_top, text="ACTUALIZAR", command=self.cargar_tabla_principal, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Button(frame_top, text="IMPORTAR JSON", command=self.importar_desde_json, bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Button(frame_top, text="EXPORTAR EXCEL", command=self.exportar_global, bg="#2d2d2d", fg="white", font=("Arial", 9, "bold")).pack(side="right")

        # COLUMNAS INCLUYENDO TOTAL A PAGAR
        cols = ("ID", "CUIL", "Nombre", "Tareas", "Mod", "Remunerativo", "Val Hora", "Hs 50", "$ 50", "Hs 100", "$ 100", "Tot Hs", "TOTAL A PAGAR")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=85, anchor="center")
        
        self.tree.column("Nombre", width=230, anchor="w")
        self.tree.column("TOTAL A PAGAR", width=120, anchor="e") # Destacado a la derecha
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", self.abrir_detalle_empleado)
        self.cargar_tabla_principal()

    def cargar_tabla_principal(self):
        self.tree.delete(*self.tree.get_children())
        datos = db.obtener_lista_empleados_completa()
        for d in datos:
            # d: ID, CUIL, Nom, Tar, Mod, Rem, ValH, H50, $50, H100, $100, TotHs, TotPagar
            fmt = (d[0], d[1], d[2], d[3], d[4], f"$ {d[5]:,.2f}", f"$ {d[6]:,.2f}", 
                   d[7], f"$ {d[8]:,.2f}", d[9], f"$ {d[10]:,.2f}", d[11], f"$ {d[12]:,.2f}")
            self.tree.insert("", "end", values=fmt)

    def modal_editar_nombre(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel)['values']
        top = tk.Toplevel(self); top.title("Editar Nombre"); top.geometry("400x150")
        tk.Label(top, text="Nuevo nombre:").pack(pady=5)
        ent = tk.Entry(top, width=40); ent.pack(); ent.insert(0, item[2]); ent.focus()
        def conf():
            if ent.get(): db.actualizar_nombre_empleado(item[0], ent.get()); self.cargar_tabla_principal(); top.destroy()
        tk.Button(top, text="GUARDAR", command=conf, bg="green", fg="white").pack(pady=10)

    def importar_desde_json(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'r', encoding='utf-8-sig') as file:
                cant = db.importar_empleados_json(json.load(file))
            self.cargar_tabla_principal(); messagebox.showinfo("Éxito", f"Importados {cant} agentes.")

    def modal_nuevo_empleado(self):
        top = tk.Toplevel(self); top.title("Alta"); top.geometry("300x400")
        tk.Label(top, text="Nombre:").pack(); e_n = tk.Entry(top, width=30); e_n.pack()
        tk.Label(top, text="CUIL:").pack(); e_c = tk.Entry(top); e_c.pack()
        def guardar():
            if e_n.get(): db.agregar_empleado(e_c.get(), e_n.get(), "-", ""); self.cargar_tabla_principal(); top.destroy()
        tk.Button(top, text="GUARDAR", command=guardar, bg="green", fg="white").pack(pady=20)

    def eliminar_empleado(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel)['values']
            if messagebox.askyesno("Confirmar", f"¿Eliminar a {item[2]}?"):
                db.borrar_empleado(item[0]); self.cargar_tabla_principal()

    def abrir_detalle_empleado(self, event):
        sel = self.tree.selection()
        if sel: VentanaDetalle(self, self.tree.item(sel, "values")[0], self.tree.item(sel, "values")[2])

    def exportar_global(self):
        try:
            ruta = os.path.join(os.path.expanduser("~"), "Downloads")
            f_path = filedialog.asksaveasfilename(initialdir=ruta, title="Guardar Excel", defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="Planilla_Vialidad.csv")
            if not f_path: return
            with open(f_path, "w", newline="", encoding='utf-8-sig') as f:
                f.write("sep=;\n")
                w = csv.writer(f, delimiter=";")
                w.writerow(["ID", "CUIL", "NOMBRE", "TAREAS", "MOD", "TOT REMUN", "VAL HORA", "Hs 50", "$ 50", "Hs 100", "$ 100", "TOT HS", "TOTAL A PAGAR ($)"])
                for d in db.obtener_lista_empleados_completa():
                    if d[5] == 0 and d[11] == 0: continue
                    w.writerow([f"{x:.2f}".replace('.', ',') if isinstance(x, float) else x for x in d])
            messagebox.showinfo("Éxito", "Excel generado."); os.startfile(f_path)
        except: messagebox.showerror("Error", "No se pudo exportar.")

class VentanaDetalle(tk.Toplevel):
    def __init__(self, parent, id_emp, nombre_emp):
        super().__init__(parent)
        self.parent, self.id_emp, self.nombre_emp = parent, id_emp, nombre_emp
        self.title(f"Planilla: {nombre_emp}"); self.geometry("1000x650")
        
        # --- FORMULARIO DE CARGA ---
        frame_form = tk.LabelFrame(self, text=" Carga de Ítems ", padx=10, pady=10)
        frame_form.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_form, text="Concepto").grid(row=0, column=0)
        tk.Label(frame_form, text="Monto Remun.").grid(row=0, column=1)
        tk.Label(frame_form, text="Hs 50%").grid(row=0, column=2)
        tk.Label(frame_form, text="Hs 100%").grid(row=0, column=3)

        self.e_conc = tk.Entry(frame_form, width=30); self.e_conc.grid(row=1, column=0, padx=5)
        self.e_monto = tk.Entry(frame_form, width=15); self.e_monto.grid(row=1, column=1, padx=5)
        self.e_h50 = tk.Entry(frame_form, width=10); self.e_h50.grid(row=1, column=2, padx=5)
        self.e_h100 = tk.Entry(frame_form, width=10); self.e_h100.grid(row=1, column=3, padx=5)
        tk.Button(frame_form, text="AGREGAR", command=self.agregar, bg="blue", fg="white", font="bold").grid(row=1, column=4, padx=10)

        # --- TABLA DE MOVIMIENTOS ---
        self.tree = ttk.Treeview(self, columns=("ID", "Concepto", "Monto", "H50", "H100"), show="headings")
        for c in ["Concepto", "Monto", "H50", "H100"]: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # --- PANEL DE EXPORTACIÓN / COMPARTIR ---
        frame_share = tk.LabelFrame(self, text=" Exportar y Compartir Datos ", padx=10, pady=10)
        frame_share.pack(fill="x", padx=10, pady=5)

        tk.Button(frame_share, text="📤 EXPORTAR JSON (Para Enviar)", command=self.exportar_mis_horas, bg="#4CAF50", fg="white").pack(side="left", padx=10)
        tk.Button(frame_share, text="📥 IMPORTAR JSON", command=self.importar_horas_archivo, bg="#2196F3", fg="white").pack(side="left", padx=10)
        
        # EL NUEVO BOTÓN DE EXCEL INTERNO
        tk.Button(frame_share, text="📊 EXPORTAR DETALLE EXCEL", command=self.exportar_detalle_excel, bg="#607D8B", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=10)
        
        # Botones de borrado
        btn_f = tk.Frame(self); btn_f.pack(pady=5)
        tk.Button(btn_f, text="BORRAR SELECCIONADO", command=self.borrar, bg="red", fg="white").pack(side="left", padx=5)
        tk.Button(btn_f, text="VACIAR PLANILLA", command=self.vaciar, bg="orange").pack(side="left", padx=5)
        
        self.lbl_info = tk.Label(self, text="", font=("Arial", 11, "bold"), bg="#333", fg="white", pady=10); self.lbl_info.pack(fill="x")
        self.cargar_datos(); self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def cerrar(self): self.parent.cargar_tabla_principal(); self.destroy()

    # --- FUNCIÓN NUEVA: EXPORTAR DETALLE INDIVIDUAL A EXCEL ---
    def exportar_detalle_excel(self):
        try:
            movs = db.obtener_movimientos(self.id_emp)
            if not movs:
                messagebox.showwarning("Sin datos", "No hay movimientos para exportar.")
                return

            ruta = os.path.join(os.path.expanduser("~"), "Downloads")
            f_path = filedialog.asksaveasfilename(
                initialdir=ruta, 
                defaultextension=".csv", 
                filetypes=[("Excel CSV", "*.csv")], 
                initialfile=f"Detalle_{self.nombre_emp.replace(' ', '_')}.csv"
            )
            
            if not f_path: return

            with open(f_path, "w", newline="", encoding='utf-8-sig') as f:
                f.write("sep=;\n")
                w = csv.writer(f, delimiter=";")
                
                # Encabezado del reporte
                w.writerow([f"REPORTE DETALLADO DE: {self.nombre_emp}"])
                w.writerow([]) # Fila vacía
                w.writerow(["ID MOV.", "CONCEPTO / DETALLE", "MONTO REMUNERATIVO ($)", "HS AL 50%", "HS AL 100%"])
                
                for m in movs:
                    # m trae: (id, id_emp, fecha, concepto, monto, h50, h100)
                    fila = [
                        m[0], 
                        m[3], 
                        f"{m[4]:.2f}".replace('.', ','), 
                        f"{m[5]:.2f}".replace('.', ','), 
                        f"{m[6]:.2f}".replace('.', ',')
                    ]
                    w.writerow(fila)
                
                # Totales al final del Excel
                rem, h5, h1 = db.obtener_resumen_empleado(self.id_emp)
                w.writerow([])
                w.writerow(["", "TOTALES ACUMULADOS:", f"{rem:,.2f}".replace('.', ','), f"{h5:.2f}".replace('.', ','), f"{h1:.2f}".replace('.', ',')])
                w.writerow(["", "TOTAL HORAS:", "", "", f"{(h5+h1):.2f}".replace('.', ',')])

            messagebox.showinfo("Éxito", "Detalle exportado correctamente."); os.startfile(f_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def exportar_mis_horas(self):
        movs = db.obtener_movimientos(self.id_emp)
        if not movs: return
        datos = [{"concepto": m[3], "h50": m[5], "h100": m[6]} for m in movs]
        f_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=f"Horas_{self.nombre_emp.replace(' ', '_')}.json")
        if f_path:
            with open(f_path, 'w', encoding='utf-8') as f: json.dump(datos, f, indent=4)
            messagebox.showinfo("Éxito", "Archivo JSON generado.")

    def importar_horas_archivo(self):
        f_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if f_path:
            try:
                with open(f_path, 'r', encoding='utf-8') as f: lista = json.load(f)
                db.importar_movimientos_masivos(self.id_emp, lista)
                self.cargar_datos(); messagebox.showinfo("Éxito", "Horas importadas.")
            except: messagebox.showerror("Error", "Archivo no válido.")

    def vaciar(self):
        if messagebox.askyesno("Confirmar", "¿Vaciar planilla?"): db.vaciar_movimientos_empleado(self.id_emp); self.cargar_datos()

    def agregar(self):
        try:
            m, h5, h1 = float(self.e_monto.get() or 0), float(self.e_h50.get() or 0), float(self.e_h100.get() or 0)
            _, ex5, ex1 = db.obtener_resumen_empleado(self.id_emp)
            if (ex5 + ex1 + h5 + h1) > 30: messagebox.showwarning("Aviso", "Supera 30hs."); return
            db.agregar_movimiento(self.id_emp, "", self.e_conc.get() or "-", m, h5, h1)
            for e in [self.e_conc, self.e_monto, self.e_h50, self.e_h100]: e.delete(0, 'end')
            self.cargar_datos()
        except: messagebox.showerror("Error", "Datos inválidos")

    def borrar(self):
        sel = self.tree.selection()
        if sel: db.borrar_movimiento(self.tree.item(sel, "values")[0]); self.cargar_datos()

    def cargar_datos(self):
        self.tree.delete(*self.tree.get_children())
        for m in db.obtener_movimientos(self.id_emp):
            self.tree.insert("", "end", values=(m[0], m[3], f"$ {m[4]:,.2f}", m[5], m[6]))
        rem, h5, h1 = db.obtener_resumen_empleado(self.id_emp)
        vh = rem / 160 if rem > 0 else 0
        self.lbl_info.config(text=f"REMUNERATIVO: $ {rem:,.2f} | VALOR HORA: $ {vh:,.2f} | TOTAL: {h5+h1}/30 HS")
if __name__ == "__main__":
    app = Aplicacion(); app.mainloop()