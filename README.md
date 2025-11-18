# Task Manager Simulator

Simulador del Administrador de Tareas de Windows desarrollado en Python con PyQt6.

## Características

- **Monitor de Procesos**: Visualización en tiempo real de todos los procesos activos
- **Rendimiento del Sistema**: Métricas de CPU, memoria, disco y red
- **Gestión de Procesos**: Finalizar, suspender y reanudar procesos
- **Interfaz Gráfica Moderna**: Desarrollada con PyQt6
- **Multiplataforma**: Compatible con Windows, Linux y macOS

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd PyTaskManager
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Ejecutar con privilegios de administrador (recomendado)

Para acceder a todos los procesos del sistema, se recomienda ejecutar con privilegios de administrador:

**Windows:**
```bash
# Abrir PowerShell o CMD como Administrador
python main.py
```

**Linux:**
```bash
sudo python3 main.py
```

## Estructura del Proyecto

```
PyTaskManager/
│
├── main.py                          # Punto de entrada
├── requirements.txt                 # Dependencias
├── README.md                        # Documentación
│
└── task_manager_simulator/
    ├── config/                      # Configuración
    │   ├── settings.py
    │   └── constants.py
    │
    ├── models/                      # Modelos de datos
    │   ├── process.py
    │   ├── performance.py
    │   ├── service.py
    │   └── startup_item.py
    │
    ├── core/                        # Lógica de negocio
    │   ├── process_manager.py
    │   └── performance_monitor.py
    │
    ├── ui/                          # Interfaz gráfica
    │   ├── main_window.py
    │   ├── tabs/
    │   │   ├── processes_tab.py
    │   │   └── performance_tab.py
    │   ├── widgets/
    │   └── dialogs/
    │
    └── utils/                       # Utilidades
        └── formatters.py
```

## Funcionalidades Implementadas

### ✅ Fase 1 (MVP)

- [x] Estructura del proyecto
- [x] Modelos de datos (Process, Performance, Service)
- [x] ProcessManager básico con psutil
- [x] PerformanceMonitor básico
- [x] Ventana principal con PyQt6
- [x] Pestaña de Procesos
  - Lista de procesos con información básica
  - Finalizar procesos
  - Suspender/Reanudar procesos
  - Actualización en tiempo real
- [x] Pestaña de Rendimiento
  - Métricas de CPU (uso, velocidad, núcleos)
  - Métricas de Memoria (uso, disponible, swap)
  - Tiempo de actividad del sistema

### 🚧 Pendiente (Fases 2-4)

- [ ] Pestaña de Detalles con columnas configurables
- [ ] Pestaña de Servicios (Windows)
- [ ] Pestaña de Inicio (Windows)
- [ ] Gráficos en tiempo real de rendimiento
- [ ] Monitoreo de disco y red avanzado
- [ ] Historial de rendimiento
- [ ] Exportación de datos
- [ ] Temas claro/oscuro

## Atajos de Teclado

- `F5` - Actualizar vista actual
- `Ctrl+Q` - Salir de la aplicación

## Capturas de Pantalla

*(Próximamente)*

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación
- **PyQt6**: Framework de interfaz gráfica
- **psutil**: Biblioteca de monitoreo del sistema
- **pywin32**: API de Windows (solo en Windows)

## Permisos y Limitaciones

### Sin privilegios de administrador:
- Solo se pueden ver procesos del usuario actual
- No se pueden finalizar procesos del sistema
- Información limitada de algunos procesos

### Con privilegios de administrador:
- Acceso completo a todos los procesos
- Gestión completa de servicios
- Acceso a métricas avanzadas del sistema

## Solución de Problemas

### Error: "Permission denied" al finalizar procesos
- Ejecute la aplicación con privilegios de administrador
- Algunos procesos del sistema están protegidos y no pueden ser finalizados

### La aplicación no muestra todos los procesos
- Ejecute con privilegios de administrador
- En Linux, use `sudo`

### Error al instalar PyQt6
```bash
# Intente actualizar pip primero
pip install --upgrade pip
pip install PyQt6
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Cree una rama para su feature (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

PyTaskManager Team

## Agradecimientos

- Inspirado en el Administrador de Tareas de Windows
- Desarrollado con fines educativos
- Basado en las especificaciones en `task_manager_simulator_specs.md`

## Roadmap

Ver el archivo `task_manager_simulator_specs.md` para el roadmap completo y las especificaciones técnicas detalladas.

## Soporte

Para reportar bugs o solicitar features, por favor abra un issue en el repositorio.
