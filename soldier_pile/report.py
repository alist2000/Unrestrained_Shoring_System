import pandas as pd
import pyarrow.feather as feather
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import datetime
import math
import numpy as np

from front.report import surcharge_inputs, Formula, edit_equation


# creating excel
def create_feather(z, value, title, excel_name):
    value = list(map(lambda x: round(x, 3), value))
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])
    df.to_feather("reports/excel/" + excel_name + ".feather")


def create_pdf_report(html_temp_file, template_vars):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(html_temp_file)
    html_filled = template.render(template_vars)
    with open('reports/template/Rep_Unrestrained_Filled.html', 'w') as f:
        f.write(html_filled)
    # return html_filled
    # file = open("report" + str(number) + ".html", "w")
    # file.write(html_filled)
    # file.close()
    # HTML(string=html_filled, base_url=__file__).write_pdf(pdf_name)


def report_final(input_values, Sx, Ax, M_max, V_max,
                 y_zero, k_or_EFPa, k_or_EFPp,
                 equations, D, h_list
                 ):
    # SITE INPUTS.
    # [input_errors, project_information, number_of_project, number_of_layer_list, unit_system, anchor_number_list,
    #  h_list, delta_h_list,
    #  gama_list,
    #  h_list_list, cohesive_properties_list, pressure_distribution_list,
    #  k_formula_list, soil_properties_list, there_is_water_list, water_started_list, surcharge_type_list,
    #  surcharge_depth_list,
    #  surcharge_inputs_list, tieback_spacing_list,
    #  anchor_angle_list, FS_list, E_list, Fy_list, allowable_deflection_list,
    #  selected_design_sections_list, ph_max_list, Fb_list, timber_size_list] = input_values.values()
    [input_validation, project_information, number_of_project, unit_system, delta_h_list, h_active_list, h_passive_list,
     hr_list, hd_list,
     retaining_height_list,
     surcharge_depth_list,
     water_active_list,
     water_passive_list,
     number_of_layer_active_list,
     number_of_layer_passive_list, surcharge_type_list, surcharge_inputs_list, formula_active_list,
     formula_passive_list, soil_properties_active_list,
     soil_properties_passive_list, ph_max_list, Fb_list, timber_size_list, FS_list,
     Pile_spacing_list, allowable_deflection_list, Fy_list, E_list,
     selected_design_sections_list] = input_values.values()
    for project in range(number_of_project):
        delta_h = delta_h_list[project]
        h_active = h_active_list[project]
        h_passive = h_passive_list[project]
        hr = hr_list[project]
        hd = hd_list[project]
        h = retaining_height_list[project]
        surcharge_depth = surcharge_depth_list[project]
        water_active = water_active_list[project]
        water_passive = water_passive_list[project]
        number_of_layer_active = number_of_layer_active_list[project]
        number_of_layer_passive = number_of_layer_passive_list[project]
        surcharge_type = surcharge_type_list[project]
        formula_active = formula_active_list[project]
        formula_passive = formula_passive_list[project]
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        surcharge_inputs(surcharge_type, q, l1, l2, teta, surcharge_depth, unit_system=unit_system)

        Pile_spacing = Pile_spacing_list[project]

        FS = FS_list[project]
        E = E_list[project]
        Fy = Fy_list[project]
        allowable_deflection = allowable_deflection_list[project]

        selected_design_sections = selected_design_sections_list[project]
        sections = ""
        for i in selected_design_sections:
            sections += i + ", "
        sections = sections[:-2]

        ph_max = ph_max_list[project]
        Fb = Fb_list[project]
        timber_size = timber_size_list[project]

        if formula_active != "User Defined":
            [gama_active, phi_active, state_active, beta_active, omega_active,
             delta_active
             ] = soil_properties_active_list[project]
        else:
            [EFPa, ka_surcharge] = soil_properties_active_list[project]
            soil_prop = [k_or_EFPa[0], k_or_EFPp[0], ka_surcharge]

        if formula_passive != "User Defined":
            [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
             delta_passive
             ] = soil_properties_passive_list[project]

            soil_prop = [k_or_EFPa, k_or_EFPp, gama_active, phi_active, beta_active, beta_passive, delta_active,
                         h_list]
        else:
            [EFPp] = soil_properties_passive_list[project]

        Formula(formula_active, soil_prop, h, unit_system)

        [product_id, user_id, title, jobNo, designer, checker, company, client, date, comment,
         other] = project_information

        if comment == None:
            comment = "-"
        if date == None:
            date = datetime.datetime.today().strftime('%Y-%m-%d')

        # UNITS
        if unit_system == "us":
            length_unit = "ft"
            force_unit = "lb"
            k_force_unit = "kips"
            moment_unit = "lb-ft"
            k_moment_unit = "kip-ft"
            pressure_unit = "ksi"
            deflection_unit = "in"
            density_unit = "pcf"
            A_unit = "in<sup>2</sup>"
            s_unit = "in<sup>3</sup>"
        else:
            length_unit = "m"
            force_unit = "N"
            k_force_unit = "KN"
            moment_unit = "N-m"
            k_moment_unit = "KN-m"
            pressure_unit = "MPa"
            deflection_unit = "mm"
            density_unit = "N/m<sup>2</sup>"
            A_unit = "mm<sup>2</sup>"
            s_unit = "mm<sup>3</sup>"
        # EXTRA (THEY ARE NOT FOR HERE)
        #       # PRESSURES
        #       # better appearance
        #       [soil_top_active, soil_end_active, soil_end_passive, water_pre_e_a, water_pre_e_p] = edit_equation(*pressures)
        #       # pressure picture
        #       if pressure_distribution == "Trapezoidal" and c == 0:
        #           distribution_pic = "template/picture_pressure1.html"
        #       elif pressure_distribution == "Trapezoidal" and c != 0:
        #           distribution_pic = "template/picture_pressure2.html"
        #       else:
        #           distribution_pic = "template/picture_pressure3.html"
        #
        #       # LOADS
        #       # better appearance
        #       [trapezoidal_force, force_soil1, force_soil2, surcharge_force, water_active_force, soil_passive_force,
        #        water_passive_force] = edit_equation(*loads)
        #       [trapezoidal_arm, arm_soil1, arm_soil2, surcharge_arm, water_active_arm, soil_passive_arm,
        #        water_passive_arm] = edit_equation(*arms)
        #       # force & arm picture
        #       if pressure_distribution == "Trapezoidal" and c == 0:
        #           force_pic = "template/picture_force1.html"
        #       elif pressure_distribution == "Trapezoidal" and c != 0:
        #           force_pic = "template/picture_force2.html"
        #       else:
        #           force_pic = "template/picture_force3.html"

        # EQUATIONS
        Mr = equations[0]
        Md = equations[1]
        d_equation = equations[2]
        [Mr, Md, d_equation] = edit_equation(Mr, Md, d_equation)

        # # WATER
        # if there_is_water == "No":
        #     water_started = "-"

        # # LAGGING
        # [d_concrete, lc, R_lagging, M_max_lagging, Sx_req_lagging, Sx_sup_lagging, lagging_status] = lagging_prop

        # FILLER DICT
        report_values = {
            # GENERAL INFORMATION
            "project_title": title, "designer": designer, "job_title": jobNo, "checker": checker,
            "company": company, "analysis_date": date, "comments": comment, "unit_system": unit_system,

            # GENERAL PROPERTIES
            "E": E, "FS": FS, "Fb": Fb, "Fy": Fy,
            "pile_spacing": Pile_spacing, "allowable_deflection": allowable_deflection,
            "retaining_height": h, "Sections": sections,

            # LAGGING INPUTS AND OUTPUTS
            "Ph_max": ph_max, "timber_size": timber_size,

            # IMPORTANT VALUES FROM ANALYSIS
            "D_round": math.ceil(D),
            "D": round(D, 2),
            "first_D": round(D / 1.2, 2),
            "Sx_required": round(Sx, 1), "Ax_required": math.ceil(Ax), "M_max": round(M_max / 1000, 1),
            "shear_max": round(V_max / 1000, 1),
            "y_zero_shear": y_zero, "d_equation": d_equation, "Md": Md, "Mr": Mr,

            # STATUSES --> IT'S ALWAYS Pass BECAUSE WE CHOOSE SECTION TO Pass IN MOMENT SHEAR AND DEFLECTION.
            "moment_status": "Pass",
            "shear_status": "Pass",

            # UNITS
            "length_unit": length_unit, "density_unit": density_unit, "force_unit": force_unit,
            "k_force_unit": k_force_unit,
            "moment_unit": moment_unit, "k_moment_unit": k_moment_unit,
            "deflection_unit": deflection_unit, "Ax_unit": A_unit, "Sx_unit": s_unit, "pressure_unit": pressure_unit,
            "ull": " &deg;"

        }
        return report_values





