import copy
import sys
import json

from sympy import symbols
from sympy.solvers import solve
import numpy as np
import scipy.integrate as spi

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout


def deflection_calculator(depth, moment, PoF, c):
    # calculate delta C/B
    c_point = depth.index(c)
    PoF_point = depth.index(PoF)
    # area = abs(spi.simpson(moment[c_point:PoF_point], depth[c_point:PoF_point]))
    # X = abs(spi.simpson(moment[c_point:PoF_point] * depth[c_point:PoF_point], depth[c_point:PoF_point])) / area
    # delta_cb = area * X
    delta_cb = abs(spi.simpson(moment[c_point:PoF_point] * depth[c_point:PoF_point], depth[c_point:PoF_point]))
    return delta_cb
