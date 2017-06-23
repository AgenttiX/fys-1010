import numpy as np


a = np.array([[2,3.0,4], [1,2,3]])

def data():
    # m (#), d_m (1e-6m), delta_d_m (1e-6m)
    meas_1 = np.array([[20, 40, 60, 80, 100], [43.2, 37.1, 30.9, 24.9, 18.7], [6.8, 6.1, 6.2, 6.0, 6.2]])
    meas_1 = meas_1.transpose()

    # P_f (bar), m (#)
    meas_2_1 = np.array([[0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], [12, 12, 9.5, 7.5, 5.5, 4,2]])
    meas_2_1 = meas_2_1.transpose()

    # P_f (bar), m (#)
    meas_2_2 = np.array([[0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], [14, 13, 11, 9, 7, 4, 3]])
    meas_2_2 = meas_2_2.transpose()

    atmospheric_pressure = 73.574  # cmHg

    # m (#), rot (°)
    meas_3_1 = ([[0, 20, 60, 80, 100], [0.6, 5.0, 6.9, 8.4, 9.4, 10.5]])
    meas_3_1 = meas_3_1.transpose()
    meas_3_2 = ([[0, 20, 60, 80, 100], [1.0, 5.0, 7.0, 8.4, 9.5, 10.6]])
    meas_3_2 = meas_3_2.transpose()

    width_of_glass_plate = 5.59  # mm



    return meas_1, meas_2_1, meas_2_2, meas_3_1, meas_3_2