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
from shear_moment_diagram import plotter


def deflection_calculator(delta_h, delta_h_decimal, depth, moment, PoF, c, hr, final_depth):
    """
    :param final_depth:
    :param delta_h: for separation
    :param delta_h_decimal: number of decimal
    :param depth: unit -> ft or m
    :param moment: unit -> lb-ft or N-m
    :param PoF: point of fixity
    :param c: middle of BO
    :param hr: retaining height
    :return: deflection * EI
    """
    # calculate delta C/B
    depth_copy = copy.deepcopy(depth)
    c_point = list(depth_copy).index(round(c + hr, delta_h_decimal))
    PoF_point = list(depth_copy).index(round(PoF + hr, delta_h_decimal))
    B = depth[PoF_point]
    C = depth[c_point]
    BC = round(C - B, delta_h_decimal)

    BC_list = [
        i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <=
                                        BC else BC for i in
        range(0, int((BC + delta_h) * pow(10, delta_h_decimal)),
              int(delta_h * pow(10, delta_h_decimal)))]
    Bc = np.array(BC_list)
    area_cb = abs(spi.simpson(moment[c_point:PoF_point:-1], depth[c_point:PoF_point:-1]))
    X_cb = abs(spi.simpson(moment[c_point:PoF_point:-1] * Bc[:-1],
                           depth[c_point:PoF_point:-1])) / area_cb
    delta_cb = area_cb * X_cb  # unit : if us --> lb - ft^3. if metric --> N - m^3
    # delta_cb = abs(spi.simpson(moment[c_point:PoF_point:-1] * Bc[:-1],
    #                            depth[c_point:PoF_point:-1]))

    # calculate all deflections
    deflection3 = []
    deflection2 = []
    deflection1 = []
    # create 3 ranges

    # range 3 --> AB --> retaining height
    A_point = 0
    A = depth[A_point]
    AB_list = [
        i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <=
                                        hr + PoF else hr + PoF for i in
        range(0, int((hr + PoF + delta_h) * pow(10, delta_h_decimal)),
              int(delta_h * pow(10, delta_h_decimal)))]
    AB = np.array(AB_list)
    AB_copy = copy.deepcopy(AB)
    x_point_moment_last = copy.deepcopy(PoF_point)
    for x in AB:
        x_point = list(AB_copy).index(x)
        if x != 0:
            delta_xb = abs(spi.simpson(moment[x_point_moment_last:PoF_point] * AB[:x_point],
                                       depth[x_point_moment_last:PoF_point]))
        else:
            delta_xb = 0.

        x_point_moment_last -= 1
        deflection3.append(delta_xb)

    # # range 2 and 3 --> BC and CO ==> BO
    # x_point_moment_start = copy.deepcopy(PoF_point)
    # end_point = copy.deepcopy(x_point_moment_start)
    # O_point = -1  # last index
    # O = depth[O_point]
    # OB = round(O - B, delta_h_decimal)
    # OC = OB - BC
    # OC_list = [i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <=
    #
    #                                            OC else OC for i in
    #            range(0, int((OC + delta_h) * pow(10, delta_h_decimal)),
    #                  int(delta_h * pow(10, delta_h_decimal)))]
    # OB_list = [
    #     i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <=
    #
    #                                     OB else OB for i in
    #     range(0, int((OB + delta_h) * pow(10, delta_h_decimal)),
    #           int(delta_h * pow(10, delta_h_decimal)))]
    # BO = np.array(OB_list)
    # BO_copy = copy.deepcopy(BO)
    # for x in BO:
    #     x_point = list(BO_copy).index(x)
    #     if x != 0.0:
    #         delta_xb = abs(spi.simpson(moment[end_point:x_point_moment_start] * BO[:x_point],
    #                                    depth[end_point:x_point_moment_start]))
    #     else:
    #         delta_xb = 0.
    #
    #     x_point_moment_start += 1
    #     if round(x, delta_h_decimal) <= BC:
    #         deflection2.append(delta_xb)
    #     else:
    #         delta_copy = copy.deepcopy(delta_xb)
    #         deflection1.append(delta_copy)

    for i in range(len(deflection3)):
        deflection3[i] = -(deflection3[i] + delta_cb * AB_list[i] / BC)
    # del deflection3[0]

    # for i in range(len(deflection2)):
    #     deflection2[i] = - deflection2[i] + delta_cb * BC_list[i] / BC
    #
    # for i in range(len(deflection1)):
    #     deflection1[i] = -(deflection1[i] - delta_cb * (OC_list[i] + BC) / BC)
    deflection = [np.array(deflection1), 0]
    deflection = np.array(deflection, dtype="object")
    # deflection_total = deflection3[::-1] + deflection2 + deflection1
    deflection_total = deflection3[::-1] + [0]
    deflection_depth = AB_list + [final_depth]
    plot = plotter(deflection_depth, deflection_total, "deflection", "Z", "in", "ft")
    return deflection_total
