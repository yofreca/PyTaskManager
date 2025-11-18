# Task Manager Simulator

Simulador del Administrador de Tareas de Windows desarrollado en Python.

## 📋 Descripción

Aplicación de escritorio que replica las funcionalidades principales del Administrador de Tareas de Windows (Task Manager), permitiendo monitorear y gestionar procesos del sistema, rendimiento de hardware, servicios y aplicaciones en ejecución.

## ✨ Características

### Fase 1 (MVP) - En Desarrollo
- ✅ Monitoreo de procesos en tiempo real
- ✅ Visualización de uso de CPU y Memoria
- ✅ Gestión básica de procesos (terminar procesos)
- ✅ Interfaz gráfica con PyQt6

### Fases Futuras
- 🔄 Detalles avanzados de procesos
- 🔄 Gestión de servicios Windows
- 🔄 Administración de programas de inicio
- 🔄 Monitoreo de disco y red
- 🔄 Gráficos históricos de rendimiento

## 🛠️ Tecnologías

- **Python 3.8+**
- **PyQt6** - Interfaz gráfica
- **psutil** - Monitoreo del sistema
- **matplotlib/pyqtgraph** - Visualización de datos
- **pywin32/WMI** - APIs específicas de Windows (opcional)

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/yofreca/PyTaskManager.git
cd PyTaskManager

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo
pip install -e .
```

## 🚀 Uso

```bash
# Ejecutar la aplicación
python task_manager_simulator/main.py

# O usando el comando instalado
task-manager
```

## 📁 Estructura del Proyecto

```
task_manager_simulator/
├── main.py                          # Punto de entrada
├── config/                          # Configuraciones
├── models/                          # Modelos de datos
├── core/                            # Lógica de negocio
│   ├── process_manager.py           # Gestor de procesos
│   ├── performance_monitor.py       # Monitor de rendimiento
│   ├── service_manager.py           # Gestor de servicios
│   └── startup_manager.py           # Gestor de inicio
├── ui/                              # Interfaz gráfica
│   ├── main_window.py               # Ventana principal
│   ├── tabs/                        # Pestañas
│   ├── widgets/                     # Componentes personalizados
│   └── dialogs/                     # Diálogos
├── utils/                           # Utilidades
├── workers/                         # Workers para threading
├── resources/                       # Recursos (iconos, estilos)
└── tests/                           # Tests unitarios
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=task_manager_simulator
```

## 🎯 Roadmap

- [x] **Fase 1: MVP** (2-3 semanas)
  - [x] Estructura del proyecto
  - [ ] Gestión de procesos básica
  - [ ] Monitoreo de rendimiento
  - [ ] Interfaz básica

- [ ] **Fase 2: Características Intermedias** (2-3 semanas)
  - [ ] Vista de detalles avanzada
  - [ ] Gestión de servicios

- [ ] **Fase 3: Características Avanzadas** (2-3 semanas)
  - [ ] Programas de inicio
  - [ ] Monitoreo de disco y red

- [ ] **Fase 4: Pulido** (1-2 semanas)
  - [ ] Testing exhaustivo
  - [ ] Theming y estilos
  - [ ] Documentación completa

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- PyTaskManager Team

## 🙏 Agradecimientos

- Inspirado en el Administrador de Tareas de Windows
- Comunidad de Python y PyQt
- Mantenedores de psutil y otras librerías utilizadas

## 📚 Documentación Adicional

Para más detalles sobre la arquitectura y especificaciones técnicas, consulta:
- [Especificaciones completas](task_manager_simulator_specs.md)
- [Documentación de arquitectura](docs/architecture.md)
- [Guía de usuario](docs/user_guide.md)
