import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.gui.widgets.wkt_converter_widget import WktConverterWidget

@pytest.fixture
def widget(qtbot):
    widget = WktConverterWidget()
    qtbot.addWidget(widget)
    return widget

def test_wkt_conversion(widget, qtbot):
    # Установка валидного WKT и координат
    wkt = 'PROJCS["Transverse_Mercator",GEOGCS["GCS_Pulkovo_1942",DATUM["D_Pulkovo_1942",SPHEROID["Krassowsky_1942",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",39.0],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
    
    widget.wkt_edit.setText(wkt)
    widget.lat_input.setText("55.0")
    widget.lon_input.setText("39.0")
    widget.h_input.setText("100.0")
    
    # Нажатие конвертировать
    qtbot.mouseClick(widget.btn_convert, Qt.MouseButton.LeftButton)
    
    # Проверка результатов (CM = 39, поэтому X должен быть около 500000)
    assert widget.x_res.text() != ""
    assert widget.y_res.text() != ""
    assert widget.h_res.text() != ""
    
    # Приблизительная проверка
    x = float(widget.x_res.text())
    assert x == pytest.approx(6097200, abs=10000) # Northing для 55 градусов
    
def test_invalid_input(widget, qtbot, monkeypatch):
    widget.wkt_edit.setText("INVALID WKT")
    widget.lat_input.setText("abc")
    
    # Мок QMessageBox, чтобы избежать блокировки
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", lambda *args: None)
    
    # Должно показать сообщение об ошибке (теперь замокано)
    qtbot.mouseClick(widget.btn_convert, Qt.MouseButton.LeftButton)
    
    # Результаты должны быть пустыми или неизменными, если произошел сбой раньше
    assert widget.x_res.text() == ""

def test_load_prj_cancel(widget, qtbot, monkeypatch):
    # Мок QFileDialog, чтобы ничего не возвращать
    monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.getOpenFileName", lambda *args: ("", ""))
    
    widget.load_from_prj()
    assert widget.wkt_edit.toPlainText() == ""
