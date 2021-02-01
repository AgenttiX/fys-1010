import numpy as np

def read_data():
    # diameters (not radiuses) unit: meter m
    # columns: current, rows: voltage
    dat=np.array([[74.3, 69.0, 64.4, 59.0, 51.1, 44.1], \
                  [76.8, 70.9, 66.6, 63.8, 58.6, 49.9], \
                  [87.3, 76.4, 72.5, 64.7, 58.6, 55.1], \
                  [92.8, 85.6, 73.5, 67.7, 65.1, 53.2], \
                  [99.4, 88.5, 78.5, 69.6, 64.3, 60.6], \
                 [103.2, 93.8, 79.9, 75.1, 68.0, 63.0]]) * 0.001  # unit: meter

    voltage = np.array([200, 220, 240, 260, 280, 300])  # (V)
    current = np.array([1.20, 1.36, 1.52, 1.68, 1.84, 2.00])  # (A)


    # number of loops in coil
    N = 130
    # diameter of coil
    R = 0.150  # (m)
    # distance betweed the two helmholtz coil
    b = 0.156  # (m)
    # Magnetization constant for helmholtz coils
    K_r = 0.0007444 #± 0.0000038

    return dat, voltage, current, N, R, b, K_r
