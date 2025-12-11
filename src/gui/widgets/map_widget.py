from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from src.core.logger import logger
import folium
import io

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_points = []
        self.show_polygon = True  # Default to True as requested

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.web_view)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(400) # Minimum width as requested
        
        # Initial empty map
        self.update_map([])

    def update_map(self, points, show_polygon=True):
        """
        Обновляет карту с заданными точками.
        :param points: Список кортежей (lat, lon, label) или (lat, lon)
        :param show_polygon: Рисовать ли полигон по точкам
        """
        self.current_points = points
        self.show_polygon = show_polygon
        
        try:
            if not points:
                # Default map (e.g., Moscow or world)
                m = folium.Map(location=[55.7558, 37.6173], zoom_start=5)
            else:
                # Calculate center
                lats = [p[0] for p in points]
                lons = [p[1] for p in points]
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)
                
                m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
                
                # Add markers
                for p in points:
                    lat, lon = p[0], p[1]
                    popup = str(p[2]) if len(p) > 2 else f"{lat:.5f}, {lon:.5f}"
                    folium.Marker([lat, lon], popup=popup).add_to(m)
                
                # Add polygon if requested and we have enough points
                if show_polygon and len(points) >= 3:
                    folium.Polygon(
                        locations=[(p[0], p[1]) for p in points],
                        color="blue",
                        weight=2,
                        fill=True,
                        fill_opacity=0.2
                    ).add_to(m)
                
                # Fit bounds
                m.fit_bounds([(min(lats), min(lons)), (max(lats), max(lons))])

            # Save to HTML and load
            data = io.BytesIO()
            m.save(data, close_file=False)
            html = data.getvalue().decode()
            self.web_view.setHtml(html)
            
        except Exception as e:
            logger.exception("Ошибка обновления карты")
