import numpy as np
from math import log10, floor
from bokeh.models import Label

class iterating_colors():
    """
    This class is made to mimic matlab-like color plotting behavior. Calling get_next() method
    returns new color in list, without hazzle. By default colorset is same as in matlab
    """
    def __init__(self, palette="matlab"):
        if (palette == "matlab"):
            self.colors = [  # matlab_line_plot_colors
                [0.0000,    0.4470,    0.7410],
                [0.8500,    0.3250,    0.0980],
                [0.9290,    0.6940,    0.1250],
                [0.4940,    0.1840,    0.5560],
                [0.4660,    0.6740,    0.1880],
                [0.3010,    0.7450,    0.9330],
                [0.6350,    0.0780,    0.1840]]

        if (palette == "octave"):
            self.colors = [ # octave and old matlab (version <= R2014a) line plotting colors
                [0.00000,   0.00000,   1.00000],
                [0.00000,   0.50000,   0.00000],
                [1.00000,   0.00000,   0.00000],
                [0.00000,   0.75000,   0.75000],
                [0.75000,   0.00000,   0.75000],
                [0.75000,   0.75000,   0.00000],
                [0.25000,   0.25000,   0.25000]]

        if (palette == "long"):
            # from
            # http://blogs.mathworks.com/pick/2008/08/15/colors-for-your-multi-line-plots/
            self.colors = [
                [0.00,  0.00,  1.00],
                [0.00,  0.50,  0.00],
                [1.00,  0.00,  0.00],
                [0.00,  0.75,  0.75],
                [0.75,  0.00,  0.75],
                [0.75,  0.75,  0.00],
                [0.25,  0.25,  0.25],
                [0.75,  0.25,  0.25],
                [0.95,  0.95,  0.00],
                [0.25,  0.25,  0.75],
                [0.75,  0.75,  0.75],
                [0.00,  1.00,  0.00],
                [0.76,  0.57,  0.17],
                [0.54,  0.63,  0.22],
                [0.34,  0.57,  0.92],
                [1.00,  0.10,  0.60],
                [0.88,  0.75,  0.73],
                [0.10,  0.49,  0.47],
                [0.66,  0.34,  0.65],
                [0.99,  0.41,  0.23]]

        self.current_index = 0


    def get_next(self):
        """
        Returns next color in colormap, color jumps to first one after the last color is used.
        :return: tuple length of 3, type: int varitying from 0 to 255.
        """
        m = len(self.colors)  # the number of rows
        color = self.colors[self.current_index % m]
        RGB_color = [round(x*255.45) for x in color]
        self.current_index+=1
        return tuple(RGB_color)

    def reset(self):
        self.current_index = 0

def too_lazy_to_import_linear_regression_tool(x_axis, data_points):
    """
    This fuction calulates linear regresion (slope and error) for line which goes through origo.
    The approach is rather manual, but precise and clear.
    :param data_points: numpy array
    :return:
            micro   slope of fitted line
            err     mean error in that slope
    """
    # these libraries are shit
    #return np.linalg.lstsq(x_axis,data_points)[0]

    # Numpy arrays can't be column vectors! Not lying! They are that feeble and ambiguous by default.
    x_mat = np.transpose(np.matrix(x_axis))
    y_mat = np.transpose(np.matrix(data_points))

    # If it is wanted that origo is not fixed, then replace x_mat by X_mat in micro calulations
    X_mat = np.concatenate((x_mat, np.ones( (x_axis.shape[0],1) ) ), axis=1)

    # No really, these libraries _are_ pure shit! They break down if some matrix-dimension is one!
    #return np.linalg.lstsq(X_mat, y_mat)[0]


    # Then let's do it the hard way.

    # https://en.wikipedia.org/wiki/Linear_regression
    # https://en.wikipedia.org/wiki/Least_squares
    micro = (np.linalg.inv(x_mat.transpose() * x_mat) * np.transpose(x_mat) * y_mat)[0,0]

    # https://en.wikipedia.org/wiki/Mean_squared_error
    # https://en.wikipedia.org/wiki/Standard_deviation
    # https://en.wikipedia.org/wiki/Simple_linear_regression#Normality_assumption
    x_mean = np.sum(x_mat)/x_mat.size
    dof = 1 # degrees of freedom
    MSE = (1/(y_mat.size-dof)) * \
            np.sum(np.multiply((y_mat-micro*x_mat),(y_mat-micro*x_mat))) / \
            np.sum(np.multiply((x_mat-x_mean),(x_mat-x_mean)))
    err = np.sqrt(MSE)

    return micro, err


def print_to_latex_tabular(array, column_precisions=None, significant_figures=True):
    """
    Prints 2d-numpy arrays (or regular lists) to latex tabular format. Then just copy-paste it.

    :param array: array to print (list or numpy array, type:float)
    :param column_precisions: array of precisions for column (list or numpy array, type:int, len=columns)
    :param significant_figures: if false then precision corresponds the number of digits
    :return:

    Examples:
        column_precisions=[...,4,...], significant_figures=True:
            0.0012345678 -> 0.001234
        column_precisions=[...,4,...], significant_figures=False:
            0.0012345678 -> 0.0012
    """

    if ((column_precisions != None) and (np.shape(array)[1] != len(column_precisions))):
        raise "column_precisions should be vector of length of columns"

    array_to_print = [["" for n in range(np.shape(array)[1])] for m in range(np.shape(array)[0])]

    # convert array to printable form
    for m in range(np.shape(array)[0]):
        for n in range(np.shape(array)[1]):

            if (column_precisions == None):
                array_to_print[m][n] = str(array[m, n])
            elif (significant_figures):
                array_to_print[m][n] = str(round(array[m, n], -int(floor(log10(abs(array[m, n]))))+column_precisions[n]))
            elif (column_precisions[n] > 0):
                array_to_print[m][n] = str(round(array[m,n], column_precisions[n]))
            # print no decimals (negative decimal indices permitted)
            else:
                array_to_print[m][n] = str(int(round(array[m, n], column_precisions[n])))

    # find the column lengths (cells with most characters)
    max_column_len = np.amax(np.vectorize(lambda cell: len(cell))(array_to_print), axis=0)

    print("")
    print("\\begin{tabular}{" + np.shape(array)[1]*"|l" + "|}\n", end="", sep="")
    print("\\hline")
    print((" & " * (np.shape(array)[1]-1) +" \\\\"))
    print("\\hline")
    for m in range(np.shape(array)[0]):
        for n in range(np.shape(array)[1]):
            print(("{:"+str(max_column_len[n])+"}").format(array_to_print[m][n]), end="", sep="")
            if (n != np.shape(array)[1]-1):
                print(" & ", end="", sep="")
            else:
                print(" \\\\\n", end="", sep="")
    print("\\hline")
    print("\end{tabular}")
    print("")
