import sys
import os

# Add src to path
sys.path.append(os.path.abspath("."))

try:
    from src.gui.widgets.wkt_converter_widget import WktConverterWidget
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
