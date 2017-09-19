import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
Make a histogram using csv input
"""

from pandas import *
from pandas.io.parsers import read_csv

path='out.csv'
fec = read_csv(path, index_col=False)
print(fec.describe())

distro = 'sizedistro.png'

plt.figure();
fec.plot.hist()
