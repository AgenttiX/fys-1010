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
    def __init__(self, name, path, mass, heat_capacity, aluminium_area, insulator_thickness=0.0, thermal_conductivity=0.0):
        """
        This class holds the data of a single measurement
        :param path: path of measurement files
        """

        self.name = name
        self.mass = mass
        self.heat_capacity = heat_capacity

        self.aluminium_area = aluminium_area
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
        self.temp_cold_orig = self.readfile(path, "Temperature1.txt")[0][:, 1]
        self.temp_hot_orig = self.readfile(path, "Temperature2.txt")[0][:, 1]
        self.voltage = self.readfile(path, "Voltage.txt")[0][:, 1]

        # Check when the power is applied
        # The peak voltage appears to be a good point for it
        self.power_inp_max = self.power_inp.max()
        self.enable_index = np.where(self.power_inp == self.power_inp_max)[0][0]
        # Gets minimum of consecutive elements of power vector
        self.disable_index = np.argmin(np.ediff1d(self.power_inp))+1

        # Computed values
        self.temp_hot_start = np.mean(self.temp_hot_orig[self.enable_index - 11:self.enable_index - 1])
        self.temp_cold_start = np.mean(self.temp_cold_orig[self.enable_index - 11:self.enable_index - 1])
        self.temp_start = (self.temp_hot_start + self.temp_cold_start)/2
        # Normalise temperatures to same level
        self.temp_hot = self.temp_hot_orig + (self.temp_cold_start - self.temp_hot_start)/2
        self.temp_cold = self.temp_cold_orig + (self.temp_hot_start - self.temp_cold_start)/2

        self.temp_max = self.temp_hot.max()
        self.temp_min = self.temp_cold.min()
        # Is not exactly the same as self.disable_index
        self.temp_peak_index = np.where(self.temp_hot == self.temp_max)[0][0]

        # Check when to end the measurement
        # The peak temperature of the cold side appears to be a good point for it
        self.temp_cold_max = self.temp_cold.max()
        self.stop_index = np.where(self.temp_cold == self.temp_cold_max)[0][0]

        # Computed vectors
        self.temp_diff = self.temp_hot - self.temp_cold
        self.power = self.current * self.voltage

        # Times
        self.time_total = self.time_vec[self.stop_index]
        self.dtime = self.time_vec[1]
        self.time_pump = self.time_vec[self.temp_peak_index] - self.time_vec[self.enable_index]
        self.time_gen = self.time_vec[self.stop_index] - self.time_vec[self.temp_peak_index]

        # Temperature differences
        self.dtemp_pump_hot = self.temp_max - self.temp_start
        self.dtemp_pump_cold = self.temp_start - self.temp_min
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

        # We are not considering case:air in which there is no insulation
        if self.not_air:
            # Heat transfer speed through insulator, assuming that outside surface is at room temperature
            self.heat_transfer_speed_hot  = thermal_conductivity * aluminium_area * \
                                            (self.temp_hot - self.temp_start)/self.insulator_thickness
            self.heat_transfer_speed_cold = thermal_conductivity * aluminium_area * \
                                            (self.temp_start - self.temp_cold)/self.insulator_thickness

            # Total leaked heat due to heat transfer
            self.heat_loss_pump_hot  = np.trapz(self.heat_transfer_speed_hot[self.enable_index : self.temp_peak_index], dx=self.dtime)
            self.heat_loss_pump_cold = np.trapz(self.heat_transfer_speed_cold[self.enable_index : self.temp_peak_index], dx=self.dtime)
            self.heat_loss_gen_hot   = np.trapz(self.heat_transfer_speed_hot[self.temp_peak_index : self.stop_index], dx=self.dtime)
            self.heat_loss_gen_cold  = np.trapz(self.heat_transfer_speed_cold[self.temp_peak_index : self.stop_index], dx=self.dtime)   # it's negative because more heat flows out

            # Estimated Q_hot with regular resistance heater. Assumed linear heat heat rise.
            self.qhot_resistor = self.work_inp / (1 + self.thermal_conductivity * self.aluminium_area * self.time_pump / (2 * self.mass * self.heat_capacity * self.insulator_thickness))
        else:   # Case: air and no insulation
            self.qhot_resistor = self.work_inp

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
        print("Start temperature (mean):", self.temp_start)
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
        print("Coefficient of performance COP_hot", self.qhot_pump / self.work_inp)
        print("Coefficient of performance COP_cold", self.qcold_pump / self.work_inp)
        print("Ideal COP_hot with the setup", self.qhot_pump/(self.qhot_pump-self.qcold_pump))
        print("Ideal COP_cold with the setup", self.qcold_pump / (self.qhot_pump - self.qcold_pump))
        print("Ideal Carnot COP_hot", (self.temp_max+273.15)/(self.temp_max-self.temp_min))
        print("Ideal Carnot COP_cold", (self.temp_min+273.15)/(self.temp_max-self.temp_min))

        if self.not_air:
            print("Heat transfer through insulator, hot side", self.heat_loss_pump_hot)
            print("Heat transfer through insulator, cold side", self.heat_loss_pump_cold)
            print("Estimated Q_hot with resistor", self.qhot_resistor)
        else:
            print("Estimated Q_hot with resistor (=energy input)", self.qhot_resistor)
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
        print("E_lost", -self.qcold_engine - self.work_gen + self.qhot_engine)
        print("\"Heat transfer efficiency\" (%)", self.work_gen / (self.qhot_engine - self.qcold_engine) * 100)
        print("Efficiency e", self.work_gen / self.qhot_engine)
        print("Ideal efficiency with the setup", 1 - (self.qcold_engine / self.qhot_engine))
        print("Ideal Carnot efficiency", (self.temp_max-self.temp_min)/(self.temp_max+273.15))
        if self.not_air:
            print("Heat transfer through insulator, hot side", self.heat_loss_gen_hot)
            print("Heat transfer through insulator, cold side", self.heat_loss_gen_cold)
        print()
        print("Total efficiency of cycle", self.work_gen/self.work_inp)
        # About the efficiency of peltier elements (#telok@IRCnet, 2016-07-27)
        # 19:10 < AgenttiX> Oletteko kokeilleet TECin ohjaamista Arduinolla? Toimisiko tämä kytkentä? http://garagelab.com/profiles/blogs/how-to-use-a-peltier-with-arduino
        # --
        # 20:21 <@hrst> Ei toimi. Peltieriä ei voi ohjata PWM:llä.
        # 20:22 <@hrst> Hyötysuhde on PWM:llä paska, mikä on ongelma koska se on muutenkin liian paska, ja sen lisäksi se hajoaa mekaaniseen värähtelyyn ennemmin tai myöhemmin.
        print("-----\n")


