""" In this file we will get all inputs like soil properties and loads ( surcharge loads ).
then we will use functions in lateral pressure directory to calculate lateral pressure for surcharge and active passive
pressure.
then we should draw load diagram.
then we should calculate forces and moments due these load diagram.
then calculate D, Do according to FS.
then calculate Y0 --> where shear will be zero.
calculate maximum moment.
calculate S required.
( solve example 2 )
now for continue and solve example 3 I should pass deflection stuff."""
import copy
import sys
from sympy import symbols
from sympy.solvers import solve
import numpy as np

from shear_moment_diagram import diagram
from surchargeLoad import surcharge

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")
sys.path.append(r"F:/Cvision/Lateral-pressure-")

from Passive_Active.active_passive import active_passive
from Force.force import moment_calculator

D = symbols("D")


def calculate_force_and_arm(soil_pressure, water_pressure, main):
    force_soil, arm_soil = main.force_final(soil_pressure)
    force_water, arm_water = main.force_final(water_pressure, "water")
    for i in force_water:
        force_soil.append(i)
    for i in arm_water:
        arm_soil.append(i)
    return force_soil, arm_soil


def control_solution(item):
    final = []
    for number in item:
        number = number.evalf(chop=True)
        try:
            final.append(float(number))
        except:
            pass
    if final:
        final_value = max(final)
    else:
        final_value = "There is no answer!"
    return final_value


# function is ready when we have no surcharge loads.
def cantilever_soldier_pile(unit_system, h_active, h_passive, Surcharge_force, Surcharge_arm, Surcharge_depth,
                            active_force,
                            passive_force,
                            active_arm,
                            passive_arm,
                            FS, pile_spacing, fy):
    """units :
    if unit system = us -->
    forces -> lb
    arm and pile spacing -> ft
    fy -> ksi

    if unit system --> metric
    forces -> N
    arm and pile spacing -> m
    fy -> MPa"""

    D = symbols("D")

    h_passive_copy = copy.deepcopy(h_passive)
    h_passive_copy_2 = copy.deepcopy(h_passive)

    # calculating moment of surcharge
    Md_surcharge_total = 0
    for i in range(len(Surcharge_force)):
        Md_surcharge = (sum(h_active) - Surcharge_arm[i]) * Surcharge_force[
            i] * pile_spacing  # surcharge arm is from top layer.
        Md_surcharge_total += Md_surcharge
    Md = moment_calculator(active_force, active_arm, pile_spacing)  # driving moment
    Ms = moment_calculator(passive_force, passive_arm, pile_spacing)  # resisting moment
    equation = Ms - FS * (Md + Md_surcharge_total)
    equation2 = Ms - (Md + Md_surcharge_total)
    equations_report = [Ms, Md + Md_surcharge_total, equation]

    # finding D0
    D_zero = solve(equation, D)
    second_D_zero = solve(equation2, D)
    D_zero = control_solution(D_zero)
    h_passive_copy[-1] = h_passive_copy[-1].subs(D, D_zero)
    D_zero_final = sum(h_passive_copy)
    if D_zero != "There is no answer!" and D_zero_final >= 0:
        D_final_final = 1.2 * D_zero_final
        if len(h_passive_copy) > 1:
            D_final = D_final_final - h_passive_copy[-2]
        else:
            D_final = D_final_final

    else:
        D_final = "There is no answer!"
        return "There is no answer for D0!", "", "", "", "", "", ""

    second_D_zero = control_solution(second_D_zero)
    h_passive_copy[-1] = h_passive_copy_2[-1].subs(D, second_D_zero)
    second_D_zero_final = sum(h_passive_copy)
    if len(h_passive_copy) > 1:
        second_D_zero = second_D_zero_final - h_passive_copy[-2]
    else:
        second_D_zero = second_D_zero_final
    h_active[-1] = second_D_zero
    if second_D_zero == "There is no answer!" or second_D_zero_final < 0:
        D_final = "There is no answer!"
        return "There is no answer for D0!", "", "", "", "", "", ""

    # finding Y. where shear equal zero
    active_force_sum = 0
    for layer in active_force:
        for force in layer:
            active_force_sum += force

    passive_force_sum = 0
    for layer in passive_force:
        for force in layer:
            passive_force_sum += force
    equation_shear = passive_force_sum - active_force_sum - sum(Surcharge_force)
    Y = solve(equation_shear, D)
    Y = control_solution(Y)
    if Y == "There is no answer!":
        return "There is no answer for Y! ( where shear equal to zero )", D_zero, D_final, "", "", "", second_D_zero
    elif Surcharge_depth > sum(h_active) + Y and Y >= 0:
        return "Surcharge depth couldn't be larger than H + Y0", D_zero, D_final, "", "", "", second_D_zero
    else:
        # active passive
        active_force_zero_shear = copy.deepcopy(active_force)
        active_arm_zero_shear = copy.deepcopy(active_arm)
        for layer in range(len(active_force_zero_shear)):
            for force in range(len(active_force_zero_shear[layer])):
                try:
                    active_force_zero_shear[layer][force] = active_force_zero_shear[layer][force].subs(D, Y)
                    active_arm_zero_shear[layer][force] = active_arm_zero_shear[layer][force].subs(D, Y)
                except:
                    pass

        passive_force_zero_shear = copy.deepcopy(passive_force)
        passive_arm_zero_shear = copy.deepcopy(passive_arm)
        for layer in range(len(passive_force_zero_shear)):
            for force in range(len(passive_force_zero_shear[layer])):
                try:
                    passive_force_zero_shear[layer][force] = passive_force_zero_shear[layer][force].subs(D, Y)
                    passive_arm_zero_shear[layer][force] = passive_arm_zero_shear[layer][force].subs(D, Y)
                except:
                    pass

        # surcharge arm is from top layer.
        M_max_surcharge_total = 0
        for i in range(len(Surcharge_force)):
            M_max_surcharge = (sum(h_active[:-1]) + Y - Surcharge_arm[i]) * Surcharge_force[i] * pile_spacing
            M_max_surcharge_total += M_max_surcharge

        M_max_active = moment_calculator(active_force_zero_shear, active_arm_zero_shear, pile_spacing)
        M_max_passive = moment_calculator(passive_force_zero_shear, passive_arm_zero_shear, pile_spacing)

        M_max = abs(M_max_passive - M_max_active - M_max_surcharge_total)
        M_max = M_max.subs(D, Y)
        fb = 0.66 * fy
        if unit_system == "us":
            s_required = M_max * 12 / (fb * 1000)  # s unit --> inch^3
        else:
            # s_required = M_max * 10 ** 6 / fb  # s unit --> mm^3
            s_required = M_max * 10 ** 3 / fb  # s unit --> mm^3  # fb: MPa = N/mm^2

    return "No Error!", float(D_zero), float(D_final), float(Y), float(M_max), float(s_required), float(second_D_zero), equations_report


