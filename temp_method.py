    def update_calc_map_from_input(self):
        """
        Parses input from CoordsWidget and updates the map.
        Similar to WktConverterWidget.refresh_map but for the calculation page.
        """
        try:
            data = self.coords_widget.get_data()
            wgs_text = data["wgs"]
            
            points = []
            if wgs_text:
                lines = wgs_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    # Try to parse line
                    parts = line.replace(',', ' ').split()
                    parts = [p.strip() for p in parts if p.strip()]
                    
                    if len(parts) >= 2:
                        try:
                            # Heuristic parsing
                            lat, lon = 0.0, 0.0
                            label = ""
                            
                            # Case 1: ID, Lat, Lon, H (4+)
                            if len(parts) >= 4:
                                label = parts[0]
                                lat = float(parts[1])
                                lon = float(parts[2])
                            # Case 2: Lat, Lon, H (3) - could be ID, Lat, Lon
                            elif len(parts) == 3:
                                # Try as Lat, Lon, H
                                try:
                                    lat = float(parts[0])
                                    lon = float(parts[1])
                                except ValueError:
                                    # Maybe ID, Lat, Lon
                                    label = parts[0]
                                    lat = float(parts[1])
                                    lon = float(parts[2])
                            # Case 3: Lat, Lon (2)
                            elif len(parts) == 2:
                                lat = float(parts[0])
                                lon = float(parts[1])
                                
                            points.append((lat, lon, label))
                        except ValueError:
                            pass
            
            self.calc_map_widget.update_map(points, show_polygon=self.chk_calc_show_polygon.isChecked())
            
        except Exception as e:
            # Silent error for real-time updates to avoid spamming
            pass
