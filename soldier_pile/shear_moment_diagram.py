import copy
import sys

from sympy import symbols
from sympy.solvers import solve
import numpy as np


def calculate_pressure(depth, pressure):
    z = symbols("z")
    equation = (pressure[1] - pressure[0]) / (depth[-1] - depth[0]) * z + pressure[0]
    pressure_list = []
    for Z in depth:
        sigma = equation.subs(z, Z)
        pressure_list.append(sigma)
    return pressure_list


class diagram:
    def __init__(self, depth, active_pressure, passive_pressure, water_pressure_active, water_pressure_passive,
                 surcharge):
        for i in range(len(depth), 0, -1):
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
        self.depth = depth
        self.active_pressure = active_pressure
        self.passive_pressure = passive_pressure
        self.water_pressure_active = water_pressure_active
        self.water_pressure_passive = water_pressure_passive
        self.surcharge = surcharge

    def base_calculate(self, delta_h=0.1):
        depth = self.depth
        active_pressure = self.active_pressure
        passive_pressure = self.passive_pressure
        water_pressure_active = self.water_pressure_active
        water_pressure_passive = self.water_pressure_passive
        surcharge = self.surcharge
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0
        sigma_active = []
        sigma_passive = []
        sigma_water_a = []
        sigma_water_p = []
        sigma_surcharge = []
        j = 0
        for depth_list in depth:
            depth[j] = [
                i / pow(10, delta_h_decimal) if i / pow(10, delta_h_decimal) <= depth[j][1] else depth[j][1]
                for i in
                range(depth_list[0], int((depth_list[1] + delta_h) * pow(10, delta_h_decimal)),
                      int(delta_h * pow(10, delta_h_decimal)))]
            active = calculate_pressure(depth[j], active_pressure[j])
            active_copy = copy.deepcopy(active)
            sigma_active.append(active_copy)
            active.clear()
            passive = calculate_pressure(depth[j], passive_pressure[j])
            passive_copy = copy.deepcopy(passive)
            sigma_passive.append(passive_copy)
            passive.clear()
            water_a = calculate_pressure(depth[j], water_pressure_active[j])
            water_copy_a = copy.deepcopy(water_a)
            sigma_water_a.append(water_copy_a)
            water_a.clear()
            water_p = calculate_pressure(depth[j], water_pressure_passive[j])
            water_copy_p = copy.deepcopy(water_p)
            sigma_water_p.append(water_copy_p)
            water_p.clear()
            j += 1
        sigma_active = np.array(sigma_active)
        sigma_passive = np.array(sigma_passive)
        sigma_water_a = np.array(sigma_water_a)
        sigma_water_p = np.array(sigma_water_p)
        sigma_final = sigma_active + sigma_water_a - sigma_passive - sigma_water_p
        return sigma_final
