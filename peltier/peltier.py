# Copyright Mika "AgenttiX" Mäki & Alpi Tolvanen, 2017
# Created for Tampere University of Technology course FYS-1010 Physics Laboratory 1


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

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
    def __init__(self, name, path, mass, heat_capacity, aluminium_area, insulator_thickness = 0, thermal_conductivity = 0):
        """
        This class holds the data of a single measurement
        :param path: path of measurement files
        """

        self.name = name
        self.mass = mass
        self.heat_capacity = heat_capacity

        self.aluminium_area = aluminium_area    #0.033 *0.032  # m^2
        self.insulator_thickness = insulator_thickness
        self.thermal_conductivity = thermal_conductivity
        self.not_air = (self.insulator_thickness != 0)

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

        # Check when the power is applied
        # The peak voltage appears to be a good point for it
        self.power_inp_max = self.power_inp.max()
        self.enable_index = np.where(self.power_inp == self.power_inp_max)[0][0]

        # Check when to end the measurement
        # The peak temperature of the cold side appears to be a good point for it
        self.temp_cold_max = self.temp_cold.max()
        self.stop_index = np.where(self.temp_cold == self.temp_cold_max)[0][0]

        # Computed vectors
        self.temp_diff = self.temp_hot - self.temp_cold
        self.power = self.current * self.voltage

        # Computed values
        self.temp_hot_start = np.mean(self.temp_hot[self.enable_index-11:self.enable_index-1])
        self.temp_cold_start = np.mean(self.temp_cold[self.enable_index-11:self.enable_index-1])
        self.temp_max = self.temp_hot.max()
        self.temp_min = self.temp_cold.min()
        self.peak_index = np.where(self.temp_hot == self.temp_max)[0][0]

        # Times
        self.time_total = self.time_vec[self.stop_index]
        self.dtime = self.time_vec[1]
        self.time_pump = self.time_vec[self.peak_index] - self.time_vec[self.enable_index]
        self.time_gen = self.time_vec[self.stop_index] - self.time_vec[self.peak_index]

        # Temperature differences
        self.dtemp_pump_hot = self.temp_max - self.temp_hot_start
        self.dtemp_pump_cold = self.temp_cold_start - self.temp_min
        self.dtemp_engine_hot = self.temp_max - self.temp_hot[self.stop_index]
        self.dtemp_engine_cold = self.temp_cold[self.stop_index] - self.temp_min

        # Transferred heat
        self.qhot_pump = self.heat(self.dtemp_pump_hot)
        self.qcold_pump = self.heat(self.dtemp_pump_cold)
        self.qhot_engine = self.heat(self.dtemp_engine_hot)
        self.qcold_engine = self.heat(self.dtemp_engine_cold)

        # Gives somewhat different results than the measurement software
        # self.power_inp_total = np.sum(self.power_inp) * self.dtime
        # self.power_gen_total = np.sum(self.power_gen) * self.dtime

        # Gives results close to those of the measurement software
        self.work_inp = np.trapz(self.power_inp, dx=self.dtime)
        self.work_gen = np.trapz(self.power_gen, dx=self.dtime)

        if (self.not_air):  # no air-insulator
            # Heat transfer speed through insulator,    assuming that outside surface is at room temperature,    calculated with equation 12 ((Q/t) = k * A *(dT)/x)
            self.heat_transfer_speed_hot  = thermal_conductivity * aluminium_area * (self.temp_hot - self.temp_hot_start)/self.insulator_thickness
            self.heat_transfer_speed_cold = thermal_conductivity * aluminium_area * (self.temp_cold_start - self.temp_cold)/self.insulator_thickness

            # Total leaked heat due to heat transfer                sum( (Q/t) *dt )
            self.heat_loss_pump_hot  = np.trapz(self.heat_transfer_speed_hot[self.enable_index : self.peak_index], dx=self.dtime)
            self.heat_loss_pump_cold = np.trapz(self.heat_transfer_speed_cold[self.enable_index : self.peak_index], dx=self.dtime)
            self.heat_loss_gen_hot   = np.trapz(self.heat_transfer_speed_hot[self.peak_index : self.stop_index], dx=self.dtime)
            self.heat_loss_gen_cold  = np.trapz(self.heat_transfer_speed_cold[self.peak_index : self.stop_index], dx=self.dtime)    # it is negative because more heat flows out

            # Esitmated Q_hot with regular resistance heater.       Assumed linear heat heat rise.
            # Quick summary of what has been done:   --   W_tot = Q_hot + Q_leak    --    Q_leak = 1/2 * k*A*dT_max/(x) * t    --   dT_max = Q_hot/(mc)
            self.Q_hot_resistor = self.work_inp / (1 + self.thermal_conductivity*self.aluminium_area*self.time_pump / ( 2*self.mass*self.heat_capacity*self.insulator_thickness ))


    def readfile(self, path, filename):
        """ Parses a file created by the DataStudio measurement software
        :param path: str of file path, should end with /
        :param filename: str of file name
        :return: data (Numpy array), title (str)
        """
        # The DataStudio software uses ISO-8859-1 encoding (especially for the degree sign in temperature files)
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
        print("Enable index", self.enable_index)
        print("End index:", self.stop_index)
        print("Measurement length (from the very beginning to the end index):", self.time_vec[self.stop_index])
        print()
        print("Start temperature (hot):", self.temp_hot_start)
        print("Start temperature (cold):", self.temp_cold_start)
        print("End temperature (hot):", self.temp_hot[self.stop_index])
        print("End temperature (cold)", self.temp_cold[self.stop_index])
        print()
        print("Max temperature", self.temp_max)
        print("Min temperature", self.temp_min)
        print()
        print("Heat pump")
        print("Energy input:", self.work_inp)
        print("Q_hot", self.qhot_pump)
        print("Q_cold", self.qcold_pump)
        print("Q_cold + W", self.qcold_pump + self.work_inp)
        print("E_lost", self.qcold_pump + self.work_inp - self.qhot_pump)
        print("Heat transfer coefficient / coefficient of performance / lämpökerroin hot", self.qhot_pump / self.work_inp)
        print("Heat transfer coefficient / coefficient of performance / lämpökerroin cold", self.qcold_pump / self.work_inp)
        if (self.not_air):
            print("Heat transfer through insulator, hot side", self.heat_loss_pump_hot)
            print("Heat transfer through insulator, cold side", self.heat_loss_pump_cold)
            print("Estimated Q_hot with resistor", self.Q_hot_resistor)
        #
        # I think it should be defined for Q_hot too. Yep, TODO that
        # Also calculate heatloss due to conduction TODO remove these comments when ready
        # Todo implement resistive heater calculations
        print()
        print("Heat engine")
        print("Energy generated:", self.work_gen)
        print("Q_hot", self.qhot_engine)
        print("Q_cold", self.qcold_engine)
        print("Q_hot - Q_cold", self.qhot_engine - self.qcold_engine)
        print("\"Heat transfer efficiency\" (%)", self.work_gen / (self.qhot_engine - self.qcold_engine) * 100)
        print("Efficiency e", self.work_gen / self.qhot_engine)
        print("Ideal efficiency", 1 - (self.qcold_engine / self.qhot_engine))
        if (self.not_air):
            print("Heat transfer through insulator, hot side", self.heat_loss_gen_hot)
            print("Heat transfer through insulator, cold side", self.heat_loss_gen_cold)
        print()
        # About the efficiency of peltier elements (#telok@IRCnet, 2016-07-27)
        # 19:10 < AgenttiX> Oletteko kokeilleet TECin ohjaamista Arduinolla? Toimisiko tämä kytkentä? http://garagelab.com/profiles/blogs/how-to-use-a-peltier-with-arduino
        # --
        # 20:21 <@hrst> Ei toimi. Peltieriä ei voi ohjata PWM:llä.
        # 20:22 <@hrst> Hyötysuhde on PWM:llä paska, mikä on ongelma koska se on muutenkin liian paska, ja sen lisäksi se hajoaa mekaaniseen värähtelyyn ennemmin tai myöhemmin.
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
aluminium_area = 0.033 *0.032  # x*y (m^2)
thickness_finnfoam = 0.00942  # x (m)
thickness_wood = 0.0088       # x (m)
thermal_conductivity_finnfoam = 0.033 # k (W/(m*K))         (http://www.finnfoam.fi)
thermal_conductivity_wood = 0.16      # k (W/(m*K))   (oak) (http://www.engineeringtoolbox.com/)


# Initialise measurements
finnfoam = Measurement("Finnfoam", "Data/Finnfoam/", mass, heat_capacity, aluminium_area, thickness_finnfoam, thermal_conductivity_finnfoam)
wood = Measurement("Wood", "Data/Wood/", mass, heat_capacity, aluminium_area, thickness_wood, thermal_conductivity_wood)
air = Measurement("Air", "Data/Air/", mass, heat_capacity, aluminium_area)

finnfoam.print()
wood.print()
air.print()

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
plot_temp_diff = plot_rgb("Temperature difference", finnfoam.temp_diff, wood.temp_diff, air.temp_diff)


# Main loop
app.exec_()
