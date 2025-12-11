import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.logger import logger

def main():
    try:
        app = QApplication(sys.argv)
        
        window = MainWindow()
        window.show()
        
        logger.info("Приложение запущено")
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Сбой приложения")
        sys.exit(1)

if __name__ == "__main__":
    main()
