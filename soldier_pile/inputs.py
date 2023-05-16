import copy

from sympy import symbols
import json

from site_input import input2


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
    if retaining_height != 0 or number_of_layer == 1:
        if retaining_height != 0:
            hr_list.append(retaining_height)
        number_of_layer += 1
        gama.insert(-1, gama[-1])
        phi.insert(-1, phi[-1])
        beta.insert(-1, beta[-1])
        omega.insert(-1, omega[-1])
        delta.insert(-1, delta[-1])
        water.insert(-1, water[-1])

    if number_of_layer == 1:
        hd_list.append(D)
    else:
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
delta_h = 0.01

D = symbols("D")


# unit_system = "us"
#
# calculation_type = "Auto"  # or Manual

# h_active = [10, 20, D]
# h_passive = [20, D]
# retaining_height = 10
# surcharge_depth = retaining_height
# water_active = ["No", "No", "No"]
# water_passive = ["No", "No"]
# number_of_layer_active = len(h_active)
# number_of_layer_passive = len(h_passive)
#
# # q_min = 72
# surcharge_type = ["Uniform"]
# q_all = []
# l1_all = []
# l2_all = []
# teta_all = []
# for i in range(len(surcharge_type)):
#     if surcharge_type[i] == "Uniform":
#         q = 72 / 0.283
#         q_all.append(q)
#         l1_all.append("")
#         l2_all.append("")
#         teta_all.append("")
#
#         # if q < q_min:
#         #     q = q_min
#     elif surcharge_type[i] == "Point Load":
#         q = 100000
#         l1 = 1
#         teta = 0
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append("")
#         teta_all.append(teta)
#
#     elif surcharge_type[i] == "Line Load":
#         q = ...
#         l1 = ...
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append("")
#         teta_all.append("")
#
#     elif surcharge_type[i] == "Strip Load":
#         q = ...
#         l1 = ...
#         l2 = ...
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append(l2)
#         teta_all.append("")
#
# surcharge_inputs = [q_all, l1_all, l2_all, teta_all]
#
# Formula_active = "Coulomb"
# if Formula_active != "User Defined":
#     gama_active = [120, 125, 125]  # pcf or N/m^3
#     phi_active = [34, 36, 36]
#     state_active = "active"
#     beta_active = [0, 0, 0]
#     omega_active = [0, 0, 0]
#     delta_active = [0, 24, 24]
#     hr, hd, number_of_layer_active, gama_active, phi_active, beta_active, omega_active, delta_active, water_active = edit_parameters(
#         retaining_height, h_active, number_of_layer_active, gama_active, phi_active, beta_active, omega_active,
#         delta_active, water_active)
#     soil_properties_active = [gama_active, phi_active, state_active, beta_active, omega_active,
#                               delta_active
#                               ]
# else:
#     EFPa = [33.96, 26.875, 26.875]  # gama * Ka  unit: pcf or N/m^3
#     Ka_surcharge = 0.283
#     hr, hd, number_of_layer_passive, EFPa, water_active = edit_parameters_user_defined(retaining_height, h_active,
#                                                                                        number_of_layer_active, EFPa,
#                                                                                        water_active)
#     soil_properties_active = [EFPa, Ka_surcharge]
#
# Formula_passive = "Coulomb"
# if Formula_passive != "User Defined":
#     gama_passive = [125, 125]
#     phi_passive = [36, 36]
#     theory_passive = "Coulomb"
#     state_passive = "passive"
#     beta_passive = [-32, -32]
#     omega_passive = [0, 0]
#     delta_passive = [24, 24]
#     soil_properties_passive = [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
#                                delta_passive
#                                ]
# else:
#
#     EFPp = [150, 150]  # gama * Kp  unit: pcf or N/m^3
#     soil_properties_passive = [EFPp]
#
# # lagging inputs
# ph_max = 400  # psf or N/M^2
# Fb = 825  # ksi for us and Mpa for metric
# timber_size = "3 x 16"
#
# FS = 1.3
# Pile_spacing = 6  # ft
# allowable_deflection = 0.5  # in
# Fy = 36  # ksi or MpaNo
# E = 29000  # ksi or MPa
#
# selected_design_sections = ["W18", "W21", "W24", "W27"]

