# insert copyleft license here

import numpy as np
import tools
import external_data

# import plotly.offline as py
# import plotly.graph_objs as go
import matplotlib.pyplot as plt


def print_data_tabulars():
    [dat, voltage, current, N, R, b, K_r] = external_data.read_data()

    print("Voltage and current")
    volt_curr = np.concatenate((np.matrix(voltage).T, np.matrix(current).T), axis=1)  # second dimension
    tools.print_to_latex_tabular(volt_curr, column_precisions=[0, 2])

    print("The measurement")
    # the full measurement, expect top row (beacause of rounding).
    table_mat = np.concatenate((np.matrix(voltage).T, dat*1000), axis=1)
    tools.print_to_latex_tabular(table_mat, column_precisions=[0, 1, 1, 1, 1, 1, 1])

    # top_row_of_table_mat
    # tools.print_to_latex_tabular(current, column_precisions=2)

    print("Helmholtz coil information")
    # other single values, the leading zeros reserve blank space for later editing
    tools.print_to_latex_tabular([[0, N], [0, R], [0, b], [0, K_r]], column_precisions=3, significant_figures=True)


def magnet_field():
    """
    Task 7 instruction-sheet.
    :return:
    """
    # TODO VIRHERAJAT ILMOITETTUUN TARKKUUTEEN
    [dat, U, I, N, R, b, K_r] = external_data.read_data()
    # equation 10
    B = K_r*I
    # milliamperes
    tools.print_to_latex_tabular(np.matrix(B).T*1e3, column_precisions=5)


def magnet_field_calc():
    [dat, U, I, N, R, b, K_r] = external_data.read_data()
    mikro = 1.2566370614*1e-6
    K = mikro * N * R**2 / ((b/2)**2 + R**2)**(3/2)
    print("Verrannollisuuskertoimet")
    print("K:", K, "  K_r:", K_r, " eta:", K_r/K)


def main():
    print("## Data tabulars ##\n")
    print_data_tabulars()
    print("\n\n## Magnet field (7), in mT ##")
    magnet_field()

    dat, voltage, current, N, R, b, K_r = external_data.read_data()

    magnetic_field = K_r*current
    # print(K_r)
    # print(current)
    print(magnetic_field)

    qm_array = np.zeros((6, 6))

    for voltage_i in range(6):
        for current_i in range(6):
            qm_array[voltage_i, current_i] = \
                (2*voltage[voltage_i]) / ((magnetic_field[current_i]**2) * ((dat[voltage_i, current_i]*0.5)**2))

    # print(qm_array)

    print("q/m e11")
    tools.print_to_latex_tabular(qm_array*1e-11, column_precisions=[4, 4, 4, 4, 4, 4])

    # plot_data = [
    #     go.Histogram(x=qm_array.flatten())
    # ]
    # py.plot(plot_data, filename="histogram.html")

    qm_min = qm_array.min()
    qm_max = qm_array.max()

    print("Min:", qm_min)
    print("Max:", qm_max)

    qm_range = qm_max - qm_min
    qm_bar_width = qm_range / 6
    print("Range:", qm_range)
    print("Bar width", qm_bar_width)

    print("Most likely:", qm_min + (qm_bar_width*1.5))

    plt.hist(qm_array.flatten(), bins=6)
    plt.xlabel("Ominaisvaraus (C/kg)")
    plt.ylabel("Frekvenssi (kpl)")
    plt.show()

    print("Theoretical:", 1.6021766208e-19 / 9.10938356e-31)

    magnet_field_calc()


main()
