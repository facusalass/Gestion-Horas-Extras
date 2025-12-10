import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
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
        
        tk.Button(frame_top, text="+ CREAR EMPLEADO", command=self.modal_nuevo_empleado, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left")
        tk.Button(frame_top, text="ACTUALIZAR TABLA", command=self.cargar_tabla_principal, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        tk.Button(frame_top, text="EXPORTAR EXCEL", command=self.exportar_global, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="right")

        # --- TABLA PRINCIPAL ---
        # AÑADIMOS LAS COLUMNAS DE DINERO ($)
        cols = ("ID", "CUIL", "Nombre", "Tareas", "Modalidad", "Remunerativo", "Valor Hora", "Hs 50%", "$ 50%", "Hs 100%", "$ 100%", "Total Hs", "A PAGAR")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        # Configuración
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
        
        # COLUMNAS 50%
        self.tree.heading("Hs 50%", text="Hs 50")
        self.tree.column("Hs 50%", width=40, anchor="center")
        self.tree.heading("$ 50%", text="$ TOTAL 50%")
        self.tree.column("$ 50%", width=80, anchor="e")

        # COLUMNAS 100%
        self.tree.heading("Hs 100%", text="Hs 100")
        self.tree.column("Hs 100%", width=40, anchor="center")
        self.tree.heading("$ 100%", text="$ TOTAL 100%")
        self.tree.column("$ 100%", width=80, anchor="e")
        
        # TOTALES FINALES
        self.tree.heading("Total Hs", text="TOT HS")
        self.tree.column("Total Hs", width=50, anchor="center")
        
        self.tree.heading("A PAGAR", text="TOTAL A PAGAR")
        self.tree.column("A PAGAR", width=110, anchor="e")
        
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
            fmt_din_50 = f"$ {d[8]:,.2f}"
            fmt_din_100 = f"$ {d[10]:,.2f}"
            fmt_final = f"$ {d[12]:,.2f}"
            
            self.tree.insert("", "end", values=(
                d[0], d[1], d[2], d[3], d[4], 
                fmt_rem, fmt_val, 
                d[7], fmt_din_50, 
                d[9], fmt_din_100, 
                d[11], fmt_final
            ))

    def modal_nuevo_empleado(self):
        top = tk.Toplevel(self)
        top.title("Alta de Empleado")
        top.geometry("400x350")
        
        tk.Label(top, text="CUIL:").pack(pady=5)
        e_cuil = tk.Entry(top)
        e_cuil.pack()
        tk.Label(top, text="Apellido y Nombre:").pack(pady=5)
        e_nombre = tk.Entry(top, width=40)
        e_nombre.pack()
        tk.Label(top, text="Tareas:").pack(pady=5)
        e_tareas = tk.Entry(top)
        e_tareas.pack()
        tk.Label(top, text="Modalidad Contrato:").pack(pady=5)
        values_mod = ["C.T.I", "P.P", "MT", "OTRO"]
        e_mod = ttk.Combobox(top, values=values_mod)
        e_mod.pack()
        
        def guardar():
            if e_nombre.get():
                exito = db.agregar_empleado(e_cuil.get(), e_nombre.get(), e_tareas.get(), e_mod.get())
                if exito:
                    self.cargar_tabla_principal()
                    top.destroy()
                else:
                    messagebox.showerror("Error", "El empleado ya existe.")
        
        tk.Button(top, text="GUARDAR", command=guardar, bg="#4CAF50", fg="white", pady=5).pack(pady=20)

    def abrir_detalle_empleado(self, event):
        item = self.tree.selection()
        if not item: return
        id_emp = self.tree.item(item, "values")[0]
        nombre_emp = self.tree.item(item, "values")[2]
        VentanaDetalle(self, id_emp, nombre_emp)

    def exportar_global(self):
        try:
            filename = "Planilla_Sueldos_Completa.csv"
            
            with open(filename, "w", newline="", encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "CUIL", "APELLIDO Y NOMBRE", "TAREAS", "MODALIDAD", 
                    "TOT. REMUNERATIVO", "VALOR HORA", 
                    "HS 50%", "$ TOTAL 50%", 
                    "HS 100%", "$ TOTAL 100%", 
                    "TOTAL HS", "TOTAL A PAGAR"
                ])
                
                datos = db.obtener_lista_empleados_completa()
                for d in datos:
                    fila_formateada = []
                    for item in d:
                        if isinstance(item, float):
                            str_num = f"{item:.2f}".replace('.', ',')
                            fila_formateada.append(str_num)
                        else:
                            fila_formateada.append(item)
                    writer.writerow(fila_formateada)
                    
            messagebox.showinfo("Exportado", f"Se generó '{filename}'. Se abrirá automáticamente.")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", str(e))


class VentanaDetalle(tk.Toplevel):
    def __init__(self, parent, id_emp, nombre_emp):
        super().__init__(parent)
        self.parent = parent
        self.id_emp = id_emp
        self.title(f"Detalle de: {nombre_emp}")
        self.geometry("950x600")
        
        frame_form = tk.LabelFrame(self, text=" Carga de Ítems ", padx=10, pady=10, bg="#f9f9f9")
        frame_form.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_form, text="Concepto:", bg="#f9f9f9").grid(row=0, column=0, sticky="w")
        self.entry_conc = tk.Entry(frame_form, width=30)
        self.entry_conc.grid(row=1, column=0, padx=5, pady=5)
        
        tk.Label(frame_form, text="$ Monto Remunerativo:", bg="#f9f9f9", fg="blue").grid(row=0, column=1, sticky="w")
        self.entry_monto = tk.Entry(frame_form, width=15)
        self.entry_monto.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_form, text="Hs 50%:", bg="#f9f9f9").grid(row=0, column=2, sticky="w")
        self.entry_h50 = tk.Entry(frame_form, width=10)
        self.entry_h50.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(frame_form, text="Hs 100%:", bg="#f9f9f9").grid(row=0, column=3, sticky="w")
        self.entry_h100 = tk.Entry(frame_form, width=10)
        self.entry_h100.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Button(frame_form, text="AGREGAR ÍTEM", command=self.agregar, bg="#4CAF50", fg="white", font=("bold")).grid(row=1, column=4, padx=15)

        tk.Label(frame_form, text="* Máximo 30 horas totales permitidas por empleado.", bg="#f9f9f9", fg="red").grid(row=2, column=0, columnspan=4, sticky="w")

        # --- TABLA DETALLE ---
        self.tree = ttk.Treeview(self, columns=("ID", "Concepto", "Monto", "H50", "H100"), show="headings")
        self.tree.heading("Concepto", text="Concepto Detalle")
        self.tree.heading("Monto", text="$ Remunerativo")
        self.tree.heading("H50", text="Hs 50%")
        self.tree.heading("H100", text="Hs 100%")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(self, text="BORRAR ÍTEM SELECCIONADO", command=self.borrar, bg="#FF5722", fg="white").pack(pady=5)
        
        # --- TOTALES ---
        frame_totales = tk.Frame(self, bg="#333", pady=10)
        frame_totales.pack(fill="x")
        
        self.lbl_rem = tk.Label(frame_totales, text="REMUNERATIVO: $ 0", fg="#4CAF50", bg="#333", font=("Arial", 11, "bold"))
        self.lbl_rem.pack(side="left", padx=20)
        
        self.lbl_hs = tk.Label(frame_totales, text="Hs Totales: 0/30", fg="white", bg="#333", font=("Arial", 12, "bold"))
        self.lbl_hs.pack(side="left", padx=20)
        
        self.lbl_extra = tk.Label(frame_totales, text="A PAGAR: $ 0", fg="#2196F3", bg="#333", font=("Arial", 14, "bold"))
        self.lbl_extra.pack(side="right", padx=20)
        
        self.cargar_datos()
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def cerrar(self):
        self.parent.cargar_tabla_principal()
        self.destroy()

    def agregar(self):
        try:
            m = float(self.entry_monto.get() or 0)
            h5_nuevas = float(self.entry_h50.get() or 0)
            h1_nuevas = float(self.entry_h100.get() or 0)
            c = self.entry_conc.get() or "-"
          
            _, h5_actuales, h1_actuales = db.obtener_resumen_empleado(self.id_emp)
            
            total_actual = h5_actuales + h1_actuales
            total_nuevas = h5_nuevas + h1_nuevas
            
            if (total_actual + total_nuevas) > 30:
                messagebox.showwarning("Límite Excedido", f"¡Cuidado! El empleado ya tiene {total_actual} hs.\nSi agregas {total_nuevas} hs, superará el límite de 30 hs.")
                return # Detenemos la función, no guarda nada
            
            # Si pasa la validación, guardamos
            db.agregar_movimiento(self.id_emp, "", c, m, h5_nuevas, h1_nuevas)
            
            self.entry_monto.delete(0, tk.END)
            self.entry_h50.delete(0, tk.END)
            self.entry_h100.delete(0, tk.END)
            self.entry_conc.delete(0, tk.END)
            self.entry_conc.focus()
            
            self.cargar_datos()
            
        except ValueError:
            messagebox.showerror("Error", "Números inválidos")

    def borrar(self):
        sel = self.tree.selection()
        if sel:
            id_mov = self.tree.item(sel, "values")[0]
            db.borrar_movimiento(id_mov)
            self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        movs = db.obtener_movimientos(self.id_emp)
        for m in movs:
            self.tree.insert("", "end", values=(m[0], m[3], f"$ {m[4]}", m[5], m[6]))
            
        rem, h50, h100 = db.obtener_resumen_empleado(self.id_emp)
        v_hora = rem / 160 if rem > 0 else 0
        
        # Dinero separado
        d50 = v_hora * h50 * 1.5
        d100 = v_hora * h100 * 2.0
        total_extras = d50 + d100
        total_hs = h50 + h100
        
        self.lbl_rem.config(text=f"REMUNERATIVO: $ {rem:,.2f}")
        
        # Color rojo si está cerca del límite
        color_hs = "red" if total_hs >= 30 else "white"
        self.lbl_hs.config(text=f"Hs Totales: {total_hs}/30", fg=color_hs)
        
        self.lbl_extra.config(text=f"A PAGAR: $ {total_extras:,.2f}")

if __name__ == "__main__":
    try:
        print("Iniciando aplicación...")
        app = Aplicacion()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar: {e}")
        input("Presiona Enter para cerrar...")