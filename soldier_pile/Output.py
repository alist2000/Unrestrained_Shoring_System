def output_single_solved(unit_system, general, specific):
    if unit_system == "us":
        deflection_unit = "in"
        length_unit = "ft"
        force_unit = "lb"
        moment_unit = "lb-ft"
        area_unit = "in^2"
        S_unit = "in^3"
    else:
        deflection_unit = "mm"
        length_unit = "m"
        force_unit = "N"
        moment_unit = "N-m"
        area_unit = "mm^2"
        S_unit = "mm^3"

    general_plot, general_values = general.values()
    specific_plot, specific_values = specific.values()
    otitle = ["Cantilever Soldier Pile - Output Summary",
              "Final Solution Alternatives"]
    header_general = ["General Plots", "General Values"]
    header_specific = ["Deflection Plots", "Checks"]
    general_value_title = [f"Excavation depth ( {length_unit} ) = ", f"maximum Shear ( {force_unit} ) = ",
                           f"maximum Moment ( {moment_unit} ) = ", f"Y zero Shear ( {length_unit} ) = ",
                           f"Required Area ( {area_unit} ) = ", f"Required Sx ( {S_unit} ) = "]
    output_general_values = []
    for i in range(len(general_values)):
        output_general_values.append(general_value_title[i] + str(general_values[i]))

    # file_name = []
    # for i in range(len(values)):
    #     filename_summary = "p" + str(product_id) + "u" + str(user_id) + "_" + "Solution" + str(
    #         i + 1) + "_SurchargeLoad_Report"
    #     filename_detail = "p" + str(product_id) + "u" + str(user_id) + "_" + "Solution" + str(
    #         i + 1) + "_SurchargeLoad_Report"
    #     file_name.append(filename_summary)
    #     file_name.append(filename_detail)
    output = [otitle, general_plot, output_general_values, specific_plot, specific_values]

    return output
