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

        self.pressure_primitive_units = 73.574  # cmHg
        self.pressure = 0.98090 * 1e5    # Pa

        # m (#), rot (°)
        meas_3_1 = np.array([[0, 20, 40, 60, 80, 100], [0.6, 5.0, 6.9, 8.4, 9.4, 10.5]])
        self.meas_3_1 = meas_3_1.transpose()
        meas_3_2 = np.array([[0, 20, 40, 60, 80, 100], [1.0, 5.0, 7.0, 8.4, 9.5, 10.6]])
        self.meas_3_2 = meas_3_2.transpose()

        self.width_of_glass_plate = 5.59e-3  # m




def plot_wave_length():

    fig = figure(title="Valon kulkema matka interferenssisiirtymien funktiona",
                 x_axis_label='m', y_axis_label="dₘ (μm)")

    distance = (50-data().meas_1[:,1]) * 2 * 1e-6
    m_count = data().meas_1[:,0]

    #fig.circle(m_count, distance, legend="mittausdata", size=10, fill_color="white")

    x = np.linspace(0,100,1000)
    k ,k_err = tools.too_lazy_to_import_linear_regression_tool(m_count, distance)
    print("Wave length")
    print("    slope i.e. lambda:", k, ", error: ", k_err)
    fig.line(x, k*x*1e6, legend="sovite λ="+str(round(k*1e9))+"±"+str(round(k_err*1e9))+"nm", line_width=2)
    fig.line(x, (k+k_err) * x*1e6, line_width=1, color=(0,0,128), line_dash="dashed")
    fig.line(x, (k-k_err) * x*1e6, legend="virherajat", line_width=1, color=(0,0,128), line_dash="dashed")

    fig.circle(m_count, distance*1e6, legend="mittausdata", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"

    return fig


def plot_refractive_index_air():
    fig = figure(title="Ilman taitekertoimen muutos paineen funktiona")

    pressure_drop = data().meas_2_2[:,0]*1e5 # Assuming we measured pressure difference to current.
    m_count = data().meas_2_2[:,1]

    lambda_0 = 633e-9   # wavelength in vacuum (m)
    n_0 = 1             # refractive index in vacuum ()
    chamber_length = 0.03    # m (m)
    delta_n = lambda_0 * m_count /(2*chamber_length)

    x = np.linspace(0, 0.7e5, 1000)
    k, k_err = tools.too_lazy_to_import_linear_regression_tool(pressure_drop, delta_n)
    print("Refractive index of air")
    print("    slope i.e. ∂n/∂p:", k, ", error:", k_err, ", n_room:", n_0 + k*data().pressure)
    # no latex in bokeh :(
    fig.line(x, k*x, legend="sovite ∂n/∂p=("+str(round(k*1e9,2))+"±"+str(round(k_err*1e9,2))+")*10⁻⁹", line_width=2)
    fig.line(x, (k + k_err) * x, line_width=1, color=(0, 0, 128), line_dash="dashed")
    fig.line(x, (k - k_err) * x, legend="virherajat", line_width=1, color=(0, 0, 128),
             line_dash="dashed")

    fig.circle(pressure_drop, delta_n, legend="mittausdata", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"


    return fig


def plot_refractive_index_glass():
    fig = figure(title="Lasin taitekertoimen muutos paineen funktiona")

    m_count = data().meas_3_2[:,0]

    angle_1 = data().meas_3_1[:,1]
    angle_2 = data().meas_3_2[:, 1]
    angle = ((angle_1 + angle_2)/2)*2*np.pi/360

    lambda_0 = 633e-9 # Should we use the value we measured?
    d = data().width_of_glass_plate

    numerator =  (2*d - m_count*lambda_0) * (1- np.cos(angle))

    denominator = 2*d*(1 - np.cos(angle)) - m_count*lambda_0


    x = np.linspace(0, 1.30e-04, 1000)
    k, k_err = tools.too_lazy_to_import_linear_regression_tool(denominator, numerator)
    print("Refractive index of glass")
    print("    slope", k, ", error:", k_err)

    fig.line(x, k*x, legend="sovite ∂y/∂x=("+str(round(k,2))+"±"+str(round(k_err,2))+")", line_width=2)
    fig.line(x, (k + k_err) * x, line_width=1, color=(0, 0, 128), line_dash="dashed")
    fig.line(x, (k - k_err) * x, legend="virherajat", line_width=1, color=(0, 0, 128),
             line_dash="dashed")

    fig.circle(denominator, numerator, legend="mittausdata", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"


    return fig



def main():
    fig1 = plot_wave_length()
    fig2 = plot_refractive_index_air()
    fig3 = plot_refractive_index_glass()

    output_file("plots.html", title="This is the title of most important kind") # todo make up better title

    show(column(fig1,fig2,fig3))



main()