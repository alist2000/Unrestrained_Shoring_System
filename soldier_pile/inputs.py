from sympy import symbols

# *** ATTENTION :  all input controls must be checked here.

number_of_project = 1

D = symbols("D")

unit_system = "us"

calculation_type = "Auto"  # or Manual

delta_h = 0.01
h_active = [10, D]
h_passive = [D]
retaining_height = 10
surcharge_depth = retaining_height
water_active = ["No", "No"]
water_passive = ["No"]
number_of_layer_active = len(h_active)
number_of_layer_passive = len(h_passive)

q_min = 72
surcharge_type = "uniform"
if surcharge_type == "uniform":
    q = 68
    if q < q_min:
        q = q_min
    surcharge_inputs = [q]
elif surcharge_type == "Point Load":
    q = ...
    if q < q_min:
        q = q_min
    l1 = ...
    teta = ...
    surcharge_inputs = [q, l1, teta]

elif surcharge_type == "Line Load":
    q = ...
    if q < q_min:
        q = q_min
    l1 = ...
    surcharge_inputs = [q, l1]

elif surcharge_type == "Strip Load":
    q = ...
    if q < q_min:
        q = q_min
    l1 = ...
    l2 = ...
    surcharge_inputs = [q, l1, l2]

Formula_active = "Coulomb"
if Formula_active != "User Defined":
    gama_active = [120, 125]
    phi_active = [34, 36]
    state_active = "active"
    beta_active = [0, 0]
    omega_active = [0, 0]
    delta_active = [0, 24]
    soil_properties_active = [gama_active, phi_active, state_active, beta_active, omega_active,
                              delta_active
                              ]

Formula_passive = "Coulomb"
if Formula_passive != "User Defined":
    gama_passive = [125]
    phi_passive = [36]
    theory_passive = "Coulomb"
    state_passive = "passive"
    beta_passive = [-32]
    omega_passive = [0]
    delta_passive = [24]
    soil_properties_passive = [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
                               delta_passive
                               ]
else:
    EFPa = ...  # gama * Ka
    soil_properties_active = [EFPa]
    EFPp = ...  # gama * Kp
    soil_properties_passive = [EFPp]

FS = 1.3
Pile_spacing = 6  # ft
allowable_deflection = 0.5  # in
Fy = 36  # ksi
E = 29000  # ksi

selected_design_sections = ["W18", "W21", "W24", "W27"]

# all values have length equal to number of project.

input_values = {"number_of_project": number_of_project,
                "unit_system": unit_system,
                "delta_h": [delta_h],
                "h_active": [h_active],
                "h_passive": [h_passive],
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