class Main:
    def __init__(self):
        # Constants
        mass = 0.019                            # m (kg)
        heat_capacity = 900                     # c (kg * degC)
        aluminium_area = 0.033 * 0.032           # x*y (m^2)
        thickness_finnfoam = 0.00942            # x (m)
        thickness_wood = 0.0088                 # x (m)
        thermal_conductivity_finnfoam = 0.04   # k (W/(m*K)
        thermal_conductivity_wood = 0.16        # k (W/(m*K))   (oak) (http://www.engineeringtoolbox.com/)


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

        self.red = pg.mkPen((255, 0, 0), width=1.5)
        self.green = pg.mkPen((0, 255, 0), width=1.5)
        self.blue = pg.mkPen((0, 0, 255), width=1.5)

        self.win = pg.GraphicsWindow(title="Peltier (Lämpövoimakoneet)")


        plot_power_inp = self.plot_bgr("", finnfoam.power_inp, wood.power_inp, air.power_inp, "P", "w")  # Power input
        plot_power_gen = self.plot_bgr("", finnfoam.power_gen, wood.power_gen, air.power_gen,  "P", "w")  # Power generated

        self.win.nextRow()

        plot_temp_hot = self.plot_bgr("", finnfoam.temp_hot, wood.temp_hot, air.temp_hot, "T", "°C") # Temperature of hot side
        plot_temp_cold = self.plot_bgr("", finnfoam.temp_cold, wood.temp_cold, air.temp_cold, "T", "°C") # Temperature of cold side

        self.win.nextRow()

        #plot_power = plot_rgb("Power", finnfoam.power, wood.power, air.power, "P", "w")
        plot_finnfoam_both = self.plot_two("", finnfoam.temp_hot, finnfoam.temp_cold, "T", "°C", "Lämmin puoli", "Kylmä puoli" )  # Temperature difference of both sides
        plot_temp_diff = self.plot_bgr("", finnfoam.temp_diff, wood.temp_diff, air.temp_diff, "ΔT", "°C")  #Temperature difference

        self.win.resize(1000, 1000)

        # Main loop
        app.exec_()

    def plot_bgr(self, title, first, second, third, ylabel="", yunit="", offset=0, name_first="Finnfoam", name_second="Puu",
                 name_third="Ilma"):
        # for reference octave uses order [blue, green, red] for coloring, we use that order to get finnfoam to be blue
        plot = self.win.addPlot(title=title)
        plot.addLegend(offset=(-1, 1))
        plot.plot(np.arange(offset, first.size + offset) / 10, first, pen=self.blue, name=name_first)
        plot.plot(np.arange(offset, second.size + offset) / 10, second, pen=self.green, name=name_second)
        plot.plot(np.arange(offset, third.size + offset) / 10, third, pen=self.red, name=name_third)
        plot.setLabel("left", ylabel, yunit)
        plot.setLabel("bottom", "t (s)")
        plot.setRange(xRange=[0, 400])

        return plot

    def plot_two(self, title, first, second, ylabel="", yunit="", name_first="", name_second="", offset=0):
        light_blue = pg.mkPen((80, 80, 255), width=1.5)
        dark_blue = pg.mkPen((0, 0, 160), width=1.5)

        plot = self.win.addPlot(title=title)
        plot.addLegend(offset=(-1, 1))
        plot.plot(np.arange(offset, first.size + offset) / 10, first, pen=light_blue, name=name_first)
        plot.plot(np.arange(offset, second.size + offset) / 10, second, pen=dark_blue, name=name_second)
        plot.setLabel("left", ylabel, yunit)
        plot.setLabel("bottom", "t (s)")
        plot.setRange(xRange=[0, 400])

        return plot


def main():
    Main()

main()
