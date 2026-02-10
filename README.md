# Sistema de Gestión de Jornales y Horas Extras (Vialidad Nacional)

Este proyecto nace de una necesidad real: optimizar y descentralizar la carga de horas extras en un entorno administrativo estatal (**Vialidad Nacional**). El software permite migrar de una gestión manual en papeles o planillas dispersas a un sistema robusto, validado y con reportes profesionales.

> **Impacto del proyecto:** Reducción del error humano en cálculos remunerativos y descentralización de la carga mediante módulos de importación/exportación offline.

---

## 🚀 Características Principales

* **Gestión Integral de Agentes (CRUD):** Alta, baja y edición de empleados con validación de CUIL único.
* **Cálculo Automático de Haberes:** El sistema toma los montos remunerativos, calcula el **Valor Hora** (base 160hs) y determina automáticamente el pago de horas al 50% y 100%.
* **Validación de Reglas de Negocio:** Bloqueo automático de cargas que superen el límite legal de **30 horas mensuales** por agente.
* **Módulo de Carga Descentralizada:** Los empleados pueden cargar sus propias horas y exportarlas en formato JSON para que el administrador las importe masivamente, evitando cuellos de botella.
* **Reportes Profesionales en Excel:** Generación de planillas CSV compatibles con Excel, con formato limpio, separadores automáticos y cálculos de totales a pagar.

---

## 🛠️ Desafíos Técnicos Resueltos

Durante el desarrollo, se abordaron problemas críticos de ingeniería de software:

* **Optimización de Base de Datos:** Se implementaron consultas SQL con `LEFT JOIN` y agregaciones (`SUM`, `GROUP BY`) para eliminar el *lag* en la interfaz, logrando un rendimiento fluido incluso con cientos de registros.
* **Manejo de Encoding:** Resolución de problemas de codificación de caracteres (UTF-8/Latin-1) para garantizar que nombres con **Ñ** o tildes se procesen correctamente, evitando errores de visualización.
* **UX/UI Intuitiva:** Diseño de interfaz enfocado en la eficiencia del usuario final (operarios y administrativos), minimizando la cantidad de clics para tareas repetitivas.

---

## 💻 Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** Tkinter (Customized UI)
* **Base de Datos:** SQLite3 (Persistencia local)
* **Formatos de Intercambio:** JSON y CSV (Excel)

---

## 📦 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/Gestion-Horas-Extras.git](https://github.com/tu-usuario/Gestion-Horas-Extras.git)
2  **Ejecutar la aplicación**
    python app.py


📂 Estructura del Proyecto
app.py: Lógica de la interfaz gráfica, validaciones de entrada y gestión de eventos de usuario.

database.py: Capa de persistencia, consultas SQL optimizadas y lógica de cálculos matemáticos.

sistema_jornales.db: Base de datos relacional ligera que almacena la persistencia de agentes y movimientos.

👨‍💻 Autor
Facundo Salass
Desarrollador enfocado en soluciones pragmáticas y automatización de procesos.
