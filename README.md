# Sistema de Gestión de Jornales y Horas Extras - Vialidad Nacional


Aplicación de escritorio desarrollada para digitalizar y automatizar el proceso de liquidación de horas extras y jornales en el área administrativa de **Vialidad Nacional**. Este sistema reemplaza el uso de planillas de cálculo manuales, centralizando la información y reduciendo errores humanos en la nómina.

## 📋 Características Principales

* **Gestión de Personal:** Alta de empleados con datos específicos (CUIL, Tareas, Modalidad de Contrato).
* **Cálculo Dinámico de Valor Hora:** Determinación automática del valor hora basada en la sumatoria de ítems remunerativos mensuales dividido por el coeficiente normativo .
* **Liquidación de Horas Extras:** Carga y cálculo automático de horas al 50% y al 100%.
* **Validación Normativa:** Sistema de control que impide la carga de horas que excedan el límite mensual permitido (30 horas por agente).
* **Base de Datos Histórica:** Persistencia de datos mediante SQLite, permitiendo revisar liquidaciones anteriores sin perder información al modificar valores actuales.
* **Reportes Automatizados:** Exportación de planillas mensuales a formato CSV/Excel con codificación compatible, listas para su presentación administrativa.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica (GUI):** Tkinter (Librería nativa)
* **Base de Datos:** SQLite3 (Relacional, serverless)
* **Manejo de Archivos:** CSV / OS modules


### Panel Principal (Dashboard)
*Vista general de la nómina con cálculos en tiempo real.*

*Interfaz de carga de novedades con alertas de límite de horas.*

## 🚀 Instalación y Ejecución

Este sistema no requiere dependencias externas pesadas ni instalación de servidores, ya que utiliza la librería estándar de Python.

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/sistema-jornales-vialidad.git](https://github.com/TU_USUARIO/sistema-jornales-vialidad.git)
    ```

2.  **Acceder a la carpeta:**
    ```bash
    cd sistema-jornales-vialidad
    ```

3.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```

*Nota: Al iniciar por primera vez, el sistema creará automáticamente la base de datos `sistema_jornales.db`.*

## 📖 Guía de Uso Rápida

1.  **Crear Empleado:** Utilice el botón "+ CREAR EMPLEADO" para dar de alta un agente con su CUIL y Modalidad.
2.  **Cargar Novedades:** Haga doble clic sobre un empleado en la lista.
3.  **Ingresar Ítems:**
    * Para definir el valor hora, cargue conceptos monetarios (ej: "Sueldo Básico", "Antigüedad").
    * Cargue la cantidad de horas trabajadas al 50% o 100%.
    * *El sistema bloqueará la carga si la suma de horas supera las 30 hs.*
4.  **Exportar:** Al finalizar el mes, presione "EXPORTAR EXCEL" para generar el reporte `Planilla_Horas_Octubre.csv`.

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos y profesionales para optimización de procesos internos.

---
**Desarrollado por Facundo Gabriel Salas**
