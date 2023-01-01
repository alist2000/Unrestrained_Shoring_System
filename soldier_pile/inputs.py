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

        if retaining_height != 0:
            hr_list.append(retaining_height)
            number_of_layer += 1
            gama.insert(-1, gama[-1])
            phi.insert(-1, phi[-1])
            beta.insert(-1, beta[-1])
            omega.insert(-1, omega[-1])
            delta.insert(-1, delta[-1])
            water.insert(-1, water[-1])

    hd_list.append(height[-1])  # final excavation depth : D
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

    hd_list.append(height[-1])  # final excavation depth : D
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
surcharge_type = "uniform"
if surcharge_type == "uniform":
    q = 72
    # if q < q_min:
    #     q = q_min
    surcharge_inputs = [q]
elif surcharge_type == "Point Load":
    q = ...
    l1 = ...
    teta = ...
    surcharge_inputs = [q, l1, teta]

elif surcharge_type == "Line Load":
    q = ...
    l1 = ...
    surcharge_inputs = [q, l1]

elif surcharge_type == "Strip Load":
    q = ...
    l1 = ...
    l2 = ...
    surcharge_inputs = [q, l1, l2]

Formula_active = "Coulomb"
if Formula_active != "User Defined":
    gama_active = [120, 125, 125]
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
    EFPa = ...  # gama * Ka
    hr, hd, EFPa, number_of_layer_passive, water_active = edit_parameters_user_defined(retaining_height, h_active,
                                                                                       number_of_layer_active, EFPa,
                                                                                       water_active)
    soil_properties_active = [EFPa]

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

    EFPp = ...  # gama * Kp
    soil_properties_passive = [EFPp]

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
                "FS": [FS],
                "Pile_spacing": [Pile_spacing],
                "allowable_deflection": [allowable_deflection],
                "Fy": [Fy],
                "E": [E],
                "selected_design_sections": [selected_design_sections]
                }
