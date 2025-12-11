
import pytest
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.widgets.wkt_converter_widget import WktConverterWidget

# Use pytest-qt's qtbot if available, otherwise manual QApplication
# Assuming pytest-qt is installed as per user rules

def test_wkt_converter_multiline(qtbot):
    widget = WktConverterWidget()
    qtbot.addWidget(widget)
    widget.show() # Ensure widget is shown so children visibility can be checked
    
    # Set WKT (Standard Pulkovo 1942)
    wkt = 'PROJCS["Transverse_Mercator",GEOGCS["GCS_Pulkovo_1942",DATUM["D_Pulkovo_1942",SPHEROID["Krassowsky_1942",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",39.0],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
    widget.wkt_edit.setText(wkt)
    
    # Set Multi-line input with mixed formats
    # 1. ID, Lat, Lon, H
    # 2. Lat, Lon, H (no ID)
    # 3. ID, Lat, Lon (no H) - handled as ID, Lat, Lon -> H=0 if parsed correctly
    input_text = "1, 55.0, 39.0, 100\n56.0 40.0 200\nPT2, 57.0, 41.0"
    widget.coords_input.setText(input_text)
    
    # Click Convert
    qtbot.mouseClick(widget.btn_convert, Qt.LeftButton)
    
    # Check warning label (Should be visible as WKT has no vertical CRS)
    assert widget.lbl_height_warning.isVisible() == True
    
    # Check results in table
    assert widget.result_table.rowCount() == 3
    assert widget.result_table.columnCount() == 4 # ID, X, Y, H
    
    # Row 0: 1, 55.0, 39.0, 100
    id0 = widget.result_table.item(0, 0).text()
    x0 = widget.result_table.item(0, 1).text()
    h0 = widget.result_table.item(0, 3).text()
    
    assert id0 == "1"
    assert float(h0) == 100.0
    
    # Row 1: 56.0, 40.0, 200 (No ID)
    id1 = widget.result_table.item(1, 0).text()
    h1 = widget.result_table.item(1, 3).text()
    
    assert id1 == "" # Empty ID
    assert float(h1) == 200.0
    
    # Row 2: PT2, 57.0, 41.0 (No H)
    id2 = widget.result_table.item(2, 0).text()
    h2 = widget.result_table.item(2, 3).text()
    
    assert id2 == "PT2"
    assert float(h2) == 0.0 # Default H

def test_wkt_converter_warning_hidden(qtbot):
    widget = WktConverterWidget()
    qtbot.addWidget(widget)
    widget.show()
    
    # Set WKT with Geoid (Mocking check_vertical_crs or using a WKT that triggers it)
    # Since we can't easily mock the internal converter without patching, let's use a WKT that "looks" like it has EGM2008
    # The check looks for "EGM2008" in sub_crs name or wkt.
    
    wkt_with_geoid = 'COMPD_CS["unknown + EGM2008 geoid height",PROJCS["Transverse_Mercator",GEOGCS["GCS_Pulkovo_1942",DATUM["D_Pulkovo_1942",SPHEROID["Krassowsky_1942",6378245.0,298.3]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",39.0],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]],VERT_CS["EGM2008 geoid height",VERT_DATUM["EGM2008  geoid",2005,AUTHORITY["EPSG","1027"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","3855"]]]'
    
    widget.wkt_edit.setText(wkt_with_geoid)
    widget.coords_input.setText("55.0 39.0 100")
    
    # Click Convert
    qtbot.mouseClick(widget.btn_convert, Qt.LeftButton)
    
    # Check warning label (Should be HIDDEN)
    assert widget.lbl_height_warning.isVisible() == False
