import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column
import tools

a = np.array([[2,3.0,4], [1,2,3]])

class data:
    """
    Because python does not have structs
    """

    # I don't care what it does as long it works. Now it is possible to call 'data().meas_2_1'
    # I also tested class without any initializer: it worked as such too.
    @classmethod
    def __init__(self):
        # m (#), d_m (1e-6m), delta_d_m (1e-6m)
        meas_1 = np.array([[20, 40, 60, 80, 100], [43.2, 37.1, 30.9, 24.9, 18.7], [6.8, 6.1, 6.2, 6.0, 6.2]])
        self.meas_1 = meas_1.transpose()

        # P_f (bar), m (#)
        meas_2_1 = np.array([[0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], [12, 12, 9.5, 7.5, 5.5, 4,2]])
        self.meas_2_1 = meas_2_1.transpose()

        # P_f (bar), m (#)
        meas_2_2 = np.array([[0.65, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1], [14, 13, 11, 9, 7, 4, 3]])
        self.meas_2_2 = meas_2_2.transpose()

        self.atmospheric_pressure = 73.574  # cmHg

        # m (#), rot (°)
        meas_3_1 = np.array([[0, 20, 60, 80, 100], [0.6, 5.0, 6.9, 8.4, 9.4, 10.5]])
        self.meas_3_1 = meas_3_1.transpose()
        meas_3_2 = np.array([[0, 20, 60, 80, 100], [1.0, 5.0, 7.0, 8.4, 9.5, 10.6]])
        self.meas_3_2 = meas_3_2.transpose()

        self.width_of_glass_plate = 5.59  # mm




def plot_wave_length():

    fig = figure(title="Valon kulkema matka interferenssisiirtymien funktiona")

    distance = (50-data().meas_1[:,1]) * 2 * 1e-6
    m_count = data().meas_1[:,0]

    fig.circle(m_count, distance, legend="mittausdata", size=3)

    x = np.linspace(0,100,1000)
    k ,k_err = tools.too_lazy_to_import_linear_regression_tool(m_count, distance)
    print("Kulmakerroin: ", k, "virhe: ", k_err)
    fig.line(x, k*x, legend="sovite", line_width=2)
    fig.line(x, (k+k_err) * x, line_width=1, color=(0,0,128), line_dash="dashed")
    fig.line(x, (k-k_err) * x, legend="virherajat", line_width=1, color=(0,0,128), line_dash="dashed")

    fig.legend.location = "top_left"

    output_file("aallonpituus.html", title="Aallopituus")
    show(fig)









plot_wave_length()