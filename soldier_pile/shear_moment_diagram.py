import copy
import sys
import json

from sympy import symbols
from sympy.solvers import solve
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout
import plotly
import json2html


def calculator_depth(depth, delta_h, delta_h_decimal, soil_pressure, water_pressure):
    j = 0
    sigma_soil = []
    sigma_water = []
    for depth_list in depth:
        depth[j] = [
            i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <=
                                            depth[j][
                                                1] else depth[j][
                1]
            for i in
            range(0, int((depth_list[1] + delta_h - depth_list[0]) * pow(10, delta_h_decimal)),
                  int(delta_h * pow(10, delta_h_decimal)))]

        soil = calculate_pressure(depth[j], soil_pressure[j])
        soil_copy = np.array(copy.deepcopy(soil))
        sigma_soil.append(soil_copy)
        soil.clear()
        water = calculate_pressure(depth[j], water_pressure[j])
        water_copy = np.array(copy.deepcopy(water))
        sigma_water.append(water_copy)
        water.clear()
        j += 1
    # edit depth for plot.
    for i in range(1, len(depth)):
        for j in range(len(depth[i])):
            depth[i][j] += depth[i - 1][-1]
    return depth, sigma_soil, sigma_water


def calculate_pressure(depth, pressure):
    z = symbols("z")
    try:
        equation = (pressure[1] - pressure[0]) / (depth[-1] - depth[0]) * z + pressure[0]
    except:
        equation = 0
    pressure_list = []
    for Z in depth:
        try:
            sigma = equation.subs(z, Z)
        except:
            sigma = 0
        pressure_list.append(sigma)
    return pressure_list


class diagram:
    def __init__(self, unit_system, surcharge_pressure, surcharge_depth, depth_active, depth_passive, active_pressure,
                 passive_pressure,
                 water_pressure_active,
                 water_pressure_passive):
        self.unit_system = unit_system

        for i in range(len(depth_active), 0, -1):
            try:
                a = depth_passive[i]
            except:
                depth_passive.insert(-i, [0, 0])
            try:
                a = passive_pressure[i]
            except:
                passive_pressure.insert(-i, [0, 0])
            try:
                a = water_pressure_active[i]
            except:
                water_pressure_active.insert(-i, [0, 0])
            try:
                a = water_pressure_passive[i]
            except:
                water_pressure_passive.insert(-i, [0, 0])

            # surcharge must be checked also.
        self.depth_active = depth_active
        self.depth_passive = depth_passive
        self.active_pressure = active_pressure
        self.passive_pressure = passive_pressure
        self.water_pressure_active = water_pressure_active
        self.water_pressure_passive = water_pressure_passive
        self.surcharge_pressure = surcharge_pressure
        self.surcharge_depth = surcharge_depth

    def base_calculate(self, delta_h=0.1):
        depth_active = self.depth_active
        depth_passive = self.depth_passive
        active_pressure = self.active_pressure
        passive_pressure = self.passive_pressure
        water_pressure_active = self.water_pressure_active
        water_pressure_passive = self.water_pressure_passive
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        depth_active, sigma_active, sigma_water_a = calculator_depth(depth_active, delta_h, delta_h_decimal,
                                                                     active_pressure,
                                                                     water_pressure_active)
        depth_passive, sigma_passive, sigma_water_p = calculator_depth(depth_passive, delta_h, delta_h_decimal,
                                                                       passive_pressure,
                                                                       water_pressure_passive)
        # reshape passive parameters to active shape. must have same shapes.( for zero values. )
        for z in range(len(depth_passive)):
            if depth_passive[z] == [0, 0]:
                copy_list = copy.deepcopy(depth_active[z])
                depth_passive[z] = copy_list
                for i in range(len(copy_list)):
                    depth_passive[z][i] = 0
        for z in range(len(sigma_passive)):
            if list(sigma_passive[z]) == [0, 0]:
                copy_list = copy.deepcopy(sigma_active[z])
                sigma_passive[z] = copy_list
                for i in range(len(sigma_active[z])):
                    sigma_passive[z][i] = 0
        for z in range(len(sigma_water_p)):
            if list(sigma_water_p[z]) == [0, 0]:
                copy_list = copy.deepcopy(sigma_water_a[z])
                sigma_water_p[z] = copy_list
                for i in range(len(sigma_water_a[z])):
                    sigma_water_p[z][i] = 0
        sigma_active = np.array(sigma_active, dtype="object")
        sigma_passive = np.array(sigma_passive, dtype="object")
        sigma_water_a = np.array(sigma_water_a, dtype="object")
        sigma_water_p = np.array(sigma_water_p, dtype="object")
        sigma_final = sigma_active + sigma_water_a - sigma_passive - sigma_water_p
        return depth_active, sigma_final

    def load_diagram(self):
        unit_system = self.unit_system
        if unit_system == "us":
            load_unit = "lb/m"
            lenght_unit = "ft"
        else:
            load_unit = "N/m"
            lenght_unit = "m"
        surcharge_pressure = self.surcharge_pressure
        surcharge_depth = self.surcharge_depth
        depth, sigma_final = self.base_calculate()
        edited_depth = depth[0]
        edited_sigma = list(sigma_final[0])
        for i in depth[1:]:
            edited_depth += i
        edited_depth[0] = 0.0
        edited_depth = np.array(edited_depth)

        for i in sigma_final[1:]:
            edited_sigma += list(i)
        edited_sigma[0] = 0.0
        for i in range(len(edited_sigma)):
            edited_sigma[i] = float(edited_sigma[i])

        for i in range(len(surcharge_pressure)):
            edited_sigma[i] += surcharge_pressure[i]
        edited_sigma = np.array(edited_sigma)

        plot = px.line(y=edited_depth, x=edited_sigma, color_discrete_sequence=["#595959"]).update_layout(
            xaxis_title=f"Ϭh ({load_unit})",
            yaxis_title=f"Z ({lenght_unit})",
            xaxis={"side": "top",
                   "zeroline": True,
                   "mirror": "ticks",
                   "zerolinecolor": "#969696",
                   "zerolinewidth": 4, },
            yaxis={"zeroline": True,
                   "mirror": "ticks",
                   "zerolinecolor": "#969696",
                   "zerolinewidth": 4}
        )
        plot['layout']['yaxis']['autorange'] = "reversed"

        # plot.write_html("output.html",
        #                 full_html=False,
        #                 include_plotlyjs='cdn')
        plot.show()
        return plot
