def output_single_solved(unit_system, general, specific):
    if unit_system == "us":
        deflection_unit = "in"
        length_unit = "ft"
        force_unit = "kips"
        moment_unit = "kips-ft"
        area_unit = "in^2"
        S_unit = "in^3"
    else:
        deflection_unit = "mm"
        length_unit = "m"
        force_unit = "KN"  # must be checked
        moment_unit = "KN-m"  # must be checked
        area_unit = "mm^2"
        S_unit = "mm^3"

    general_plot, general_values = general.values()
    #  create html for plots
    i = 1
    for plot in general_plot:
        plot.write_html(f"plot/general_output{i}.html",
                        full_html=False,
                        include_plotlyjs='cdn')
        # plot.write_image(f"plot/output{i}.png")
        i += 1

    specific_plot, specific_values = specific.values()
    number_of_section = len(specific_plot)
    #  create html for plots
    i = 1
    for plot in specific_plot:
        plot.write_html(f"plot/deflection_output{i}.html",
                        full_html=False,
                        include_plotlyjs='cdn')
        # plot.write_image(f"plot/output{i}.png")
        i += 1

    otitle = ["Cantilever Soldier Pile - Output Summary",
              "Final Solution Alternatives"]
    header_general = ["General Plots", "General Values"]
    header_specific = ["Section", "Deflection Plot", "Checks"]
    # file names
    # excels -> this titles will use for api and download excels.
    excel_general = ["load", "shear", "moment"]

    general_value_title = [f"Embedment Depth ( {length_unit} ) = ", f"maximum Shear ( {force_unit} ) = ",
                           f"maximum Moment ( {moment_unit} ) = ", f"Y zero Shear ( {length_unit} ) = ",
                           f"Required Area ( {area_unit} ) = ", f"Required Sx ( {S_unit} ) = "]
    output_general_values = []
    for i in range(len(general_values)):
        output_general_values.append(general_value_title[i] + str(round(general_values[i], 2)))

    output_specific_values = []
    excel_specific = []
    for i in range(number_of_section):
        specific_values_list = [specific_values[0][i],  # section name
                                f"Maximum Deflection ( {deflection_unit} ) = " + str(round(specific_values[1][i], 2)),
                                # max deflection
                                "DCR Moment = " + str(round(specific_values[2][i], 2)),  # DCR moment
                                "DCR Shear = " + str(round(specific_values[3][i], 2)),  # DCR shear
                                "DCR Deflection = " + str(round(specific_values[4][i], 2)),  # DCR deflection
                                # lagging
                                "Timber Size " + specific_values[5] + ": \n\n" + specific_values[6][
                                    i],
                                f"d = {specific_values[7][i]} ( {deflection_unit} )",
                                f"h = {specific_values[8][i]} ( {deflection_unit} )",
                                f"b = {specific_values[9][i]} ( {deflection_unit} )",
                                f"tw = {specific_values[10][i]} ( {deflection_unit} )",
                                f"tf = {specific_values[11][i]} ( {deflection_unit} )"]

        output_specific_values.append(specific_values_list)
        excel_specific.append("deflection" + str(i + 1))

    # file_name = []
    # for i in range(len(values)):
    #     filename_summary = "p" + str(product_id) + "u" + str(user_id) + "_" + "Solution" + str(
    #         i + 1) + "_SurchargeLoad_Report"
    #     filename_detail = "p" + str(product_id) + "u" + str(user_id) + "_" + "Solution" + str(
    #         i + 1) + "_SurchargeLoad_Report"
    #     file_name.append(filename_summary)
    #     file_name.append(filename_detail)
    titles = [otitle, header_general, header_specific, excel_general, excel_specific]
    values = [output_general_values, output_specific_values]
    output = [otitle, header_general, header_specific, general_plot, output_general_values, specific_plot,
              specific_values]

    return titles, values


def output_single_no_solution(error):
    print(error)
    otitle = ["Cantilever Soldier Pile - Output Summary",
              "Final Solution Alternatives"]
    header = ["Error NO.", "Description"]
    number_of_error = len(error)
    errors = []
    for i in range(number_of_error):
        errors.append((i + 1, error[i][0]))
    output = [otitle, header, errors]
    return output