def put_D_in_list(my_list, d):
    for i in range(len(my_list)):
        for j in range(len(my_list[i])):
            try:
                my_list[i][j] = my_list[i][j].subs(D, d)
            except:
                pass
    return my_list


def multiple_pressure_pile_spacing(pressure, spacing):
    for i in range(len(pressure)):
        for j in range(len(pressure[i])):
            pressure[i][j] *= spacing
    return pressure


def calculate_D_and_control(hr, hd, retaining_h, unit_system, h_active,
                            surcharge_force,
                            surcharge_arm,
                            surcharge_depth,
                            force_soil_active,
                            force_soil_passive,
                            arm_soil_active,
                            arm_soil_passive, FS,
                            Pile_spacing,
                            Fy):
    D = symbols("D")
    hr.append(D)
    hd_copy = copy.deepcopy(hd)
    number_of_hr = len(hr)
    i = 1
    j = 0
    d_final = sum(hd[:-1]) + 1
    control = False
    while control is False:
        active_force = force_soil_active[
                       :number_of_hr] + [force_soil_active[-1]]
        passive_force = force_soil_passive[:i] + [force_soil_passive[-1]]
        for i in range(len(active_force[-2])):
            active_force[-2][i] = (active_force[-2][i] * D) / hd[0]
        # for i in range(len(arm_soil_active[-2])):
        #     arm_soil_active[-2][i] = (arm_soil_active[-2][i] * D) / hd[0]

        error, d0, d_final, y0, M_max, s_required, second_D_zero = cantilever_soldier_pile(unit_system, retaining_h, hr,
                                                                                           surcharge_force,
                                                                                           surcharge_arm,
                                                                                           surcharge_depth,
                                                                                           active_force,
                                                                                           passive_force,
                                                                                           arm_soil_active[:
                                                                                                           number_of_hr] +
                                                                                           [arm_soil_active[-1]],
                                                                                           arm_soil_passive[:i] +
                                                                                           [arm_soil_passive[-1]], FS,
                                                                                           Pile_spacing,
                                                                                           Fy)
        if error == "No Error!":
            if hd_copy[j] == D:
                control = True
            else:
                if d_final > hd_copy[j]:
                    control = False
                    hr.insert(-1, hd_copy[j])
                    del hd[hd.index(hd_copy[j])]
                    j += 1
                else:
                    control = True
                    # delete extra layers that are underground.
                    for k in hd[j:-1]:
                        del hd[hd.index(k)]
        else:
            return error, "", "", "", "", "", "", ""

    # delete D in hr
    del hr[-1]
    h_active = hr + hd

    return error, h_active, d0, d_final, y0, M_max, s_required, second_D_zero
