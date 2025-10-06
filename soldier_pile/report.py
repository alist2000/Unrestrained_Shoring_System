import pandas as pd
import pyarrow.feather as feather
from jinja2 import Environment, FileSystemLoader
import datetime
import math
import numpy as np
import pathlib

# This import assumes the other report file is in a specific sub-directory
from Unrestrained_Shoring_System.soldier_pile.front.report import surcharge_inputs, Formula, edit_equation, force_arm

# --- Define and Create Output Paths ---
# Get the directory where this script (report.py) is located.
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

# Define paths for the output directories relative to this script.
REPORTS_DIR = SCRIPT_DIR / "reports"
EXCEL_DIR = REPORTS_DIR / "excel"
TEMPLATE_DIR = REPORTS_DIR / "template"

# *** FIX: Create these directories if they don't exist to prevent OSError ***
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------------

def create_feather(z, value, title, excel_name):
    """Saves a pandas DataFrame to a feather file in the correct reports/excel directory."""
    value = list(map(lambda x: round(x, 3), value))
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])

    # Use the robust, absolute path
    output_path = EXCEL_DIR / f"{excel_name}.feather"
    df.to_feather(output_path)


def create_pdf_report(html_temp_file, template_vars):
    """
    Renders a Jinja2 template and saves it to the correct reports/template directory.
    Note: The loader's root is now the script's directory for robust template finding.
    """
    env = Environment(loader=FileSystemLoader(SCRIPT_DIR))
    template = env.get_template(html_temp_file)
    html_filled = template.render(template_vars)

    # Use the robust, absolute path for the output file
    output_path = TEMPLATE_DIR / 'Rep_Unrestrained_Filled.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_filled)


def report_final(input_values, Sx, Ax, M_max, V_max,
                 y_zero, k_or_EFPa, k_or_EFPp,
                 equations, D, h_list
                 ):
    # This function's logic remains the same as it primarily processes data
    # and calls the file-writing functions that we have already fixed.

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
        h = retaining_height_list[project]
        surcharge_depth = surcharge_depth_list[project]
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
        sections = ", ".join(selected_design_sections)

        ph_max = ph_max_list[project]
        Fb = Fb_list[project]
        timber_size = timber_size_list[project]

        soil_prop = []
        if formula_active != "User Defined":
            [gama_active, phi_active, state_active, beta_active, omega_active,
             delta_active] = soil_properties_active_list[project]
            soil_prop = [k_or_EFPa, k_or_EFPp, gama_active, phi_active, beta_active, [], delta_active, h_list]
            if formula_passive != "User Defined":
                [gama_passive, phi_passive, state_passive, beta_passive, omega_passive,
                 delta_passive] = soil_properties_passive_list[project]
                soil_prop[5] = beta_passive
        else:
            [EFPa, ka_surcharge] = soil_properties_active_list[project]
            soil_prop = [k_or_EFPa[0], k_or_EFPp[0], ka_surcharge]

        Formula(formula_active, soil_prop, h, unit_system)

        [product_id, user_id, title, jobNo, designer, checker, company, client, date, comment,
         other] = project_information

        if comment is None:
            comment = "-"
        if date is None:
            date = datetime.datetime.today().strftime('%Y-%m-%d')

        if unit_system == "us":
            length_unit, force_unit, k_force_unit = "ft", "lb", "kips"
            moment_unit, k_moment_unit, pressure_unit = "lb-ft", "kip-ft", "ksi"
            deflection_unit, density_unit, A_unit, s_unit = "in", "pcf", "in<sup>2</sup>", "in<sup>3</sup>"
        else:
            length_unit, force_unit, k_force_unit = "m", "N", "KN"
            moment_unit, k_moment_unit, pressure_unit = "N-m", "KN-m", "MPa"
            deflection_unit, density_unit, A_unit, s_unit = "mm", "N/m<sup>2</sup>", "mm<sup>2</sup>", "mm<sup>3</sup>"

        Mr, Md, d_equation = edit_equation(*equations)

        report_values = {
            "project_title": title, "designer": designer, "job_title": jobNo, "checker": checker,
            "company": company, "analysis_date": date, "comments": comment, "unit_system": unit_system.upper(),
            "E": E, "FS": FS, "Fb": Fb, "Fy": Fy, "pile_spacing": Pile_spacing,
            "allowable_deflection": allowable_deflection, "retaining_height": h, "Sections": sections,
            "Ph_max": ph_max, "timber_size": timber_size, "D_round": math.ceil(D), "D": round(D, 2),
            "first_D": round(D / 1.2, 2), "Sx_required": round(Sx, 1), "Ax_required": math.ceil(Ax),
            "M_max": round(M_max / 1000, 1), "shear_max": round(V_max / 1000, 1), "y_zero_shear": y_zero,
            "d_equation": d_equation, "Md": Md, "Mr": Mr, "moment_status": "Pass", "shear_status": "Pass",
            "length_unit": length_unit, "density_unit": density_unit, "force_unit": force_unit,
            "k_force_unit": k_force_unit, "moment_unit": moment_unit, "k_moment_unit": k_moment_unit,
            "deflection_unit": deflection_unit, "Ax_unit": A_unit, "Sx_unit": s_unit,
            "pressure_unit": pressure_unit, "ull": " &deg;"
        }
        return report_values


def report_force_arm_edit(forces, arms):
    new_forces = [forces[0][1]]
    new_arms = [arms[0][1]]
    for force_item in forces[1:-1]:
        new_forces.extend(force_item)
    for arm_item in arms[1:-1]:
        new_arms.extend(arm_item)
    new_forces.append(forces[-1][-1])
    new_arms.append(arms[-1][-1])
    return new_forces, new_arms


def report_force_arm(active_force, active_arm, passive_force, passive_arm, surcharge_force, surcharge_arm, unit_system):
    active_force, active_arm = report_force_arm_edit(active_force, active_arm)
    active_force.extend(surcharge_force)
    active_arm.extend(surcharge_arm)
    passive_force, passive_arm = report_force_arm_edit(passive_force, passive_arm)

    active_force = edit_equation(*active_force)
    active_arm = edit_equation(*active_arm)
    passive_force = edit_equation(*passive_force)
    passive_arm = edit_equation(*passive_arm)

    force_arm(active_force, active_arm, passive_force, passive_arm, unit_system)
