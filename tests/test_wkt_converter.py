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
    # Ввод координат в многострочное поле: ID, Lat, Lon, H
    widget.coords_input.setText("1, 55.0, 39.0, 100.0")
    
    # Нажатие конвертировать
    qtbot.mouseClick(widget.btn_convert, Qt.MouseButton.LeftButton)
    
    # Проверка результатов в таблице
    assert widget.result_table.rowCount() == 1
    
    # Получаем значения из таблицы (ID, N, E, H)
    n_item = widget.result_table.item(0, 1)
    e_item = widget.result_table.item(0, 2)
    h_item = widget.result_table.item(0, 3)
    
    assert n_item is not None
    assert e_item is not None
    assert h_item is not None
    
    # Приблизительная проверка
    x = float(n_item.text())
    # Northing для 55 градусов на CM 39 (это прямо на меридиане, X должен быть около 6097200)
    assert x == pytest.approx(6097200, abs=10000)
    
def test_invalid_input(widget, qtbot, monkeypatch):
    widget.wkt_edit.setText("INVALID WKT")
    widget.coords_input.setText("abc")
    
    # Мок QMessageBox, чтобы избежать блокировки
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", lambda *args: None)
    
    # Должно показать сообщение об ошибке (теперь замокано)
    qtbot.mouseClick(widget.btn_convert, Qt.MouseButton.LeftButton)
    
    # Результаты должны быть пустыми (таблица пустая)
    assert widget.result_table.rowCount() == 0

def test_load_prj_cancel(widget, qtbot, monkeypatch):
    # Мок QFileDialog, чтобы ничего не возвращать
    monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.getOpenFileName", lambda *args: ("", ""))
    
    widget.load_from_prj()
    assert widget.wkt_edit.toPlainText() == ""
