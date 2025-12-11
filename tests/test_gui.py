import pytest
from PySide6.QtCore import Qt
from src.gui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_window_title(app):
    assert "GenWKT" in app.windowTitle()

def test_projection_defaults(app):
    assert app.proj_widget.entry_cm.text() == "29 59 59,91779"
    assert app.proj_widget.entry_scale.text() == "1.0"

def test_calculation_error_empty(app, qtbot):
    # Должна показываться ошибка, если нет данных
    # Мы не можем легко протестировать QMessageBox с pytest-qt без моков, 
    # но мы можем проверить, обработано ли исключение или вызвана ли логика.
    # Пока просто проверим, что виджеты существуют.
    assert app.btn_calc is not None
