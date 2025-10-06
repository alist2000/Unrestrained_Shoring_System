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

sys.path.append(r"D:/git/Shoring/LateralPressure")

from LateralPressure.Passive_Active.active_passive import active_passive
from LateralPressure.Force.force import moment_calculator

# some inputs
unit_system = "us"
Fs = 1.3
Pile_spacing = 6  # ft
Fy = 36  # ksi
surcharge_type = "Uniform"
q = 68
q_min = 72


def calculate_force_and_arm(soil_pressure, water_pressure, state):
    if state == "active":
        main = main_active
    else:
        main = main_passive
    force_soil, arm_soil = main.force_final(soil_pressure)
    force_water, arm_water = main.force_final(water_pressure, "water")
    for i in force_water:
        force_soil.append(i)
    for i in arm_water:
        arm_soil.append(i)
    return force_soil, arm_soil


# inputs for active passive.
D = symbols("D")
h_active = [10, D]
H = sum(h_active[:-1])
main_active = active_passive([10, D], ["No", "No"])
soil_active, water_active, depth_list_active, h_water_active = main_active.pressure_calculator(number_of_layer=2,
                                                                                               gama=[120, 125],
                                                                                               phi=[34, 36],
                                                                                               theory="Coulomb",
                                                                                               state="active",
                                                                                               unit_system="us",
                                                                                               beta=[0, 0],
                                                                                               omega=[0, 0],
                                                                                               delta=[0, 24])

force_soil_active, arm_soil_active = calculate_force_and_arm(soil_active, water_active, "active")

h_passive = [D]
main_passive = active_passive([D], ["No"])
soil_passive, water_passive, depth_list_passive, h_water_passive = main_passive.pressure_calculator(number_of_layer=1,
                                                                                                    gama=[125],
                                                                                                    phi=[36],
                                                                                                    theory="Coulomb",
                                                                                                    state="passive",
                                                                                                    unit_system="us",
                                                                                                    beta=[-32],
                                                                                                    omega=[0],
                                                                                                    delta=[24])

force_soil_passive, arm_soil_passive = calculate_force_and_arm(soil_passive, water_passive, "passive")

# inputs for surcharge.
surcharge_depth = 10
main_surcharge = surcharge("us", surcharge_depth, delta_h=0.01)
if q < q_min:
    q = q_min
if surcharge_type == "Uniform":
    surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge = main_surcharge.uniform(q)


def control_solution(item):
    final = []
    for number in item:
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
def calculate_excavation_depth(Surcharge_force, Surcharge_arm, active_force, passive_force, active_arm,
                               passive_arm,
                               FS, pile_spacing):
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

    # calculating moment of surcharge
    Md_surcharge = (sum(h_active) - Surcharge_arm) * Surcharge_force * pile_spacing  # surcharge arm is from top layer.
    Md = moment_calculator(active_force, active_arm, pile_spacing)  # driving moment
    Ms = moment_calculator(passive_force, passive_arm, pile_spacing)  # resisting moment
    equation = Ms - FS * (Md + Md_surcharge)
    equation2 = Ms - (Md + Md_surcharge)

    # finding D0
    D_zero = solve(equation, D)
    second_D_zero = solve(equation2, D)
    D_zero = control_solution(D_zero)
    if D_zero != "There is no answer!":
        D_final = 1.2 * D_zero
    else:
        D_final = "There is no answer!"
        return "There is no answer for D0!"

    second_D_zero = control_solution(second_D_zero)
    if second_D_zero == "There is no answer!":
        D_final = "There is no answer!"
        return "There is no answer for D0!"

    # finding Y. where shear equal zero
    active_force_sum = 0
    for layer in active_force:
        for force in layer:
            active_force_sum += force

    passive_force_sum = 0
    for layer in passive_force:
        for force in layer:
            passive_force_sum += force
    equation_shear = passive_force_sum - active_force_sum

    return "No Error!", D_zero, D_final, second_D_zero, equation_shear