# all values have length equal to number of project.

# input_values = {"number_of_project": number_of_project,
#                 "unit_system": unit_system,
#                 "delta_h": [delta_h],
#                 "h_active": [h_active],
#                 "h_passive": [h_passive],
#                 "hr": [hr],
#                 "hd": [hd],
#                 "retaining_height": [retaining_height],
#                 "surcharge_depth": [surcharge_depth],
#                 "water_active": [water_active],
#                 "water_passive": [water_passive],
#                 "number_of_layer_active": [number_of_layer_active],
#                 "number_of_layer_passive": [number_of_layer_passive],
#                 "surcharge_type": [surcharge_type],
#                 "surcharge_inputs": [surcharge_inputs],
#                 "formula_active": [Formula_active],
#                 "formula_passive": [Formula_passive],
#                 "soil_properties_active": [soil_properties_active],
#                 "soil_properties_passive": [soil_properties_passive],
#                 "ph_max": [ph_max],
#                 "Fb": [Fb],
#                 "timber_size": [timber_size],
#                 "FS": [FS],
#                 "Pile_spacing": [Pile_spacing],
#                 "allowable_deflection": [allowable_deflection],
#                 "Fy": [Fy],
#                 "E": [E],
#                 "selected_design_sections": [selected_design_sections]
#                 }


