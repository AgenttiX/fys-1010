# Copyright Mika "AgenttiX" Mäki & Alpi Tolvanen, 2017
# Created for Tampere University of Technology course FYS-1010 Physics Laboratory 1


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import numpy as np

# PyQtGraph can be found from Ubuntu repositories as python3-pyqtgraph
# http://www.pyqtgraph.org/
import pyqtgraph as pg


class Measurement:
    def __init__(self, name, path, mass, heat_capacity):
        """
        This class holds the data of a single measurement
        :param path: path of measurement files
        """

        self.name = name
        self.mass = mass
        self.heat_capacity = heat_capacity

        # Load data from files
        currentdata = self.readfile(path, "Current.txt")[0]

        # Numpy arrays for data vectors
        self.time_vec = currentdata[:, 0]
        self.current = currentdata[:, 1]
        self.power_inp = self.readfile(path, "Power.txt")[0][:, 1]
        self.power_gen = self.readfile(path, "PowerGenerated.txt")[0][:, 1]
        self.qcold_vec = self.readfile(path, "Qcold.txt")[0][:, 1]
        self.qcold_pump_vec = self.readfile(path, "Qcold_pump.txt")[0][:, 1]
        self.qhot_vec = self.readfile(path, "Qhot.txt")[0][:, 1]
        self.qhot_pump_vec = self.readfile(path, "Qhot_pump.txt")[0][:, 1]
        self.tc_initial = self.readfile(path, "Tc_initial.txt")[0][:, 1]
        self.temp_cold = self.readfile(path, "Temperature1.txt")[0][:, 1]
        self.temp_hot = self.readfile(path, "Temperature2.txt")[0][:, 1]
        self.voltage = self.readfile(path, "Voltage.txt")[0][:, 1]

        # Computed values
        self.temp_max = self.temp_hot.max()
        self.temp_min = self.temp_cold.min()
        self.time = self.time_vec[-1]

        self.dtemp_pump_hot = self.temp_max - self.temp_hot[0]
        self.dtemp_pump_cold = self.temp_cold[0] - self.temp_min
        self.dtemp_engine_hot = self.temp_max - self.temp_hot[-1]
        self.dtemp_engine_cold = self.temp_cold[-1] - self.temp_min

        self.qhot_pump = self.heat(self.dtemp_pump_hot)
        self.qcold_pump = self.heat(self.dtemp_pump_cold)
        self.qhot_engine = self.heat(self.dtemp_engine_hot)
        self.qcold_engine = self.heat(self.dtemp_engine_cold)

        # Computed vectors
        self.temp_diff = self.temp_hot - self.temp_cold
        self.power = self.current * self.voltage

    def readfile(self, path, filename):
        """ Parses a file created by the DataStudio measurement software
        :param path: str of file path, should end with /
        :param filename: str of file name
        :return: data (Numpy array), title (str)
        """
        # The DataStudio software uses ISO-8859-1 encoding (for the degree sign in temperature files)
        file = open(path + filename, encoding="iso-8859-1")
        rowlist = file.readlines()

        title = rowlist[0].strip("\n")
        labels = rowlist[1].strip("\n").split(sep="\t")

        data = np.zeros((len(rowlist)-2, 2))

        for i in range(2, len(rowlist)):
            columns = rowlist[i].split(sep="\t")
            data[i-2, 0] = float(columns[0].replace(",", "."))
            data[i-2, 1] = float(columns[1].replace(",", "."))

        return data, title, labels

    def heat(self, delta_temp):
        return self.heat_capacity * self.mass * delta_temp

    def print(self):
        print("-----", self.name, "-----")
        print("Start temperature (hot):", self.temp_hot[0])
        print("Start temperature (cold):", self.temp_cold[0])
        print("End temperature (hot):", self.temp_hot[-1])
        print("End temperature (cold)", self.temp_cold[-1])
        print()
        print("Max temperature", self.temp_max)
        print("Min temperature", self.temp_min)
        print()
        print("Heat pump")
        print("Q_hot", self.qhot_pump)
        print("Q_cold", self.qcold_pump)
        print()
        print("Heat engine")
        print("Q_hot", self.qhot_engine)
        print("Q_cold", self.qcold_engine)
        print("-----\n")


def plot_rgb(title, first, second, third):

    plot = win.addPlot(title=title)
    plot.plot(first, pen=red)
    plot.plot(second, pen=green)
    plot.plot(third, pen=blue)

    return plot


# Constants
mass = 0.019            # m (kg)
heat_capacity = 900    # c (kg * degC)

# Initialise measurements
finnfoam = Measurement("Finnfoam", "Data/Finnfoam/", mass, heat_capacity)
air = Measurement("Air", "Data/Air/", mass, heat_capacity)
wood = Measurement("Wood", "Data/Wood/", mass, heat_capacity)


finnfoam.print()
air.print()
wood.print()


# PyQtGraph initialisation
app = pg.mkQApp()
pg.setConfigOptions(antialias=True, background="w", foreground="k")

red = pg.mkPen((255, 0, 0), width=1.5)
green = pg.mkPen((0, 255, 0), width=1.5)
blue = pg.mkPen((0, 0, 255), width=1.5)

win = pg.GraphicsWindow(title="Peltier (Lämpövoimakoneet)")


plot_power_inp = plot_rgb("Power input", finnfoam.power_inp, wood.power_inp, air.power_inp)
plot_power_gen = plot_rgb("Power generated", finnfoam.power_gen, wood.power_gen, air.power_gen)

win.nextRow()

plot_temp_hot = plot_rgb("Temperature of hot side", finnfoam.temp_hot, wood.temp_hot, air.temp_hot)
plot_temp_cold = plot_rgb("Temperature of cold side", finnfoam.temp_cold, wood.temp_cold, air.temp_cold)

win.nextRow()

plot_power = plot_rgb("Power", finnfoam.power, wood.power, air.power)


# Main loop
app.exec_()