def calculate_m_max(unit_system, H, active_force, passive_force, active_arm,
                    passive_arm,
                    pile_spacing, fy, load_type, h, Q, shear_equation, delta_h=0.01, l1=0, l2=0, teta=0):
    y = symbols("y")
    surcharge_zero_shear = surcharge("us", h, delta_h, True)
    if load_type == "Uniform":
        surcharge_force_zero, surcharge_arm_zero, surcharge_pressure_zero, error_surcharge_zero = \
            surcharge_zero_shear.uniform(Q)
    elif load_type == "Point Load":
        surcharge_force_zero, surcharge_arm_zero, surcharge_pressure_zero, error_surcharge_zero = \
            surcharge_zero_shear.point_load(Q, l1, teta)
    elif load_type == "Line Load":
        surcharge_force_zero, surcharge_arm_zero, surcharge_pressure_zero, error_surcharge_zero = \
            surcharge_zero_shear.line_load(Q, l1)
    else:  # strip load
        surcharge_force_zero, surcharge_arm_zero, surcharge_pressure_zero, error_surcharge_zero = \
            surcharge_zero_shear.strip_load(Q, l1, l2)

    shear_equation = shear_equation - surcharge_force_zero
    Y = solve(shear_equation, D)
    Y = control_solution(Y)
    if Y == "There is no answer!":
        return "There is no answer for Y! ( where shear equal to zero )"
    else:
        # surcharge
        surcharge_force_zero_shear = copy.deepcopy(surcharge_force_zero)
        surcharge_arm_zero_shear = copy.deepcopy(surcharge_arm_zero)
        for layer in range(len(surcharge_force_zero_shear)):
            try:
                surcharge_force_zero_shear[layer] = surcharge_force_zero_shear[layer].subs(y, Y)
                surcharge_arm_zero_shear[layer] = surcharge_arm_zero_shear[layer].subs(y, Y)
            except:
                pass

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
        M_max_surcharge = (H + Y - surcharge_arm_zero_shear) * surcharge_force_zero_shear * pile_spacing
        M_max_active = moment_calculator(active_force_zero_shear, active_arm_zero_shear, pile_spacing)
        M_max_passive = moment_calculator(passive_force_zero_shear, passive_arm_zero_shear, pile_spacing)

        M_max = abs(M_max_passive - M_max_active - M_max_surcharge)
        M_max = M_max.subs(D, Y)
        fb = 0.66 * fy
        if unit_system == "us":
            s_required = M_max * 12 / (fb * 1000)  # s unit --> inch^3
        else:
            s_required = M_max * 10 ** 6 / fb  # s unit --> mm^3

    return Y, M_max, s_required


error, d0, d_final, second_D_zero, shear_equation = calculate_excavation_depth(surcharge_force,
                                                                               surcharge_arm,
                                                                               force_soil_active,
                                                                               force_soil_passive,
                                                                               arm_soil_active,
                                                                               arm_soil_passive, Fs,
                                                                               Pile_spacing)

Y, M_max, s_required = calculate_m_max(unit_system, H, force_soil_active,
                                       force_soil_passive,
                                       arm_soil_active,
                                       arm_soil_passive,
                                       Pile_spacing, Fy, surcharge_type, q, shear_equation, delta_h=0.01, l1=0, l2=0,
                                       teta=0)
depth_list_active[-1][-1] = depth_list_active[-1][-1].subs(D, second_D_zero)
depth_list_passive[-1][-1] = depth_list_passive[-1][-1].subs(D, second_D_zero)


def put_D_in_list(my_list, d):
    for i in range(len(my_list)):
        for j in range(len(my_list[i])):
            try:
                my_list[i][j] = my_list[i][j].subs(D, d)
            except:
                pass
    return my_list


soil_active = put_D_in_list(soil_active, second_D_zero)
soil_passive = put_D_in_list(soil_passive, second_D_zero)
water_active = put_D_in_list(water_active, second_D_zero)
water_passive = put_D_in_list(water_passive, second_D_zero)


def multiple_pressure_pile_spacing(pressure, spacing):
    for i in range(len(pressure)):
        for j in range(len(pressure[i])):
            pressure[i][j] *= spacing
    return pressure


surcharge_pressure = multiple_pressure_pile_spacing(np.array([surcharge_pressure]), Pile_spacing)
soil_active = multiple_pressure_pile_spacing(soil_active, Pile_spacing)
soil_passive = multiple_pressure_pile_spacing(soil_passive, Pile_spacing)
water_active = multiple_pressure_pile_spacing(water_active, Pile_spacing)
water_passive = multiple_pressure_pile_spacing(water_passive, Pile_spacing)

main_diagram = diagram("us", surcharge_pressure[0], surcharge_depth, depth_list_active, depth_list_passive, soil_active,
                       soil_passive, water_active,
                       water_passive)

depth, sigma = main_diagram.base_calculate(delta_h=0.01)
load_diagram = main_diagram.load_diagram(depth, sigma)
shear_diagram = main_diagram.shear_diagram(depth, sigma)
