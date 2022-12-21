from inputs import input_values

from surchargeLoad import surcharge
from shoring_cantilever import calculate_force_and_arm, control_solution, cantilever_soldier_pile, put_D_in_list, \
    multiple_pressure_pile_spacing
from shear_moment_diagram import diagram

import sys

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")

from Passive_Active.active_passive import active_passive
from Force.force import moment_calculator

import copy
import sys
from sympy import symbols
from sympy.solvers import solve
import numpy as np


def main_unrestrained_shoring(inputs):
    D = symbols("D")

    [number_of_project, unit_system, calculation_type, delta_h, h_active, h_passive, retaining_height, surcharge_depth,
     water_active,
     water_passive,
     number_of_layer_active,
     number_of_layer_passive, surcharge_type, surcharge_inputs, soil_properties_active, soil_properties_passive, FS,
     Pile_spacing, allowable_deflection, Fy, E, selected_design_sections] = inputs.values()

    for project in range(number_of_project):
        calculation_type = calculation_type[project]
        delta_h = delta_h[project]
        h_active = h_active[project]
        h_passive = h_passive[project]
        surcharge_depth = surcharge_depth[project]
        water_active = water_active[project]
        water_passive = water_passive[project]
        number_of_layer_active = number_of_layer_active[project]
        number_of_layer_passive = number_of_layer_passive[project]
        surcharge_type = surcharge_type[project]
        FS = FS[project]
        Pile_spacing = Pile_spacing[project]
        Fy = Fy[project]
        if calculation_type == "Auto":
            [gama_active, phi_active, theory_active, state_active, beta_active, omega_active,
             delta_active
             ] = soil_properties_active[project]
            [gama_passive, phi_passive, theory_passive, state_passive, beta_passive, omega_passive,
             delta_passive
             ] = soil_properties_passive[project]
            main_active = active_passive(h_active, water_active)
            soil_active, water_active, depth_list_active, h_water_active = main_active.pressure_calculator(
                number_of_layer=number_of_layer_active,
                gama=gama_active,
                phi=phi_active,
                theory=theory_active,
                state="active",
                unit_system=unit_system,
                beta=beta_active,
                omega=omega_active,
                delta=delta_active)

            force_soil_active, arm_soil_active = calculate_force_and_arm(soil_active, water_active, main_active)

            main_passive = active_passive(h_passive, water_passive)
            soil_passive, water_passive, depth_list_passive, h_water_passive = main_passive.pressure_calculator(
                number_of_layer=number_of_layer_passive,
                gama=gama_passive,
                phi=phi_passive,
                theory=theory_passive,
                state="passive",
                unit_system=unit_system,
                beta=beta_passive,
                omega=omega_passive,
                delta=delta_passive)

            force_soil_passive, arm_soil_passive = calculate_force_and_arm(soil_passive, water_passive, main_passive)


        else:
            EFPa = soil_properties_active[project]
            EFPp = soil_properties_passive[project]

        main_surcharge = surcharge(unit_system, surcharge_depth, delta_h)

        if surcharge_type == "uniform":
            [q] = surcharge_inputs[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.uniform(q)
        elif surcharge_type == "Point Load":
            [q, l1, teta] = surcharge_inputs[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.point_load(q, l1, teta)

        elif surcharge_type == "Line Load":
            [q, l1] = surcharge_inputs[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.line_load(q, l1)
        else:  # strip load
            [q, l1, l2] = surcharge_inputs[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.strip_load(q, l1, l2)

        error, d0, d_final, y0, M_max, s_required, second_D_zero = cantilever_soldier_pile(unit_system, h_active,
                                                                                           surcharge_force,
                                                                                           surcharge_arm,
                                                                                           surcharge_depth,
                                                                                           force_soil_active,
                                                                                           force_soil_passive,
                                                                                           arm_soil_active,
                                                                                           arm_soil_passive, FS,
                                                                                           Pile_spacing,
                                                                                           Fy)
        depth_list_active[-1][-1] = depth_list_active[-1][-1].subs(D, second_D_zero)
        depth_list_passive[-1][-1] = depth_list_passive[-1][-1].subs(D, second_D_zero)

        soil_active = put_D_in_list(soil_active, second_D_zero)
        soil_passive = put_D_in_list(soil_passive, second_D_zero)
        water_active = put_D_in_list(water_active, second_D_zero)
        water_passive = put_D_in_list(water_passive, second_D_zero)

        surcharge_pressure = multiple_pressure_pile_spacing(np.array([surcharge_pressure]), Pile_spacing)
        soil_active = multiple_pressure_pile_spacing(soil_active, Pile_spacing)
        soil_passive = multiple_pressure_pile_spacing(soil_passive, Pile_spacing)
        water_active = multiple_pressure_pile_spacing(water_active, Pile_spacing)
        water_passive = multiple_pressure_pile_spacing(water_passive, Pile_spacing)

        main_diagram = diagram("us", surcharge_pressure[0], surcharge_depth, depth_list_active, depth_list_passive,
                               soil_active,
                               soil_passive, water_active,
                               water_passive)

        depth, sigma = main_diagram.base_calculate(delta_h)
        load_diagram = main_diagram.load_diagram(depth, sigma)
        shear_diagram, shear_values = main_diagram.shear_diagram(depth, sigma)
        moment_diagram, moment_values = main_diagram.moment_diagram(depth, shear_values)

        # shear control
        V_max = max(abs(shear_values))
        if unit_system == "us":
            A_required = V_max / (0.44 * Fy * 1000)  # in^2
        else:
            A_required = V_max * 1000 / (0.44 * Fy)  # in^2

    return load_diagram, shear_diagram, moment_diagram, M_max, V_max, s_required, A_required


output = main_unrestrained_shoring(input_values)