def input_single(input_values):
    # INPUT errors --> can be developed. now we have no error for inputs.
    # *** pile spacing need a limitation.

    # *** GENERAL INFORMATION ***

    product_id = input_values.get("product_id")
    user_id = input_values.get("user_id")
    unit_system = input_values.get("information").get("unit")
    title = input_values.get("information").get("title")
    jobNo = input_values.get("information").get("jobNo")
    designer = input_values.get("information").get("designer")
    checker = input_values.get("information").get("checker")
    company = input_values.get("information").get("company")
    client = input_values.get("information").get("client")
    date = input_values.get("information").get("date")
    comment = input_values.get("information").get("comment")
    other = input_values.get("information").get("other")

    project_information = [product_id, user_id, title, jobNo, designer, checker, company, client, date, comment, other]


    # *** GENERAL DATA ***

    FS = abs(float(input_values.get("data").get("General data").get("FS").get("value")))
    Fy = abs(float(input_values.get("data").get("General data").get("Fy").get("value")))
    E = abs(float(input_values.get("data").get("General data").get("E").get("value")))
    pile_spacing = abs(float(input_values.get("data").get("General data").get("Pile Spacing").get("value")))
    allowable_deflection = abs(
        float(input_values.get("data").get("General data").get("Allowable Deflection").get("value")))
    selected_sections = json.loads(input_values.get("data").get("General data").get("Sections").get("value")).get(
        "item").split(",")  # this value should be converted to a list.

    # *** SOIL PROPERTIES ***

    retaining_height = abs(float(input_values.get("data").get("Soil Properties").get("Retaining Height").get("value")))
    try:
        number_of_layer_active = abs(
            int(json.loads(input_values.get("data").get("Soil Properties").get("Soil Layer Number").get("value")).get(
                "item")))
    except:  # if formula = user defined --> this value not send.
        number_of_layer_active = 1
    if number_of_layer_active == 1:
        control_index = number_of_layer_active
    else:
        control_index = 0
    formula = json.loads(input_values.get("data").get("Soil Properties").get("Formula").get("value")).get(
        "item")
    Formula_passive = Formula_active = formula
    space = " "
    h_active = [
        abs(float(input_values.get("data").get("Soil Properties").get('Height of layer' + layer * space).get("value")))
        for layer in range(number_of_layer_active - 1)]
    if number_of_layer_active == 1:
        h_active.append(retaining_height)
    h_active.append(D)

    omega_active = [0 for i in range(number_of_layer_active)]

    water_active = []
    for layer in range(number_of_layer_active):
        try:
            water = input_values.get("data").get("General data").get("Water level at top of this layer?").get("value")
        except:  # checkbox input in site won't be sent if user don't select that.
            water = "No"
        water_active.append(water)
    EFPa_valid = True
    EFPp_valid = True
    Ka_valid = True
    gama_valid = True

    if formula == "User Defined":
        number_of_layer_active = 1
        water_active.append(water_active[0])
        EFPa = abs(
            float(input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Active").get("value")))
        EFPp = abs(
            float(input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Passive").get("value")))
        Ka_surcharge = abs(float(input_values.get("data").get("Soil Properties").get("Ka Surcharge").get("value")))
        hr = [retaining_height]
        hd = [D]

        soil_properties_active = [[EFPa, EFPa], Ka_surcharge]
        soil_properties_passive = [[EFPp, EFPa]]

        EFPa_valid = EFPa
        EFPp_valid = EFPp
        Ka_valid = Ka_surcharge

    elif formula == "Rankine" or formula == "Coulomb":
        gama_active = [
            abs(float(input_values.get("data").get("Soil Properties").get('γ' + layer * space).get(
                "value")))
            for layer in range(number_of_layer_active)]
        phi_active = [
            abs(float(input_values.get("data").get("Soil Properties").get('Φ' + layer * space).get(
                "value")))
            for layer in range(number_of_layer_active)]
        beta_active = []
        beta_passive = []
        for layer in range(number_of_layer_active):
            try:
                beta_active.append(
                    abs(float(input_values.get("data").get("Soil Properties").get('β active' + layer * space).get(
                        "value"))))
            except:
                beta_active.append(0)
            try:
                beta_passive.append(
                    abs(float(input_values.get("data").get("Soil Properties").get('β passive' + layer * space).get(
                        "value"))))
            except:
                beta_passive.append(0)
        delta_active = [0 for layer in range(number_of_layer_active)]
        for i in gama_active:
            if i == 0:
                gama_valid = 0  # then this value will go to the validation
        if formula == "Coulomb":
            delta_active.clear()
            for layer in range(number_of_layer_active):
                try:
                    delta_active.append(abs(float(
                        input_values.get("data").get("Soil Properties").get('δ' + layer * space).get("value"))))
                except:
                    delta_active.append(0)

    # elif formula == "Coulomb":
    #     gama_active = [
    #         abs(float(input_values.get("data").get("Soil Properties").get('γ' + layer * space).get(
    #             "value")))
    #         for layer in range(number_of_layer_active)]
    #     phi_active = [
    #         abs(float(input_values.get("data").get("Soil Properties").get('Φ' + layer * space).get(
    #             "value")))
    #         for layer in range(number_of_layer_active)]
    #     delta_active = [
    #         abs(float(input_values.get("data").get("Soil Properties").get('δ' + layer * space).get(
    #             "value")))
    #         for layer in range(number_of_layer_active)]
    #     beta_active = [
    #         abs(float(input_values.get("data").get("Soil Properties").get('β active' + layer * space).get(
    #             "value")))
    #         for layer in range(number_of_layer_active)]
    #     beta_passive = [
    #         abs(float(input_values.get("data").get("Soil Properties").get('β passive' + layer * space).get(
    #             "value")))
    #         for layer in range(number_of_layer_active)]
    #     for i in gama_active:
    #         if i == 0:
    #             gama_valid = 0  # then this value will go to the validation

    if formula != "User Defined" and retaining_height != 0 and gama_valid:
        hr, hd, number_of_layer_active, gama_active, phi_active, beta_active, omega_active, delta_active, water_active = edit_parameters(
            retaining_height, h_active, number_of_layer_active, gama_active, phi_active, beta_active,
            omega_active,
            delta_active, water_active)

        soil_properties_active = [gama_active, phi_active, "active", beta_active, omega_active,
                                  delta_active
                                  ]

        gama_passive = gama_active[len(hr):]
        phi_passive = phi_active[len(hr):]
        omega_passive = omega_active[len(hr):]
        delta_passive = delta_active[len(hr):]

        for i in range(len(beta_passive) - len(hd)):
            del beta_passive[i]

        soil_properties_passive = [gama_passive, phi_passive, "passive", beta_passive, omega_passive,
                                   delta_passive
                                   ]
    try:  # if gama was ok
        water_passive = water_active[len(hr):]
        number_of_layer_passive = len(hd)
        h_passive = hd
    except:  # if gama or retaining height equal to zero.
        hr = []
        hd = []
        water_passive = []
        number_of_layer_passive = []
        h_passive = []
        soil_properties_active = []
        soil_properties_passive = []

    # *** SURCHARGE ***
     # this part should be added in site ( must be checked! )
    try:
        surcharge_depth = abs(
            float(input_values.get("data").get("Surcharge").get("Surcharge Effective Depth").get("value")))
    except:
        surcharge_depth = retaining_height  # I should define it in site ***
    if surcharge_depth > retaining_height:  # surcharge has no effect under excavation line.(ASSUMED ACCORDING TO MANUAL FILE)
        surcharge_depth = retaining_height

    max_surcharge_site = 4
    surcharge_type = [
        json.loads(input_values.get("data").get("Surcharge").get("Load Type" + space * layer).get("value")).get(
            "item") for layer in range(max_surcharge_site)]

    q_all = []
    l1_all = []
    l2_all = []
    teta_all = []
    for i in range(len(surcharge_type)):
        if surcharge_type[i] == "Uniform":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append("")
            l2_all.append("")
            teta_all.append("")

        elif surcharge_type[i] == "Point Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            teta = abs(float(input_values.get("data").get("Surcharge").get('Ɵ' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append("")
            teta_all.append(teta)

        elif surcharge_type[i] == "Line Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))

            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append("")
            teta_all.append("")

        elif surcharge_type[i] == "Strip Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            l2 = abs(float(input_values.get("data").get("Surcharge").get('L2' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append(l2)
            teta_all.append("")

        else:
            q_all.append(0)
            l1_all.append(0)
            l2_all.append(0)
            teta_all.append(0)

    surcharge_inputs = [q_all, l1_all, l2_all, teta_all]

    #  *** LAGGING ***

    ph_max = abs(float(input_values.get("data").get("Lagging").get('Ph max').get(
        "value")))
    Fb = abs(float(input_values.get("data").get("Lagging").get('Fb').get(
        "value")))
    timber_size = json.loads(input_values.get("data").get("Lagging").get("Timber Size").get("value")).get("item")

    validation_dict = {"FS": FS, "Fy": Fy, "E": E, "Pile Spacing": pile_spacing,
                       "Allowable Deflection": allowable_deflection, "Retaining Height": retaining_height,
                       "Ph max": ph_max, "Fb": Fb, "γ": gama_valid, "EFPa": EFPa_valid, "EFPp": EFPp_valid,
                       "Ka surcharge": Ka_valid}
    status, input_errors = validation_zero(validation_dict)
    error_number = len(input_errors)
    error_description = input_errors
    input_validation = {"error_number": error_number,
                        "description": error_description}
    final_values = {"input_validation": input_validation,
                    "project_information": project_information,
                    "number_of_project": number_of_project,
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
                    "Pile_spacing": [pile_spacing],
                    "allowable_deflection": [allowable_deflection],
                    "Fy": [Fy],
                    "E": [E],
                    "selected_design_sections": [selected_sections]
                    }
    return final_values


# a = input_single(input2)

def validation_zero(item):
    errors = []
    values = list(item.values())
    keys = list(item.keys())
    for i in range(len(values)):
        if values[i] == 0:
            errors.append([f"{keys[i]} can not be zero!"])
    return not bool(errors), errors
