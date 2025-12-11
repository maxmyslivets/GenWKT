import numpy as np
from src.core.converter import CoordinateConverter
from src.core.estimator import ParameterEstimator

def test_calculation():
    converter = CoordinateConverter()
    estimator = ParameterEstimator()

    # Input Data
    wgs_data = [
        [1, 55.9132151, 28.7827337, 148.13],
        [2, 55.9177362, 28.8195407, 153.07],
        [3, 55.8997317, 28.8448859, 150.32],
        [4, 55.8879009, 28.8148194, 144.81],
        [5, 55.8993879, 28.7702963, 140.8]
    ]

    msk_data = [
        [1, 7686.0995773235, -8996.72764806, 128.313878864],
        [2, 8149.5516395103, -6686.6830560778, 133.2730658024],
        [3, 6118.3181298608, -5135.559022994, 130.5397422902],
        [4, 4832.9892219482, -7038.7691853523, 125.0153974839],
        [5, 6160.4605288561, -9801.7721945621, 120.9794011708]
    ]

    # Parameters
    # Shift X: -6191992.4462 (Assuming X_proj = X_msk - Shift_X)
    # Shift Y: 67119.6943 (Assuming Y_proj = Y_msk - Shift_Y or similar)
    # CM: 29 59 59.91779 (From previous context, as user repeated the shift value for CM which is likely error)
    
    shift_x = -6191992.4462
    shift_y = 67119.6943
    
    cm_dms = "29 59 59.91779"
    cm_deg = converter.parse_dms(cm_dms)
    
    print(f"CM: {cm_deg}")
    
    wgs_coords = []
    msk_coords = []
    
    for i in range(len(wgs_data)):
        w_lat, w_lon, w_h = wgs_data[i][1], wgs_data[i][2], wgs_data[i][3]
        m_x, m_y, m_h = msk_data[i][1], msk_data[i][2], msk_data[i][3]
        
        # Apply Shifts
        # Try 1: X_proj = m_x - shift_x (since shift is negative, this adds ~6M)
        #        Y_proj = m_y - shift_y (since m_y is -9000 and we expect -76000, subtracting 67000 works)
        
        x_proj = m_x - shift_x
        y_proj = m_y - shift_y
        
        # WGS -> Cartesian
        wx, wy, wz = converter.wgs84_to_cartesian(w_lat, w_lon, w_h)
        wgs_coords.append([wx, wy, wz])
        
        # MSK -> Cartesian
        # We calculated x_proj (Northing) and y_proj (Easting)
        mx, my, mz = converter.msk_to_cartesian(northing=x_proj, easting=y_proj, h=m_h, central_meridian_deg=cm_deg, false_easting=0, false_northing=0)
        msk_coords.append([mx, my, mz])
        
    wgs_coords = np.array(wgs_coords)
    msk_coords = np.array(msk_coords)
    
    # Estimate
    params = estimator.calculate_helmert(wgs_coords, msk_coords)
    
    print("Calculated Parameters:")
    for k, v in params.items():
        print(f"{k}: {v}")
        
    # Residuals
    transformed = estimator.apply_helmert(wgs_coords, params)
    residuals = msk_coords - transformed
    
    print("\nResiduals (m):")
    rms = np.sqrt(np.mean(residuals**2))
    print(f"RMS: {rms}")
    print(residuals)

if __name__ == "__main__":
    try:
        test_calculation()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
