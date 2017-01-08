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


import csv
import numpy as np


def readfile(filepath):
    """ Parses a file created by the measurement software
    :param filepath: str of the file path
    :return: np.array, np.array
    """
    rawfile = open(filepath)
    file = csv.reader(rawfile, delimiter="\t")
    datalist = []
    for row in file:
        datalist.append(row)

    title = datalist[0][0]
    labels = datalist[1]

    data = np.zeros((len(datalist)-2, 2))

    for i, row in enumerate(datalist):
        if i <= 1:
            continue
        for j, cell in enumerate(row):
            data[i-2, j] = float(cell.replace(",", "."))

    return data, title, labels

file1 = readfile("Data/Air/Power.txt")

print(file1)
