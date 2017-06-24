import numpy as np


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
    MSE = (1/(y_mat.size)) * np.sum(np.multiply((y_mat/x_mat-micro),(y_mat/x_mat-micro)))
    err = np.sqrt(MSE)

    return micro, err