# Simulador del Administrador de Tareas de Windows en Python

## 1. Introducción

### Descripción General
Aplicación de escritorio que replica las funcionalidades principales del Administrador de Tareas de Windows (Task Manager), permitiendo monitorear y gestionar procesos del sistema, rendimiento de hardware, servicios y aplicaciones en ejecución.

### Objetivo del Proyecto
Crear una herramienta educativa y funcional que demuestre:
- Monitoreo de procesos del sistema operativo
- Visualización de métricas de rendimiento en tiempo real
- Gestión de procesos (finalizar, prioridad, afinidad)
- Interfaz gráfica intuitiva similar al Task Manager original

### Alcance
- **Fase 1**: Procesos y rendimiento básico (CPU, Memoria)
- **Fase 2**: Detalles avanzados y gráficos en tiempo real
- **Fase 3**: Servicios, inicio automático y usuarios
- **Fase 4**: Historial y análisis de rendimiento

---

## 2. Arquitectura del Sistema

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaz Gráfica (GUI)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Procesos │Rendimiento│ Detalles │ Servicios│  Inicio  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Capa de Lógica de Negocio                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │  Process    │ Performance │   Service   │   Startup   │ │
│  │  Manager    │   Monitor   │   Manager   │   Manager   │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Capa de Acceso a Datos del Sistema               │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   psutil    │   WMI/Win32 │  Threading  │   Logging   │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Sistema Operativo                          │
└─────────────────────────────────────────────────────────────┘
```

### Patrón de Diseño
- **MVC (Model-View-Controller)**: Separación entre datos, presentación y lógica
- **Observer Pattern**: Para actualización en tiempo real de métricas
- **Singleton**: Para gestores de sistema únicos
- **Factory Pattern**: Para creación de diferentes tipos de monitores

---

## 3. Componentes Principales

### 3.1 Módulo de Procesos (Process Manager)

#### Responsabilidades
- Obtener lista de procesos activos
- Monitorear uso de recursos por proceso (CPU, RAM, Disco, Red)
- Gestionar procesos (terminar, suspender, reanudar)
- Cambiar prioridad de procesos
- Establecer afinidad de CPU

#### Información a Capturar por Proceso
- **Identificación**: PID, Nombre, Descripción, Usuario
- **Recursos**: CPU (%), Memoria (MB), Disco (MB/s), Red (KB/s)
- **Estado**: En ejecución, Suspendido, No responde
- **Detalles**: Ruta del ejecutable, Línea de comandos, Fecha de inicio
- **Relaciones**: Proceso padre, Procesos hijos, DLLs cargadas

#### Operaciones Disponibles
- Finalizar proceso
- Finalizar árbol de procesos
- Establecer prioridad (Tiempo real, Alta, Normal, Baja)
- Establecer afinidad de CPU
- Crear volcado de proceso
- Abrir ubicación del archivo
- Buscar en línea

### 3.2 Módulo de Rendimiento (Performance Monitor)

#### Métricas de CPU
- Utilización total (%)
- Utilización por núcleo (%)
- Velocidad actual y base
- Procesos activos
- Threads activos
- Handles
- Tiempo de actividad

#### Métricas de Memoria
- Memoria en uso / Total
- Memoria comprometida / Límite
- Memoria en caché
- Memoria paginada / No paginada
- Pool de paginación / No paginación
- Caché modificada
- Caché en espera
- Memoria libre

#### Métricas de Disco
- Uso por disco (%)
- Tiempo activo
- Velocidad de lectura (MB/s)
- Velocidad de escritura (MB/s)
- Tiempo de respuesta promedio

#### Métricas de Red
- Throughput por adaptador (Mbps)
- Bytes enviados/recibidos
- Conexiones activas
- Utilización del adaptador (%)

#### Métricas de GPU (Opcional)
- Utilización (%)
- Memoria dedicada en uso
- Memoria compartida en uso
- Temperatura

### 3.3 Módulo de Detalles (Details View)

#### Columnas Configurables
Lista completa de información disponible por proceso:
- Básico: Nombre, PID, Estado, Usuario
- CPU: %, Tiempo de CPU, Ciclos
- Memoria: Memoria privada, Conjunto de trabajo, Pico de trabajo
- Disco: I/O de lectura, I/O de escritura, Total de I/O
- Red: Bytes de red, Throughput de red
- GPU: Uso de GPU, Memoria de GPU

#### Funcionalidades
- Ordenamiento por cualquier columna
- Filtrado por usuario, tipo de proceso
- Búsqueda en tiempo real
- Exportación de datos (CSV, TXT)
- Agrupación por tipo o usuario

### 3.4 Módulo de Servicios (Service Manager)

#### Información de Servicios
- Nombre del servicio
- Descripción
- Estado (En ejecución, Detenido, Pausado)
- Tipo de inicio (Automático, Manual, Deshabilitado)
- Usuario de inicio
- PID (si está en ejecución)

#### Operaciones
- Iniciar servicio
- Detener servicio
- Reiniciar servicio
- Pausar/Reanudar servicio
- Cambiar tipo de inicio
- Ver propiedades

### 3.5 Módulo de Inicio (Startup Manager)

#### Información de Programas de Inicio
- Nombre de la aplicación
- Editor/Fabricante
- Estado (Habilitado/Deshabilitado)
- Impacto en el inicio (Alto, Medio, Bajo, No medido)
- Ubicación de registro o carpeta
- Línea de comandos
- Fecha de deshabilitación (si aplica)

#### Operaciones
- Habilitar/Deshabilitar
- Abrir ubicación del archivo
- Buscar en línea
- Ver propiedades

---

## 4. Tecnologías y Librerías de Python

### 4.1 Librerías de Sistema

#### psutil (Obligatorio)
- **Propósito**: Acceso multiplataforma a información del sistema
- **Capacidades**:
  - Procesos: Lista, información, control (kill, suspend)
  - CPU: Utilización, frecuencia, estadísticas por núcleo
  - Memoria: Virtual, swap, detalle por proceso
  - Disco: Particiones, uso, I/O
  - Red: Interfaces, estadísticas, conexiones

#### pywin32 (Windows específico)
- **Propósito**: API nativa de Windows
- **Capacidades**:
  - WMI: Windows Management Instrumentation
  - Servicios: Control total de servicios Windows
  - Registro: Acceso a entradas de inicio automático
  - Eventos: Captura de eventos del sistema

#### wmi (Alternativa a pywin32)
- **Propósito**: Interfaz simplificada a WMI
- **Capacidades**:
  - Información detallada de hardware
  - Procesos y servicios
  - Configuración del sistema

### 4.2 Librerías de Interfaz Gráfica

#### PyQt6 o PyQt5 (Recomendado)
- **Ventajas**:
  - Interfaz nativa y profesional
  - Widgets avanzados (QTableView, QTreeView)
  - Gráficos con QtCharts
  - Actualización eficiente con Signals/Slots
  - Theming y estilos personalizables
- **Componentes clave**:
  - QMainWindow: Ventana principal
  - QTabWidget: Sistema de pestañas
  - QTableWidget/QTableView: Tablas de datos
  - QTimer: Actualización periódica
  - QPushButton, QMenu: Controles

#### Tkinter (Alternativa simple)
- **Ventajas**: Incluido en Python estándar
- **Desventajas**: Apariencia menos moderna, menos widgets

#### CustomTkinter (Alternativa moderna)
- **Ventajas**: Tkinter con apariencia moderna
- **Desventajas**: Menos maduro que PyQt

### 4.3 Librerías de Visualización

#### matplotlib
- **Propósito**: Gráficos de rendimiento en tiempo real
- **Uso**: Historial de CPU, RAM, Disco, Red

#### pyqtgraph (Si se usa PyQt)
- **Propósito**: Gráficos de alto rendimiento
- **Ventajas**: Actualización en tiempo real más eficiente que matplotlib

### 4.4 Librerías Auxiliares

#### threading / multiprocessing
- **Propósito**: Actualización en segundo plano sin bloquear UI
- **Uso**: Worker threads para monitoreo continuo

#### dataclasses / pydantic
- **Propósito**: Modelado de datos estructurados
- **Uso**: Clases para Process, Service, StartupItem

#### logging
- **Propósito**: Registro de eventos y errores
- **Uso**: Debug y monitoreo de la aplicación

---

## 5. Estructura de Archivos del Proyecto

```
task_manager_simulator/
│
├── main.py                          # Punto de entrada
│
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Configuraciones globales
│   └── constants.py                 # Constantes (refresh rates, etc.)
│
├── models/
│   ├── __init__.py
│   ├── process.py                   # Modelo de datos de proceso
│   ├── service.py                   # Modelo de datos de servicio
│   ├── performance.py               # Modelo de datos de rendimiento
│   └── startup_item.py              # Modelo de datos de inicio
│
├── core/
│   ├── __init__.py
│   ├── process_manager.py           # Gestor de procesos
│   ├── performance_monitor.py       # Monitor de rendimiento
│   ├── service_manager.py           # Gestor de servicios
│   ├── startup_manager.py           # Gestor de inicio automático
│   └── system_info.py               # Información general del sistema
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Ventana principal
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── processes_tab.py         # Pestaña de procesos
│   │   ├── performance_tab.py       # Pestaña de rendimiento
│   │   ├── details_tab.py           # Pestaña de detalles
│   │   ├── services_tab.py          # Pestaña de servicios
│   │   └── startup_tab.py           # Pestaña de inicio
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── process_table.py         # Tabla de procesos personalizada
│   │   ├── performance_chart.py     # Gráfico de rendimiento
│   │   ├── resource_gauge.py        # Medidor de recursos
│   │   └── context_menu.py          # Menús contextuales
│   └── dialogs/
│       ├── __init__.py
│       ├── process_properties.py    # Propiedades de proceso
│       ├── service_properties.py    # Propiedades de servicio
│       └── about_dialog.py          # Diálogo Acerca de
│
├── utils/
│   ├── __init__.py
│   ├── formatters.py                # Formateo de datos (MB, %, etc.)
│   ├── sorters.py                   # Algoritmos de ordenamiento
│   ├── filters.py                   # Filtros de datos
│   └── validators.py                # Validaciones
│
├── workers/
│   ├── __init__.py
│   ├── monitor_worker.py            # Worker para monitoreo continuo
│   └── update_worker.py             # Worker para actualizaciones
│
├── resources/
│   ├── icons/                       # Iconos de la aplicación
│   ├── styles/                      # Hojas de estilo (QSS)
│   └── images/                      # Imágenes adicionales
│
├── tests/
│   ├── __init__.py
│   ├── test_process_manager.py
│   ├── test_performance_monitor.py
│   └── test_ui.py
│
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   └── user_guide.md
│
├── requirements.txt                 # Dependencias
├── setup.py                         # Script de instalación
├── README.md                        # Documentación principal
└── LICENSE                          # Licencia del proyecto
```

---

## 6. Flujo de Datos y Actualización

### 6.1 Ciclo de Actualización

```
┌─────────────────────────────────────────────────┐
│  QTimer (cada 1 segundo por defecto)            │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  Worker Thread: Recolectar datos del sistema    │
│  - psutil.process_iter()                        │
│  - psutil.cpu_percent()                         │
│  - psutil.virtual_memory()                      │
│  - psutil.disk_io_counters()                    │
│  - psutil.net_io_counters()                     │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  Signal/Slot: Enviar datos a UI Thread          │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  UI Thread: Actualizar widgets                  │
│  - Actualizar tabla de procesos                 │
│  - Actualizar gráficos                          │
│  - Actualizar etiquetas de métricas             │
└─────────────────────────────────────────────────┘
```

### 6.2 Manejo de Threads

**Thread Principal (UI Thread)**
- Renderizado de interfaz
- Manejo de eventos del usuario
- Actualizaciones visuales

**Worker Thread (Monitor Thread)**
- Recolección de datos del sistema
- Procesamiento de información
- Cálculos de métricas

**Comunicación**
- Signals/Slots en PyQt
- Thread-safe queues
- Locks para datos compartidos

---

## 7. Consideraciones Técnicas

### 7.1 Rendimiento

#### Optimizaciones Necesarias
- **Actualización selectiva**: Solo actualizar datos visibles en la pestaña activa
- **Caching**: Cachear información estática (nombre de proceso, ruta)
- **Throttling**: Ajustar frecuencia de actualización según necesidad
- **Lazy loading**: Cargar detalles solo cuando se solicitan
- **Delta updates**: Solo actualizar valores que cambiaron

#### Frecuencias de Actualización Recomendadas
- Procesos: 1-2 segundos
- CPU: 1 segundo
- Memoria: 2-3 segundos
- Disco: 2-3 segundos
- Red: 1-2 segundos
- GPU: 2-3 segundos

### 7.2 Permisos y Privilegios

#### Requerimientos
- **Procesos de usuario**: No requiere privilegios especiales
- **Procesos del sistema**: Requiere ejecución como administrador
- **Servicios**: Requiere privilegios de administrador
- **Registro (Inicio)**: Puede requerir permisos elevados

#### Manejo de Privilegios
- Detectar nivel de privilegios al inicio
- Mostrar advertencia si se ejecuta sin privilegios
- Solicitar elevación UAC cuando sea necesario
- Limitar operaciones según privilegios disponibles

### 7.3 Compatibilidad

#### Sistemas Operativos
- **Windows 10/11**: Funcionalidad completa
- **Windows 7/8**: Funcionalidad básica (algunas API no disponibles)
- **Linux/Mac**: Funcionalidad limitada (sin servicios Windows, inicio)

#### Python
- **Versión mínima**: Python 3.8+
- **Versión recomendada**: Python 3.10+

### 7.4 Manejo de Errores

#### Errores Comunes
- **Proceso terminado**: Manejar procesos que terminan durante consulta
- **Acceso denegado**: Procesos del sistema protegidos
- **Servicio no encontrado**: Servicio eliminado o no disponible
- **Memoria insuficiente**: Sistema bajo recursos

#### Estrategias
- Try-except en todas las operaciones de sistema
- Logging detallado de errores
- Mensajes de error amigables para el usuario
- Recuperación automática cuando sea posible

---

## 8. Características Avanzadas (Futuras)

### 8.1 Análisis de Rendimiento
- Histórico de uso de recursos
- Detección de cuellos de botella
- Alertas de uso excesivo
- Exportación de reportes

### 8.2 Gestión Avanzada de Procesos
- Inyección de DLL
- Volcado de memoria
- Análisis de handles
- Inspección de módulos cargados

### 8.3 Monitoreo de Red
- Conexiones por proceso
- Puertos en escucha
- Tráfico en tiempo real
- Filtrado de conexiones

### 8.4 GPU y Hardware Especializado
- Monitoreo de GPU (NVIDIA, AMD)
- Temperaturas de hardware
- Velocidades de ventiladores
- Voltajes

### 8.5 Personalización
- Temas claros/oscuros
- Columnas personalizables
- Atajos de teclado configurables
- Perfils de visualización

### 8.6 Integración
- Exportación a CSV/JSON
- API REST para consultas externas
- Integración con herramientas de monitoreo
- Plugins extensibles

---

## 9. Roadmap de Implementación

### Fase 1: MVP (2-3 semanas)
**Objetivo**: Aplicación funcional básica

1. **Semana 1**:
   - Configurar entorno y estructura de proyecto
   - Implementar modelos de datos básicos
   - Crear ProcessManager con psutil
   - Implementar ventana principal con PyQt

2. **Semana 2**:
   - Implementar pestaña de Procesos
   - Tabla de procesos con información básica
   - Operaciones básicas (terminar proceso)
   - Actualización en tiempo real

3. **Semana 3**:
   - Implementar pestaña de Rendimiento
   - Gráficos básicos de CPU y Memoria
   - Métricas en tiempo real
   - Testing y corrección de bugs

### Fase 2: Características Intermedias (2-3 semanas)

4. **Semana 4-5**:
   - Implementar pestaña de Detalles
   - Columnas configurables
   - Filtros y búsqueda
   - Menús contextuales completos

5. **Semana 6**:
   - Implementar pestaña de Servicios
   - Gestión de servicios Windows
   - Control de servicios (iniciar/detener)

### Fase 3: Características Avanzadas (2-3 semanas)

6. **Semana 7-8**:
   - Implementar pestaña de Inicio
   - Gestión de programas de inicio
   - Impacto en el inicio
   - Monitoreo de disco y red avanzado

7. **Semana 9**:
   - Optimización de rendimiento
   - Theming y estilos
   - Documentación completa

### Fase 4: Pulido y Extra (1-2 semanas)

8. **Semana 10**:
   - Testing exhaustivo
   - Corrección de bugs
   - Características opcionales (GPU, análisis)
   - Empaquetado y distribución

---

## 10. Métricas de Éxito

### Funcionalidad
- ✅ Muestra al menos 90% de los procesos activos
- ✅ Actualización en tiempo real sin lag perceptible
- ✅ Operaciones sobre procesos funcionan correctamente
- ✅ Gráficos de rendimiento precisos

### Rendimiento
- ✅ Uso de CPU del simulador < 5% en idle
- ✅ Uso de memoria del simulador < 150 MB
- ✅ Tiempo de actualización < 100ms
- ✅ UI responsiva incluso con >100 procesos

### Usabilidad
- ✅ Interfaz intuitiva similar al Task Manager
- ✅ Respuesta inmediata a acciones del usuario
- ✅ Mensajes de error claros
- ✅ Documentación completa

---

## 11. Riesgos y Mitigaciones

### Riesgos Técnicos

**Riesgo 1**: Rendimiento degradado con muchos procesos
- **Mitigación**: Virtualización de tablas, actualización selectiva

**Riesgo 2**: Acceso denegado a procesos del sistema
- **Mitigación**: Detección de privilegios, manejo de excepciones

**Riesgo 3**: API de psutil incompleta para ciertas métricas
- **Mitigación**: Uso de pywin32 como fallback, WMI para datos específicos

**Riesgo 4**: Incompatibilidad entre versiones de Windows
- **Mitigación**: Feature detection, degradación elegante

### Riesgos de Proyecto

**Riesgo 5**: Complejidad de la UI
- **Mitigación**: Desarrollo incremental, priorización de funcionalidades

**Riesgo 6**: Tiempo de desarrollo subestimado
- **Mitigación**: MVP bien definido, fases opcionales

---

## 12. Referencias y Recursos

### Documentación Oficial
- **psutil**: https://psutil.readthedocs.io/
- **PyQt6**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **pywin32**: https://github.com/mhammond/pywin32
- **Windows API**: https://docs.microsoft.com/en-us/windows/win32/

### Tutoriales y Guías
- System monitoring with Python
- Building desktop apps with PyQt
- Windows process management
- Real-time data visualization

### Proyectos Similares
- Process Hacker
- System Explorer
- Process Explorer (Sysinternals)

---

## 13. Glosario

- **PID**: Process ID, identificador único de proceso
- **Thread**: Hilo de ejecución dentro de un proceso
- **Handle**: Referencia a un recurso del sistema
- **Working Set**: Memoria física actualmente utilizada por un proceso
- **Private Bytes**: Memoria asignada exclusivamente a un proceso
- **I/O**: Input/Output, operaciones de lectura/escritura
- **WMI**: Windows Management Instrumentation
- **UAC**: User Account Control, control de cuentas de usuario
- **DLL**: Dynamic Link Library, biblioteca de enlace dinámico
- **Pool**: Área de memoria del kernel
- **Paged/Non-Paged**: Memoria que puede/no puede ser movida a disco

---

## 14. Conclusión

Este documento proporciona una guía completa para implementar un simulador del Administrador de Tareas de Windows en Python. El proyecto combina:

- **Programación de sistemas**: Acceso a APIs de bajo nivel
- **Desarrollo de interfaces**: UI moderna y responsiva
- **Arquitectura de software**: Diseño modular y escalable
- **Optimización**: Rendimiento y uso eficiente de recursos

El resultado será una herramienta educativa que demuestra conceptos avanzados de programación mientras proporciona funcionalidad real para monitorear y gestionar procesos del sistema.

**Siguiente Paso**: Comenzar con la Fase 1 del roadmap, configurando el entorno y creando la estructura básica del proyecto.
