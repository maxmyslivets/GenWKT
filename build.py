import PyInstaller.__main__
import shutil
from pathlib import Path

def build():
    print("Начинается процесс сборки...")
    
    # Очистка dist/build
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
        
    # Аргументы PyInstaller
    args = [
        "main.py",
        "--name=GenWKT",
        "--noconsole",
        "--onedir",
        "--noconfirm",
        "--icon=assets/icon.png",
        "--add-data=assets;assets",
        "--add-data=src/gui/styles;src/gui/styles",
        "--hidden-import=PySide6",
        "--clean",
    ]
    
    PyInstaller.__main__.run(args)
    
    print("Сборка завершена. Исполняемый файл находится в dist/GenWKT/GenWKT.exe")

if __name__ == "__main__":
    build()
