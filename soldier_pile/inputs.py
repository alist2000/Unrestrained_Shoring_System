import copy

from sympy import symbols


# *** ATTENTION :  all input controls must be checked here.

def edit_parameters(retaining_height, height,
                    number_of_layer,
                    gama,
                    phi,
                    beta,
                    omega,
                    delta,
                    water):
    hr_list = []
    hd_list = []
    i = 0
    for h in height[:-1]:  # last index is parametric ( D )
        if h > retaining_height and retaining_height != 0:
            hr = retaining_height
            hd = h - retaining_height
            hr_list.append(hr)
            hd_list.append(hd)
            number_of_layer += 1
            gama.insert(i + 1, gama[i])
            phi.insert(i + 1, phi[i])
            beta.insert(i + 1, beta[i])
            omega.insert(i + 1, omega[i])
            delta.insert(i + 1, delta[i])
            water.insert(i + 1, water[i])
            i += 1
            for j in height[i:]:
                hd_list.append(j)
            return hr_list, hd_list, number_of_layer, gama, phi, beta, omega, delta, water

        else:
            if retaining_height != 0:
                hr_list.append(h)
                retaining_height = retaining_height - h
            else:
                hd_list.append(h)
            i += 1

    # extra ? check and control
    if retaining_height != 0:
        hr_list.append(retaining_height)
        number_of_layer += 1
        gama.insert(-1, gama[-1])
        phi.insert(-1, phi[-1])
        beta.insert(-1, beta[-1])
        omega.insert(-1, omega[-1])
        delta.insert(-1, delta[-1])
        water.insert(-1, water[-1])

    hd_list.append(height[-1])  # final Embedment Depth : D
    return hr_list, hd_list, number_of_layer, gama, phi, beta, omega, delta, water


def edit_parameters_user_defined(retaining_height, height,
                                 number_of_layer, EFP,
                                 water):
    hr_list = []
    hd_list = []
    i = 0
    for h in height[:-1]:  # last index is parametric ( D )
        if h > retaining_height and retaining_height != 0:
            hr = retaining_height
            hd = h - retaining_height
            hr_list.append(hr)
            hd_list.append(hd)
            number_of_layer += 1
            EFP.insert(i + 1, EFP[i])
            water.insert(i + 1, water[i])
            i += 1
            for j in height[i:]:
                hd_list.append(j)
            return hr_list, hd_list, number_of_layer, EFP, water


        else:
            if retaining_height != 0:
                hr_list.append(h)
                retaining_height = retaining_height - h
            else:
                hd_list.append(h)
            i += 1
    if retaining_height != 0:
        hr_list.append(retaining_height)
        number_of_layer += 1
        EFP.insert(-1, EFP[-1])

        water.insert(-1, water[-1])

    hd_list.append(height[-1])  # final Embedment Depth : D
    return hr_list, hd_list, number_of_layer, EFP, water


number_of_project = 1

D = symbols("D")

unit_system = "us"

calculation_type = "Auto"  # or Manual

delta_h = 0.01
h_active = [10, 20, D]
h_passive = [20, D]
retaining_height = 10
surcharge_depth = retaining_height
water_active = ["No", "No", "No"]
water_passive = ["No", "No"]
number_of_layer_active = len(h_active)
number_of_layer_passive = len(h_passive)

# q_min = 72
surcharge_type = ["Uniform"]
q_all = []
l1_all = []
l2_all = []
teta_all = []
for i in range(len(surcharge_type)):
    if surcharge_type[i] == "Uniform":
        q = 72 / 0.283
        q_all.append(q)
        l1_all.append("")
        l2_all.append("")
        teta_all.append("")

        # if q < q_min:
        #     q = q_min
    elif surcharge_type[i] == "Point Load":
        q = 100000
        l1 = 1
        teta = 0
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append("")
        teta_all.append(teta)

    elif surcharge_type[i] == "Line Load":
        q = ...
        l1 = ...
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append("")
        teta_all.append("")

    elif surcharge_type[i] == "Strip Load":
        q = ...
        l1 = ...
        l2 = ...
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append(l2)
        teta_all.append("")

surcharge_inputs = [q_all, l1_all, l2_all, teta_all]

Formula_active = "Coulomb"
if Formula_active != "User Defined":
    gama_active = [120, 125, 125]  # pcf or N/m^3
    phi_active = [34, 36, 36]
    state_active = "active"
    beta_active = [0, 0, 0]
    omega_active = [0, 0, 0]
    delta_active = [0, 24, 24]
    hr, hd, number_of_layer_active, gama_active, phi_active, beta_active, omega_active, delta_active, water_active = edit_parameters(
        retaining_height, h_active, number_of_layer_active, gama_active, phi_active, beta_active, omega_active,
        delta_active, water_active)
    soil_properties_active = [gama_active, phi_active, state_active, beta_active, omega_active,
                              delta_active
                              ]
else:
    EFPa = [33.96, 26.875, 26.875]  # gama * Ka
    Ka_surcharge = 0.283
    hr, hd, number_of_layer_passive, EFPa, water_active = edit_parameters_user_defined(retaining_height, h_active,
                                                                                       number_of_layer_active, EFPa,
                                                                                       water_active)
    soil_properties_active = [EFPa, Ka_surcharge]

Formula_passive = "Coulomb"
if Formula_passive != "User Defined":
    gama_passive = [125, 125]
    phi_passive = [36, 36]
    theory_passive = "Coulomb"
    state_passive = "passive"
    beta_passive = [-32, -32]
    omega_passive = [0, 0]
    delta_passive = [24, 24]
    soil_properties_passive = [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
                               delta_passive
                               ]
else:

    EFPp = [150, 150]  # gama * Kp
    soil_properties_passive = [EFPp]


# lagging inputs
ph_max = 400
Fb = 825  # ksi for us and Mpa for metric
timber_size = "3 x 16"


FS = 1.3
Pile_spacing = 6  # ft
allowable_deflection = 0.5  # in
Fy = 36  # ksi or MpaNo
E = 29000  # ksi or MPa

selected_design_sections = ["W18", "W21", "W24", "W27"]

# all values have length equal to number of project.

input_values = {"number_of_project": number_of_project,
                "unit_system": unit_system,
                "delta_h": [delta_h],
                "h_active": [h_active],
                "h_passive": [h_passive],
                "hr": [hr],
                "hd": [hd],
                "retaining_height": [retaining_height],
                "surcharge_depth": [surcharge_depth],
                "water_active": [water_active],
                "water_passive": [water_passive],
                "number_of_layer_active": [number_of_layer_active],
                "number_of_layer_passive": [number_of_layer_passive],
                "surcharge_type": [surcharge_type],
                "surcharge_inputs": [surcharge_inputs],
                "formula_active": [Formula_active],
                "formula_passive": [Formula_passive],
                "soil_properties_active": [soil_properties_active],
                "soil_properties_passive": [soil_properties_passive],
                "ph_max": [ph_max],
                "Fb": [Fb],
                "timber_size": [timber_size],
                "FS": [FS],
                "Pile_spacing": [Pile_spacing],
                "allowable_deflection": [allowable_deflection],
                "Fy": [Fy],
                "E": [E],
                "selected_design_sections": [selected_design_sections]
                }
