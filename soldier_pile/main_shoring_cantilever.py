from inputs import input_single
from site_input import input2

from surchargeLoad import surcharge
from shoring_cantilever import calculate_force_and_arm, control_solution, cantilever_soldier_pile, put_D_in_list, \
    multiple_pressure_pile_spacing, calculate_D_and_control
from shear_moment_diagram import diagram
from database import SQL_reader
from deflection import deflection_calculator
from Lagging import lagging_design
from shear_moment_diagram import plotter_deflection
from report import create_feather
from Output import output_single_solved, output_single_no_solution

import sys
import math

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")

from Passive_Active.active_passive import active_passive
from Force.force import moment_calculator
from Surcharge.result import result_surcharge

import copy
import sys
from sympy import symbols
from sympy.solvers import solve
import numpy as np


def main_unrestrained_shoring(inputs):
    D = symbols("D")

    [input_validation, number_of_project, unit_system, delta_h_list, h_active_list, h_passive_list, hr_list, hd_list,
     retaining_height_list,
     surcharge_depth_list,
     water_active_list,
     water_passive_list,
     number_of_layer_active_list,
     number_of_layer_passive_list, surcharge_type_list, surcharge_inputs_list, formula_active_list,
     formula_passive_list, soil_properties_active_list,
     soil_properties_passive_list, ph_list, Fb_list, timber_size_list, FS_list,
     Pile_spacing_list, allowable_deflection_list, Fy_list, E_list, selected_design_sections_list] = input_single(
        inputs).values()

    inputs_errors = list(input_validation.values())
    number_of_input_error = inputs_errors[0]
    description_input_error = inputs_errors[1]
    if number_of_input_error != 0:
        output_single = output_single_no_solution(description_input_error)
        return output_single

    if unit_system == "us":
        deflection_unit = "in"
        length_unit = "ft"
    else:
        deflection_unit = "mm"
        length_unit = "m"

    project_error = []
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
        ph = ph_list[project]
        Fb = Fb_list[project]
        timber_size = timber_size_list[project]
        Fy = Fy_list[project]
        E = E_list[project]
        selected_design_sections = selected_design_sections_list[project]
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        h_active_main = hr + hd
        h_passive_main = hd
        h_passive = h_passive_main  # must be equal!
        hd_use = [D]

        error_surcharge_list = []

        controller = False
        i = 0
        while controller is False:
            h_active_use = hr + hd_use
            h_passive_use = hd_use
            layer_number_active = len(h_active_use)
            layer_number_passive = len(h_passive_use)

            # ACTIVE SIDE
            main_active = active_passive(h_active_use, water_active[:layer_number_active])
            if formula_active != "User Defined":
                # inputs
                [gama_active, phi_active, state_active, beta_active, omega_active,
                 delta_active
                 ] = soil_properties_active_list[project]

                soil_active, water_active_pressure, depth_list_active, h_water_active, k, water_pressure_list_active = main_active.pressure_calculator(
                    number_of_layer=layer_number_active,
                    gama=gama_active[:layer_number_active],
                    phi=phi_active[:layer_number_active],
                    theory=formula_active,
                    state="active",
                    unit_system=unit_system,
                    beta=beta_active[:layer_number_active],
                    omega=omega_active[:layer_number_active],
                    delta=delta_active[:layer_number_active])

                # *** calculate surcharge ***
                i_sur = 0
                surcharge_force_list = []
                surcharge_arm_list = []
                surcharge_pressure_list = []
                for h in hr:
                    main_surcharge = surcharge(unit_system, h, delta_h)
                    Ka = k[i_sur]
                    surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
                        main_surcharge,
                        surcharge_type, q, l1, l2,
                        teta, Ka)
                    if i_sur != 0:
                        surcharge_arm += hr[i_sur - 1]
                    surcharge_force_list.append(surcharge_force)
                    surcharge_arm_list.append(surcharge_arm)
                    surcharge_pressure_list.append(surcharge_pressure)
                    i_sur += 1
                    # error_surcharge_list.append(error_surcharge)

            else:
                # inputs
                [EFPa, Ka] = soil_properties_active_list[project]

                # we have EFP = gama * K. assume K = 1 and gama = EFP. other values is not necessary.
                soil_active, water_active_pressure, depth_list_active, h_water_active, k, water_pressure_list_active = main_active.pressure_calculator(
                    number_of_layer=layer_number_active,
                    gama=EFPa[:layer_number_active],
                    phi=None,  # this value is not necessary.
                    theory=formula_active,
                    state="active",
                    unit_system=unit_system,
                    beta=None,  # this value is not necessary.
                    omega=None,  # this value is not necessary.
                    delta=None)  # this value is not necessary.

                # *** calculate surcharge ***
                surcharge_force_list = []
                surcharge_arm_list = []
                surcharge_pressure_list = []
                i_sur = 0
                for h in hr:
                    main_surcharge = surcharge(unit_system, h, delta_h)
                    surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
                        main_surcharge,
                        surcharge_type, q, l1, l2,
                        teta, Ka)
                    if i_sur != 0:
                        surcharge_arm += hr[i_sur - 1]
                    surcharge_force_list.append(surcharge_force)
                    surcharge_arm_list.append(surcharge_arm)
                    surcharge_pressure_list.append(surcharge_pressure)
                    # error_surcharge_list.append(error_surcharge)
                    i_sur += 1

            # we ignore errors for surcharge. if we have error just don't
            # if error_surcharge_list[0] != "No Error!":
            #     project_error.append(error_surcharge_list)
            #     break

            force_soil_active, arm_soil_active = calculate_force_and_arm(soil_active, water_active_pressure,
                                                                         main_active)

            # PASSIVE SIDE
            main_passive = active_passive(h_passive_use, water_passive[:layer_number_passive])
            if formula_passive != "User Defined":
                [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
                 delta_passive
                 ] = soil_properties_passive_list[project]
                soil_passive, water_passive_pressure, depth_list_passive, h_water_passive, k, water_pressure_list_passive = main_passive.pressure_calculator(
                    gama=gama_passive[:layer_number_passive],
                    number_of_layer=layer_number_passive,
                    phi=phi_passive[:layer_number_passive],
                    theory=formula_passive,
                    state="passive",
                    unit_system=unit_system,
                    beta=beta_passive[:layer_number_passive],
                    omega=omega_passive[:layer_number_passive],
                    delta=delta_passive[:layer_number_passive])

            else:
                [EFPp] = soil_properties_passive_list[project]
                soil_passive, water_passive_pressure, depth_list_passive, h_water_passive, k, water_pressure_list_passive = main_passive.pressure_calculator(
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

            error_cantilever, d0, d_final, y0, M_max, s_required, second_D_zero = cantilever_soldier_pile(unit_system,
                                                                                                          h_active_use,
                                                                                                          hd_use,
                                                                                                          surcharge_force_list,
                                                                                                          surcharge_arm_list,
                                                                                                          surcharge_depth,
                                                                                                          force_soil_active,
                                                                                                          force_soil_passive,
                                                                                                          arm_soil_active,
                                                                                                          arm_soil_passive,
                                                                                                          FS,
                                                                                                          Pile_spacing,
                                                                                                          Fy)
            if error_cantilever != "No Error!":
                project_error.append([error_cantilever])
                break

            # control D final with height of layer.
            h_passive_copy = copy.deepcopy(h_passive)
            h_passive_copy[-1] = h_passive_copy[-1].subs(D, second_D_zero)
            if 0 <= y0 <= h_passive_copy[-1]:
                Y_zero_shear = y0
                s_required_final = s_required
                M_max_final = M_max
            if 0 <= second_D_zero <= h_passive_copy[-1]:
                second_D_zero_copy = copy.deepcopy(second_D_zero)
                depth_list_active_copy = copy.deepcopy(depth_list_active)
                depth_list_passive_copy = copy.deepcopy(depth_list_passive)
                soil_active_copy = copy.deepcopy(soil_active)
                soil_passive_copy = copy.deepcopy(soil_passive)
                water_active_pressure_copy = copy.deepcopy(water_pressure_list_active)
                water_passive_pressure_copy = copy.deepcopy(water_pressure_list_passive)
                second_D_zero_final = second_D_zero_copy
                depth_list_active_final = depth_list_active_copy
                depth_list_passive_final = depth_list_passive_copy
                soil_active_final = soil_active_copy
                soil_passive_final = soil_passive_copy
                water_active_pressure_final = water_active_pressure_copy
                water_passive_pressure_final = water_passive_pressure_copy

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

        if not project_error:

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
                active_force_result += sum(surcharge_force_list)
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
            excavation_depth_dfinal = final_h_active_for_def - sum(hr)

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

            # create feather for load diagram
            create_feather(depth, sigma, "Load",
                           "load_project" + str(project + 1))

            # create feather for shear diagram
            create_feather(depth, shear_values, "Shear",
                           "shear_project" + str(project + 1))

            # create feather for moment diagram
            create_feather(depth, moment_values, "Moment",
                           "moment_project" + str(project + 1))

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
            depth_deflection, deflection = deflection_calculator(delta_h, delta_h_decimal, depth, moment_values, PoF, c,
                                                                 sum_hr,
                                                                 final_h_active_for_def)
            maxdef = max(deflection)
            mindef = abs(min(deflection))
            max_deflection = max(maxdef, mindef)
            if unit_system == "us":
                E_allowable_deflection = E * 1000 * float(allowable_deflection) / (12 ** 3)  # E: Ksi , M: lb.ft
            else:
                E_allowable_deflection = E * float(allowable_deflection) * (10 ** 9)  # E: Mpa , M: N.m
            Ix_min = max_deflection / E_allowable_deflection

            # shear control
            V_max = max(abs(shear_values))
            if unit_system == "us":
                A_required = V_max / (0.44 * Fy * 1000)  # in^2
            else:
                A_required = V_max * 1000 / (0.44 * Fy)  # mm^2

            # export appropriate section
            output_section_list = []
            for w in selected_design_sections:
                w = w[1:]  # section has sent : w + number
                output_section = SQL_reader(w, A_required, s_required_final, Ix_min, unit_system)
                output_section_list.append(output_section)

            #  divide deflections by EI of every section
            # + control lagging
            status_lagging = []
            DCR_lagging = []
            d_concrete_list = []

            DCR_moment = []
            DCR_shear = []
            final_deflection = []
            final_sections = []
            h_list = []
            bf_list = []
            tw_list = []
            tf_list = []
            for item in output_section_list:
                section, Ix, section_area, Sx, h, bf, tw, tf = item.values()
                #  control available sections
                if section != "" and Ix != "":
                    final_sections.append(section)
                    if unit_system == "us":
                        EI = E * 1000 * float(Ix) / (12 ** 3)  # E: Ksi , M: lb.ft
                    else:
                        EI = E * float(Ix) * (10 ** 9)  # E: Mpa , M: N.m

                    # lagging control
                    lagging = lagging_design(unit_system, Pile_spacing, section, ph, timber_size)
                    DCR_moment_timber, status, d_concrete = lagging.moment_design(Fb, tw, 1.25, 1.1, 1.1)
                    DCR_lagging.append(DCR_moment_timber)
                    status_lagging.append(status)
                    d_concrete_list.append(d_concrete)

                    #  DCR moment
                    DCR_m = s_required_final / Sx
                    DCR_moment.append(DCR_m)

                    #  DCR shear
                    DCR_v = A_required / section_area
                    DCR_shear.append(DCR_v)

                    deflection_copy = copy.deepcopy(deflection)
                    for i in range(len(deflection)):
                        deflection_copy[i] = deflection_copy[i] / EI
                    final_deflection.append(deflection_copy)

                    # add dimensions of section
                    h_list.append(h)
                    bf_list.append(bf)
                    tw_list.append(tw)
                    tf_list.append(tf)

            #  DCR deflection
            DCR_deflection = []
            max_delta_list = []
            deflection_plot = []
            i = 0
            for delta in final_deflection:
                # deflection plot
                plot = plotter_deflection(depth_deflection, delta, "Deflection", "Z", deflection_unit, length_unit)
                create_feather(depth_deflection, delta, "Deflection",
                               "deflection_project" + str(project + 1) + "_section" + str(i + 1))
                deflection_plot.append(plot)
                max_delta = max(delta)
                min_delta = abs(min(delta))
                max_delta = max(min_delta, max_delta)
                max_delta_list.append(max_delta)
                DCR_def = max_delta / allowable_deflection
                DCR_deflection.append(DCR_def)
                i += 1

            #  check error for available sections according to S and A.
            #  deflection ratio don't be checked when export sections.(Ix not control)
            if not final_deflection:
                section_error = ["No answer! No section is appropriate for your situation!"]
                project_error.append(section_error)
            else:
                continue

    if number_of_project == 1 and not project_error:
        general_plot = [load_diagram, shear_diagram, moment_diagram]
        general_values = [math.ceil(excavation_depth_dfinal), round(V_max / 1000, 2), round(M_max_final / 1000, 2),
                          Y_zero_shear, A_required, s_required_final]
        general_output = {"plot": general_plot, "value": general_values}
        specific_plot = deflection_plot
        specific_values = [final_sections, max_delta_list, DCR_moment, DCR_shear, DCR_deflection, timber_size,
                           status_lagging, d_concrete_list, h_list, bf_list, tw_list, tf_list]
        specific_output = {"plot": specific_plot, "value": specific_values}
        output_single = output_single_solved(unit_system, general_output, specific_output)
        return output_single
    if number_of_project == 1 and project_error:
        output_single = output_single_no_solution(project_error)
        return output_single

    return "No Error!", load_diagram, shear_diagram, moment_diagram, M_max_final, V_max, s_required_final, A_required, output_section_list, final_deflection, DCR_deflection, max_delta_list


a = main_unrestrained_shoring(input2)
