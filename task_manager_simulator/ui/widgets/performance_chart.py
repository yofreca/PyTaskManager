"""
Widget de gráfico de rendimiento en tiempo real.
"""
import logging
from typing import List
from collections import deque

try:
    import pyqtgraph as pg
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QWidget, QVBoxLayout


logger = logging.getLogger(__name__)


class PerformanceChart(QWidget):
    """
    Widget que muestra un gráfico de rendimiento en tiempo real.

    Usa pyqtgraph si está disponible, sino muestra un placeholder.
    """

    def __init__(self, title: str = "Performance", max_points: int = 60,
                 y_range: tuple = (0, 100), parent=None):
        """
        Inicializa el gráfico de rendimiento.

        Args:
            title: Título del gráfico
            max_points: Número máximo de puntos a mostrar
            y_range: Rango del eje Y (min, max)
            parent: Widget padre
        """
        super().__init__(parent)

        self.title = title
        self.max_points = max_points
        self.y_range = y_range
        self.data = deque(maxlen=max_points)

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if PYQTGRAPH_AVAILABLE:
            self._init_pyqtgraph()
        else:
            self._init_placeholder()

    def _init_pyqtgraph(self):
        """Inicializa el gráfico con pyqtgraph."""
        # Configurar el widget de gráfico
        pg.setConfigOptions(antialias=True)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#FFFFFF')
        self.plot_widget.setTitle(self.title, color='#000000', size='12pt')
        self.plot_widget.setLabel('left', 'Percentage', units='%', color='#000000')
        self.plot_widget.setLabel('bottom', 'Time', units='s', color='#000000')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(self.y_range[0], self.y_range[1])
        self.plot_widget.setXRange(0, self.max_points)

        # Configurar la curva
        pen = pg.mkPen(color='#0078D4', width=2)
        self.curve = self.plot_widget.plot(pen=pen)

        # Configurar el área rellena debajo de la curva
        self.fill = pg.FillBetweenItem(
            self.curve,
            pg.PlotCurveItem([0], [0]),
            brush=pg.mkBrush(color=(0, 120, 212, 50))
        )
        self.plot_widget.addItem(self.fill)

        self.layout().addWidget(self.plot_widget)

        logger.debug(f"PerformanceChart '{self.title}' inicializado con pyqtgraph")

    def _init_placeholder(self):
        """Inicializa un placeholder si pyqtgraph no está disponible."""
        label = QLabel(f"{self.title}\n[Graph requires pyqtgraph]\n\nInstall with: pip install pyqtgraph")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: gray;
                font-size: 12px;
                padding: 20px;
                border: 1px dashed #cccccc;
                background-color: #f5f5f5;
            }
        """)
        self.layout().addWidget(label)

        logger.warning(f"PerformanceChart '{self.title}' usando placeholder - pyqtgraph no disponible")

    def update_data(self, value: float):
        """
        Actualiza el gráfico con un nuevo valor.

        Args:
            value: Nuevo valor a agregar
        """
        if not PYQTGRAPH_AVAILABLE:
            return

        self.data.append(value)

        # Actualizar la curva
        x_data = list(range(len(self.data)))
        y_data = list(self.data)

        self.curve.setData(x_data, y_data)

    def update_data_series(self, values: List[float]):
        """
        Actualiza el gráfico con una serie completa de valores.

        Args:
            values: Lista de valores
        """
        if not PYQTGRAPH_AVAILABLE:
            return

        self.data.clear()
        self.data.extend(values[-self.max_points:])

        x_data = list(range(len(self.data)))
        y_data = list(self.data)

        self.curve.setData(x_data, y_data)

    def clear(self):
        """Limpia el gráfico."""
        self.data.clear()
        if PYQTGRAPH_AVAILABLE:
            self.curve.setData([], [])

    def set_y_range(self, min_val: float, max_val: float):
        """
        Establece el rango del eje Y.

        Args:
            min_val: Valor mínimo
            max_val: Valor máximo
        """
        if PYQTGRAPH_AVAILABLE:
            self.y_range = (min_val, max_val)
            self.plot_widget.setYRange(min_val, max_val)


class MultiSeriesChart(QWidget):
    """
    Widget que muestra múltiples series en un gráfico.

    Útil para mostrar uso por núcleo de CPU, etc.
    """

    def __init__(self, title: str = "Multi-Series", max_points: int = 60,
                 y_range: tuple = (0, 100), num_series: int = 1, parent=None):
        """
        Inicializa el gráfico multi-serie.

        Args:
            title: Título del gráfico
            max_points: Número máximo de puntos a mostrar
            y_range: Rango del eje Y
            num_series: Número de series a mostrar
            parent: Widget padre
        """
        super().__init__(parent)

        self.title = title
        self.max_points = max_points
        self.y_range = y_range
        self.num_series = num_series
        self.data_series = [deque(maxlen=max_points) for _ in range(num_series)]

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if PYQTGRAPH_AVAILABLE:
            self._init_pyqtgraph()
        else:
            self._init_placeholder()

    def _init_pyqtgraph(self):
        """Inicializa el gráfico con pyqtgraph."""
        pg.setConfigOptions(antialias=True)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#FFFFFF')
        self.plot_widget.setTitle(self.title, color='#000000', size='12pt')
        self.plot_widget.setLabel('left', 'Percentage', units='%', color='#000000')
        self.plot_widget.setLabel('bottom', 'Time', units='s', color='#000000')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setYRange(self.y_range[0], self.y_range[1])
        self.plot_widget.setXRange(0, self.max_points)

        # Crear curvas para cada serie
        self.curves = []
        colors = self._generate_colors(self.num_series)

        for i in range(self.num_series):
            pen = pg.mkPen(color=colors[i], width=1.5)
            curve = self.plot_widget.plot(pen=pen, name=f"Series {i+1}")
            self.curves.append(curve)

        self.layout().addWidget(self.plot_widget)

        logger.debug(f"MultiSeriesChart '{self.title}' inicializado con {self.num_series} series")

    def _init_placeholder(self):
        """Inicializa un placeholder."""
        label = QLabel(f"{self.title}\n[Graph requires pyqtgraph]")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-size: 12px;")
        self.layout().addWidget(label)

    def _generate_colors(self, count: int) -> List[str]:
        """Genera una lista de colores para las series."""
        # Paleta de colores
        base_colors = [
            '#0078D4',  # Azul
            '#107C10',  # Verde
            '#D83B01',  # Rojo
            '#FFB900',  # Amarillo
            '#E74856',  # Rosa
            '#0099BC',  # Cyan
            '#8764B8',  # Púrpura
            '#498205',  # Verde oscuro
        ]

        # Repetir colores si hay más series que colores
        colors = []
        for i in range(count):
            colors.append(base_colors[i % len(base_colors)])

        return colors

    def update_data(self, series_index: int, value: float):
        """
        Actualiza una serie con un nuevo valor.

        Args:
            series_index: Índice de la serie (0-based)
            value: Nuevo valor
        """
        if not PYQTGRAPH_AVAILABLE or series_index >= self.num_series:
            return

        self.data_series[series_index].append(value)

        x_data = list(range(len(self.data_series[series_index])))
        y_data = list(self.data_series[series_index])

        self.curves[series_index].setData(x_data, y_data)

    def update_all_series(self, values: List[float]):
        """
        Actualiza todas las series con nuevos valores.

        Args:
            values: Lista de valores, uno por serie
        """
        if not PYQTGRAPH_AVAILABLE:
            return

        for i, value in enumerate(values[:self.num_series]):
            self.update_data(i, value)

    def clear(self):
        """Limpia todas las series."""
        for data in self.data_series:
            data.clear()

        if PYQTGRAPH_AVAILABLE:
            for curve in self.curves:
                curve.setData([], [])
