import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column
import tools

a = np.array([[2,3.0,4], [1,2,3]])

class data:
    """
    Because python does not have structures
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
        self.pressure = 0.98091 * 1e5    # Pa

        # m (#), rot (°)
        meas_3_1 = np.array([[0, 20, 40, 60, 80, 100], [0.6, 5.0, 6.9, 8.4, 9.4, 10.5]])
        self.meas_3_1 = meas_3_1.transpose()
        meas_3_2 = np.array([[0, 20, 40, 60, 80, 100], [1.0, 5.0, 7.0, 8.4, 9.5, 10.6]])
        self.meas_3_2 = meas_3_2.transpose()

        self.width_of_glass_plate = 5.59e-3  # m




def plot_wave_length():

    fig = figure(x_axis_label='m', y_axis_label="dₗ (μm)") # title="Valon kulkema lisämatka interferenssisiirtymien funktiona",

    distance = (50-data().meas_1[:,1]) * 2 * 1e-6
    m_count = data().meas_1[:,0]

    #fig.circle(m_count, distance, legend="mittausdata", size=10, fill_color="white")

    x = np.linspace(0,100,1000)
    k ,k_err = tools.linear_regression_origo(m_count, distance)
    fig.line(x, k*x*1e6, legend="sovite ∂dₗ/∂m = λ = "+str(round(k*1e9))+"nm", line_width=2)
    fig.line(x, (k+k_err) * x*1e6, line_width=1, color=(0,0,128), line_dash="dashed")
    fig.line(x, (k-k_err) * x*1e6, legend="keskivirherajat λ = "+str(round(k*1e9))+"±"+str(round(k_err*1e9))+"nm",\
             line_width=1, color=(0,0,128), line_dash="dashed")

    fig.circle(m_count, distance*1e6, legend="mittauspisteet", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"


    print("Wave length")
    print("    slope i.e. lambda:", k, ", error: ", k_err,\
          ", maxium range in deviation:", np.sqrt((k_err/np.sqrt(5))**2 + k_err**2))




    return fig


def plot_refractive_index_air():
    fig = figure(x_axis_label='Δp (Pa)', y_axis_label="Δn")# title="Ilman taitekertoimen muutos paineen funktiona")

    pressure_drop = data().meas_2_2[:,0]*1e5 # Assuming we measured pressure difference to current.
    m_count = data().meas_2_2[:,1]

    lambda_0 = 633e-9   # wavelength in vacuum (m)
    n_0 = 1             # refractive index in vacuum ()
    chamber_length = 0.03    # m (m)
    delta_n = lambda_0 * m_count /(2*chamber_length)

    x = np.linspace(0, 0.7e5, 1000)
    k, k_err = tools.linear_regression_origo(pressure_drop, delta_n)
    # no latex in bokeh :(
    fig.line(x, k*x, legend="sovite ∂(Δn)/∂(Δp) = ("+str(round(k*1e9,2))+")*10⁻⁹ (1/Pa)", line_width=2)
    fig.line(x, (k + k_err) * x, line_width=1, color=(0, 0, 128), line_dash="dashed")
    fig.line(x, (k - k_err) * x, legend="keskivirherajat ∂n/∂p = ("+str(round(k*1e9,2))+"±"+str(round(k_err*1e9,2))+")*10⁻⁹ (1/Pa)",\
             line_width=1, color=(0, 0, 128),line_dash="dashed")

    fig.circle(pressure_drop, delta_n, legend="mittauspisteet", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"




    air_pressure = data().pressure
    air_pressure_err = 50  # Pa # this is just rough guess, it could be 10 Pa too

    # I'm not using maxium error, but rather mean error

    # f = n_0 + (∂n/∂p)*p_1

    # ∂n/∂p = k
    # p_1 = air_pressure

    # Δ(∂n/∂p) = k_err
    # Δ(p_1) = air_pressure_err

    # ∂f/∂(n_0) = 0
    # ∂f/∂(∂n/∂p) = air_pressure
    # ∂f/∂(p_1) = k

    # Δf = sqrt( (∂f/∂(∂n/∂p) * Δ(∂n/∂p))^2  +  (∂f/∂(p_1) * Δ(p_1))^2 )

    # INCORRECT
    # INCORRECT
    m_f = np.sqrt((air_pressure * k_err)**2 + (k * air_pressure_err)**2)
    Delta_f = np.abs(air_pressure) * k_err + np.abs(k) * air_pressure_err
    # INCORRECT
    # INCORRECT


    print("Refractive index of air")
    print("    slope i.e. ∂n/∂p:", k, ", error:", k_err, ", n_room:", n_0 + k*air_pressure,\
          ", maxium range in deviation:", np.sqrt((k_err/np.sqrt(7))**2 + k_err**2))
    print("    [INCORRECT]cumulative mean error in n_room:", m_f)
    print("    [INCORRECT]cumulative maxium error in n_room:", Delta_f)
    print("")


    return fig


def plot_refractive_index_glass():
    fig = figure(x_axis_label='nimittäjä (m)', y_axis_label="osoittaja (m)")# title="Lasin taitekertoimen muutos paineen funktiona")

    m_count = data().meas_3_2[:,0]

    angle_1 = data().meas_3_1[:,1]
    angle_2 = data().meas_3_2[:, 1]
    angle = ((angle_1 + angle_2)/2)*2*np.pi/360

    lambda_0 = 633e-9 # Should we use the value we measured?
    d = data().width_of_glass_plate

    numerator =  (2*d - m_count*lambda_0) * (1- np.cos(angle))
    denominator = 2*d*(1 - np.cos(angle)) - m_count*lambda_0
    #tools.print_to_latex_tabular(np.hstack((np.matrix(numerator).T, np.matrix(denominator).T)), column_precisions=[3,3])


    x = np.linspace(0, 1.30e-04, 1000)
    k, k_err = tools.linear_regression_origo(denominator, numerator)
    print("Refractive index of glass")
    print("    slope", k, ", error:", k_err,\
          ", maxium range in deviation:", np.sqrt((k_err/np.sqrt(6))**2 + k_err**2))

    fig.line(x, k*x, legend="sovite ∂y/∂x = "+str(round(k,2)), line_width=2)
    fig.line(x, (k + k_err) * x, line_width=1, color=(0, 0, 128), line_dash="dashed")
    fig.line(x, (k - k_err) * x, legend="keskivirherajat ∂y/∂x = ("+str(round(k,2))+"±"+str(round(k_err,2))+")",\
             line_width=1, color=(0, 0, 128), line_dash="dashed")

    fig.circle(denominator, numerator, legend="mittauspisteet", size=10, color="black", fill_color="white", line_width=2)

    fig.legend.location = "top_left"


    return fig


def print_latex_tabulars():
    tools.print_to_latex_tabular(data().meas_1, column_precisions=[0,1,1], significant_figures=False)
    tools.print_to_latex_tabular(data().meas_2_2, column_precisions=[2, 1], significant_figures=False)

    angle_1 = data().meas_3_1
    angle_2 = data().meas_3_2
    angle_mean = ((angle_1 + angle_2) / 2)
    tools.print_to_latex_tabular(angle_mean, column_precisions=[0, 1], significant_figures=False)


def main():
    fig1 = plot_wave_length()
    fig2 = plot_refractive_index_air()
    fig3 = plot_refractive_index_glass()

    output_file("plots.html", title="This is the title of most important kind")

    show(column(fig1,fig2,fig3))

    #print_latex_tabulars()





main()