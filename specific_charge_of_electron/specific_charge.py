# insert copyleft licence here

import numpy as np
import tools
import external_data


def print_tabulars():
    [dat, voltage, current, N, R, b] = external_data.read_data()

    volt_curr = np.concatenate((np.matrix(voltage).T, np.matrix(current).T),axis=1) # second dimension
    tools.print_to_latex_tabular(volt_curr, column_precisions=[0,2])

    # the full measurement, expect top row (beacause of rounding).
    table_mat = np.concatenate((np.matrix(voltage).T, dat*1000), axis=1)
    tools.print_to_latex_tabular(table_mat, column_precisions=1)

    # top_row_of_table_mat
    # tools.print_to_latex_tabular(current, column_precisions=2)

    # other single values, the leading zeros reserve blank space for later editing
    tools.print_to_latex_tabular([[0,N],[0,R],[0,b]], column_precisions=3, significant_figures=True)




def Main():
    print_tabulars()


Main()