from inputs import input_values

from surchargeLoad import surcharge
from shoring_cantilever import calculate_force_and_arm, control_solution, cantilever_soldier_pile, put_D_in_list, \
    multiple_pressure_pile_spacing, calculate_D_and_control
from shear_moment_diagram import diagram
from database import SQL_reader
from deflection import deflection_calculator

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
            [EFPa, Ka] = soil_properties_active_list[project]
            # hr, hd, EFPa, water_active = edit_parameters_user_defined(retaining_height, h_active,
            #                                                           number_of_layer_active, EFPa,
            #                                                           water_active)

        if formula_passive != "User Defined":
            [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
             delta_passive
             ] = soil_properties_passive_list[project]
        else:
            # must be developed here!
            [EFPp] = soil_properties_passive_list[project]

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

            main_active = active_passive(h_active_use, water_active[:layer_number_active])
            if formula_active != "User Defined":
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
                # we have EFP = gama * K. assume K = 1 and gama = EFP. other values is not necessary.
                soil_active, water_active_pressure, depth_list_active, h_water_active = main_active.pressure_calculator(
                    number_of_layer=layer_number_active,
                    gama=EFPa[:layer_number_active],
                    phi=None,  # this value is not necessary.
                    theory=formula_active,
                    state="active",
                    unit_system=unit_system,
                    beta=None,  # this value is not necessary.
                    omega=None,  # this value is not necessary.
                    delta=None)  # this value is not necessary.
                force_soil_active, arm_soil_active = calculate_force_and_arm(soil_active, water_active_pressure,
                                                                             main_active)

            main_passive = active_passive(h_passive_use, water_passive[:layer_number_passive])
            if formula_passive != "User Defined":
                soil_passive, water_passive_pressure, depth_list_passive, h_water_passive = main_passive.pressure_calculator(
                    gama=gama_passive[:layer_number_passive],
                    number_of_layer=layer_number_passive,
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
                soil_passive, water_passive_pressure, depth_list_passive, h_water_passive = main_passive.pressure_calculator(
                    number_of_layer=layer_number_passive,
                    gama=EFPp[:layer_number_passive],
                    phi=None,  # this value is not necessary.
                    theory=formula_passive,
                    state="passive",
                    unit_system=unit_system,
                    beta=None,  # this value is not necessary.
                    omega=None,  # this value is not necessary.
                    delta=None)  # this value is not necessary.

                force_soil_passive, arm_soil_passive = calculate_force_and_arm(soil_passive, water_passive_pressure,
                                                                               main_passive)

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

            # control D final with height of layer.
            h_passive_copy = copy.deepcopy(h_passive)
            h_passive_copy[-1] = h_passive_copy[-1].subs(D, second_D_zero)
            if 0 <= y0 <= h_passive_copy[i]:
                Y_zero_shear = y0
                s_required_final = s_required
                M_max_final = M_max
            if 0 <= second_D_zero <= h_passive_copy[i]:
                second_D_zero_final = second_D_zero
                depth_list_active_final = depth_list_active
                depth_list_passive_final = depth_list_passive
                soil_active_final = soil_active
                soil_passive_final = soil_passive
                water_active_pressure_final = water_active_pressure
                water_passive_pressure_final = water_passive_pressure

            if hd_use == h_passive:
                controller = True
            else:
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

        #  Control R: summation of horizontal forces.
        controller2 = True
        passive_force_result = 0
        active_force_result = 0
        while controller2:
            force_soil_active_final = put_D_in_list(force_soil_active, d_final)
            force_soil_passive_final = put_D_in_list(force_soil_passive, d_final)
            for layer in force_soil_passive_final:
                for force in layer:
                    passive_force_result += force
            for layer in force_soil_active_final:
                for force in layer:
                    active_force_result += force
            active_force_result += surcharge_force
            R = active_force_result - passive_force_result
            # passive force must be greater than active.
            if R > 0:
                controller2 = True
                # fail! --> increase D
                d_final += delta_h
            else:
                controller2 = False

        h_active_for_def = copy.deepcopy(h_active)
        h_active_for_def[-1] = h_active_for_def[-1].subs(D, d_final)
        final_h_active_for_def = float(sum(h_active_for_def))

        depth_list_active_final[-1][-1] = depth_list_active_final[-1][-1].subs(D, second_D_zero_final)
        depth_list_passive_final[-1][-1] = depth_list_passive_final[-1][-1].subs(D, second_D_zero_final)
        excavation_depth = 0
        for i in depth_list_passive_final:
            excavation_depth += float(sum(i))

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

        # calculate deflection
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        j = 0
        for i in depth:
            depth[j] = round(i, delta_h_decimal)
            j += 1

        PoF = round(0.25 * excavation_depth, delta_h_decimal)  # point of fixity --> B
        c = round((excavation_depth - PoF) / 2, delta_h_decimal) + PoF  # point c --> center of OB
        sum_hr = round(sum(hr), delta_h_decimal)
        deflection = deflection_calculator(delta_h, delta_h_decimal, depth, moment_values, PoF, c, sum_hr,
                                           final_h_active_for_def)

        # shear control
        V_max = max(abs(shear_values))
        if unit_system == "us":
            A_required = V_max / (0.44 * Fy * 1000)  # in^2
        else:
            A_required = V_max * 1000 / (0.44 * Fy)  # in^2

        # export appropriate section
        output_section_list = []
        for w in selected_design_sections:
            w = w[1:]
            output_section = SQL_reader(w, A_required, s_required_final, unit_system)
            output_section_list.append(output_section)

        #  divide deflections by EI of every section
        final_deflection = []
        for item in output_section_list:
            section, Ix, section_area, Sx = item.values()
            #  control available sections
            if section != "" and Ix != "":
                if unit_system == "us":
                    EI = E * 1000 * float(Ix) / (12 ** 3)  # E: Ksi , M: lb.ft
                else:
                    EI = E * float(Ix) * (10 ** 9)  # E: Mpa , M: N.m

                deflection_copy = copy.deepcopy(deflection)
                for i in range(len(deflection)):
                    deflection_copy[i] = deflection_copy[i] / EI
                final_deflection.append(deflection_copy)
                DCR_deflection = []
                max_delta_list = []
                for delta in final_deflection:
                    max_delta = max(delta)
                    min_delta = abs(min(delta))
                    max_delta = max(min_delta, max_delta)
                    max_delta_list.append(max_delta)
                    DCR = allowable_deflection / max_delta
                    DCR_deflection.append(DCR)

        #  check error for available sections according to S and A.
        #  deflection ratio don't be checked when export sections.(Ix not control)
        if not final_deflection:
            section_error = "No answer! No section is appropriate for your situation!"
            return section_error

    return "No Error!", load_diagram, shear_diagram, moment_diagram, M_max_final, V_max, s_required_final, A_required, output_section_list, final_deflection, DCR_deflection, max_delta_list


output = main_unrestrained_shoring(input_values)
