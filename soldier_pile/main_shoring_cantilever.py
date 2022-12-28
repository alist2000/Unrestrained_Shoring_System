from inputs import input_values

from surchargeLoad import surcharge
from shoring_cantilever import calculate_force_and_arm, control_solution, cantilever_soldier_pile, put_D_in_list, \
    multiple_pressure_pile_spacing, calculate_D_and_control
from shear_moment_diagram import diagram
from database import SQL_reader

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

    [number_of_project, unit_system, delta_h_list, h_active_list, h_passive_list, hr_list, hd_list,
     retaining_height_list,
     surcharge_depth_list,
     water_active_list,
     water_passive_list,
     number_of_layer_active_list,
     number_of_layer_passive_list, surcharge_type_list, surcharge_inputs_list, formula_active_list,
     formula_passive_list, soil_properties_active_list,
     soil_properties_passive_list, FS_list,
     Pile_spacing_list, allowable_deflection_list, Fy_list, E_list, selected_design_sections_list] = inputs.values()

    for project in range(number_of_project):
        delta_h = delta_h_list[project]
        h_active = h_active_list[project]
        h_passive = h_passive_list[project]
        hr = hr_list[project]
        hd = hd_list[project]
        retaining_height = retaining_height_list[project]
        surcharge_depth = surcharge_depth_list[project]
        water_active = water_active_list[project]
        water_passive = water_passive_list[project]
        number_of_layer_active = number_of_layer_active_list[project]
        number_of_layer_passive = number_of_layer_passive_list[project]
        surcharge_type = surcharge_type_list[project]
        formula_active = formula_active_list[project]
        formula_passive = formula_passive_list[project]
        FS = FS_list[project]
        Pile_spacing = Pile_spacing_list[project]
        allowable_deflection = allowable_deflection_list[project]
        Fy = Fy_list[project]
        E = E_list[project]
        selected_design_sections = selected_design_sections_list[project]

        # *** calculate surcharge ***
        main_surcharge = surcharge(unit_system, surcharge_depth, delta_h)

        if surcharge_type == "uniform":
            [q] = surcharge_inputs_list[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.uniform(q)
        elif surcharge_type == "Point Load":
            [q, l1, teta] = surcharge_inputs_list[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.point_load(q, l1, teta)

        elif surcharge_type == "Line Load":
            [q, l1] = surcharge_inputs_list[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.line_load(q, l1)
        else:  # strip load
            [q, l1, l2] = surcharge_inputs_list[project]
            surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.strip_load(q, l1, l2)

        # *** calculate active passive pressure ***
        if formula_active != "User Defined":
            [gama_active, phi_active, state_active, beta_active, omega_active,
             delta_active
             ] = soil_properties_active_list[project]

            # edit parameters
            # hr, hd, number_of_layer_active, gama_active, phi_active, beta_active, omega_active, delta_active, water_active = edit_parameters(
            #     retaining_height, h_active, number_of_layer_active, gama_active, phi_active, beta_active, omega_active,
            #     delta_active, water_active)

        else:
            # must be developed here!
            EFPa = soil_properties_active_list[project]
            # hr, hd, EFPa, water_active = edit_parameters_user_defined(retaining_height, h_active,
            #                                                           number_of_layer_active, EFPa,
            #                                                           water_active)

        if formula_passive != "User Defined":
            [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
             delta_passive
             ] = soil_properties_passive_list[project]
        else:
            # must be developed here!
            EFPp = soil_properties_passive_list[project]

        h_active_main = hr + hd
        h_passive_main = hd
        h_passive = h_passive_main  # must be equal!
        hd_use = [D]

        controller = False
        i = 0
        while controller is False:
            h_active_use = hr + hd_use
            h_passive_use = hd_use
            layer_number_active = len(h_active_use)
            layer_number_passive = len(h_passive_use)

            if formula_active != "User Defined":
                main_active = active_passive(h_active_use, water_active[:layer_number_active])
                soil_active, water_active_pressure, depth_list_active, h_water_active = main_active.pressure_calculator(
                    number_of_layer=layer_number_active,
                    gama=gama_active[:layer_number_active],
                    phi=phi_active[:layer_number_active],
                    theory=formula_active,
                    state="active",
                    unit_system=unit_system,
                    beta=beta_active[:layer_number_active],
                    omega=omega_active[:layer_number_active],
                    delta=delta_active[:layer_number_active])
                force_soil_active, arm_soil_active = calculate_force_and_arm(soil_active, water_active_pressure,
                                                                             main_active)
            else:
                soil_active = []
                for i in range(layer_number_active):
                    soil_active_pressure = EFPa[i] * h_active_use[i]
                    soil_active.append(soil_active_pressure)
                    # water must be calculated
                    # forces and arms also!

            if formula_passive != "User Defined":
                main_passive = active_passive(h_passive_use, water_passive[:layer_number_passive])
                soil_passive, water_passive_pressure, depth_list_passive, h_water_passive = main_passive.pressure_calculator(
                    number_of_layer=layer_number_passive,
                    gama=gama_passive[:layer_number_passive],
                    phi=phi_passive[:layer_number_passive],
                    theory=formula_passive,
                    state="passive",
                    unit_system=unit_system,
                    beta=beta_passive[:layer_number_passive],
                    omega=omega_passive[:layer_number_passive],
                    delta=delta_passive[:layer_number_passive])

                force_soil_passive, arm_soil_passive = calculate_force_and_arm(soil_passive, water_passive_pressure,
                                                                               main_passive)
            else:
                soil_passive = []
                for i in range(layer_number_passive):
                    soil_passive_pressure = EFPp[i] * h_passive_use[i]
                    soil_passive.append(soil_passive_pressure)
                    # water must be calculated
                    # forces and arms also!

            error, d0, d_final, y0, M_max, s_required, second_D_zero = cantilever_soldier_pile(unit_system,
                                                                                               h_active_use, hd_use,
                                                                                               surcharge_force,
                                                                                               surcharge_arm,
                                                                                               surcharge_depth,
                                                                                               force_soil_active,
                                                                                               force_soil_passive,
                                                                                               arm_soil_active,
                                                                                               arm_soil_passive, FS,
                                                                                               Pile_spacing,
                                                                                               Fy)
            if error != "No Error!":
                return error
            # error, h_active, d0, d_final, y0, M_max, s_required, second_D_zero = calculate_D_and_control(hr, hd,
            #                                                                                              retaining_height,
            #                                                                                              unit_system,
            #                                                                                              h_active,
            #                                                                                              surcharge_force,
            #                                                                                              surcharge_arm,
            #                                                                                              surcharge_depth,
            #                                                                                              force_soil_active,
            #                                                                                              force_soil_passive,
            #                                                                                              arm_soil_active,
            #                                                                                              arm_soil_passive,
            #                                                                                              FS,
            #                                                                                              Pile_spacing,
            #                                                                                              Fy)
            # if error != "No Error!":
            #     return error

            if hd_use == h_passive:
                controller = True
                Y_zero_shear = y0
                s_required_final = s_required
                M_max_final = M_max
                second_D_zero_final = second_D_zero
                depth_list_active_final = depth_list_active
                depth_list_passive_final = depth_list_passive
                soil_active_final = soil_active
                soil_passive_final = soil_passive
                water_active_pressure_final = water_active_pressure
                water_passive_pressure_final = water_passive_pressure
            else:
                # control D final with height of layer.
                if 0 <= y0 < h_passive[i]:
                    Y_zero_shear = y0
                    s_required_final = s_required
                    M_max_final = M_max
                if 0 <= second_D_zero < h_passive[i]:
                    second_D_zero_final = second_D_zero
                    depth_list_active_final = depth_list_active
                    depth_list_passive_final = depth_list_passive
                    soil_active_final = soil_active
                    soil_passive_final = soil_passive
                    water_active_pressure_final = water_active_pressure
                    water_passive_pressure_final = water_passive_pressure

                if d_final > h_passive[i]:
                    controller = False
                    hd_use.insert(i, h_passive[i])
                    i += 1
                else:
                    controller = True
                    h_active = hr + hd_use
                    h_passive = hd_use
                    soil_active_final = soil_active_final[:len(h_active)]
                    soil_passive_final = soil_passive_final[:len(h_passive)]
                    water_active_pressure_final = water_active_pressure_final[:len(h_active)]
                    water_passive_pressure_final = water_passive_pressure_final[:len(h_passive)]
        # if second_D_zero > 0:
        depth_list_active_final[-1][-1] = depth_list_active_final[-1][-1].subs(D, second_D_zero_final)
        depth_list_passive_final[-1][-1] = depth_list_passive_final[-1][-1].subs(D, second_D_zero_final)
        # else:
        #     del depth_list_active[-1]
        #     del depth_list_passive[-1]
        #     depth_list_active[-1][-1] += second_D_zero
        #     depth_list_passive[-1][-1] += second_D_zero
        soil_active_final = put_D_in_list(soil_active_final, second_D_zero_final)
        soil_passive_final = put_D_in_list(soil_passive_final, second_D_zero_final)
        water_active_pressure_final = put_D_in_list(water_active_pressure_final, second_D_zero_final)
        water_passive_pressure_final = put_D_in_list(water_passive_pressure_final, second_D_zero_final)

        surcharge_pressure = multiple_pressure_pile_spacing(np.array([surcharge_pressure]), Pile_spacing)
        soil_active_final = multiple_pressure_pile_spacing(soil_active_final, Pile_spacing)
        soil_passive_final = multiple_pressure_pile_spacing(soil_passive_final, Pile_spacing)
        water_active_pressure_final = multiple_pressure_pile_spacing(water_active_pressure_final, Pile_spacing)
        water_passive_pressure_final = multiple_pressure_pile_spacing(water_passive_pressure_final, Pile_spacing)

        main_diagram = diagram("us", surcharge_pressure[0], surcharge_depth, depth_list_active_final,
                               depth_list_passive_final,
                               soil_active_final,
                               soil_passive_final, water_active_pressure_final,
                               water_passive_pressure_final)

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

        output_section_list = []
        for w in selected_design_sections:
            w = w[1:]
            output_section = SQL_reader(w, A_required, s_required_final, unit_system)
            output_section_list.append(output_section)

    return "No Error!", load_diagram, shear_diagram, moment_diagram, M_max_final, V_max, s_required_final, A_required, output_section_list


output = main_unrestrained_shoring(input_values)
