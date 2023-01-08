max_general_plot = 3
general_plot = []
for i in range(max_general_plot):
    general_plot.append(open(f"../plot/general_output{i + 1}.html", "r").read())


def generate_html_response_cantilever_shoring(titles, values):
    # otitle = titles[0]
    # header_general = titles[1]
    # header_specific = titles[2]
    # excel_names = titles[3]

    general_values = values[0]
    specific_values = values[1]

    max_specific_plot = len(specific_values)  # this value can be changed according to site inputs
    specific_plot = []
    for i in range(max_specific_plot):
        specific_plot.append(open(f"../plot/deflection_output{i + 1}.html", "r").read())

    html = "<html>"
    html_end = "</html>"

    head = """<head>
	<title>Output Summary</title>
	<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
	<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
	<style type="text/css">
		* {font-size: 10px; }
		body {
			font: 10px Arial, Helvetica, sans-serif;
			line-height: 1.0;
		}
		@media print {
			.pagebreak { page-break-before: always; }
		}
		@page {
			size: letter;
			margin: 1.5cm;
			@bottom-right {
				content: "Page " counter(page) " of " counter(pages);
			}
		}
		.custom-page-start {
			margin-top: 0px;
			margin-bottom: 0px;
		}
		h1 {color: #2f4f6e; font-size: 15px;}
		h2 {
			background: #96B9D0; font-size: 13px;
			padding-top: 3px;
			padding-bottom: 3px;
			padding-left: 3px;
			margin-bottom: 5px; margin-top: 5px;
			margin-left: -1px; margin-right: -1px;
		}
		h3 {
			background: #84c1ff; font-size: 13px;
			font-size: 10px; 
			margin-bottom: -1px; margin-top: -1px;
			margin-left: -1px; margin-right: -1px;
			padding-top: 8px;
			padding-bottom: 8px;
			padding-left: 8px;
		}
		t1 {display: block; font-size: 15px; font-style: italic; padding-left: 3px;}
		t1b {font-size: 15px; font-style: italic; font-weight: bold;}
		t2 {font-size: 15px;}
		t2b {font-size: 15px;font-weight: bold;}
		p {font-size: 10px;}
		td {vertical-align: top;}
	</style>
  </head>"""

    body = "<body>"
    body_end = "</body>"
    div = """<div class="custom-page-start"> <hr>"""
    div_start = """<div class="custom-page-start" style="width: 50%; : padding-right: 5px">"""
    div_end = "</div>"
    h1 = "<h1>"
    h1_title = "<h1 style='font-size: 15px'>"
    h1_end = "</h1>"
    table = "<table border=1>"
    table_end = "</table>"
    tbody = "<tbody>"
    tbody_end = "</tbody>"
    hr = "<hr>"
    tr = "<tr>"
    tr_height_92 = '<tr height="92.4">'
    tr_height_115 = '<tr height="115.5">'
    tr = "<tr>"
    tr_end = "</tr>"
    th = "<th>"
    th_end = "</th>"
    td = "<td>"
    td_end = "</td>"

    def title():

        t1 = """		<table border="0" style="border-collapse: collapse; width: 100%;">
			<tbody>
				<tr>
					<td style="width: 100%;font-size: 15px;">
						<h2>"""

        t2 = """</h2>
            </td>
          </tr>
        </tbody>
      </table>
    <hr>"""

        title = h1_title + titles[0][0] + h1_end + t1 + titles[0][1] + t2

        return title

    m1 = """
                 <table border="0" style="border-collapse: collapse; width: 100%;">
                     <tbody>
                       <tr>
                         <td style="width: 100%;"><t1b></t1b></td>
                       </tr>
                     </tbody>
                   </table>
                     """
    h3 = """
                    <table border="1" bordercolor="#C0C0C0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
            			<tbody style="width: 100%;padding: 5px;border: 5px solid white;background-color: #e7eff6 ">
                      """
    start_table = """<table border="0" style="border-collapse: collapse; width: 100%;">
                    			<tbody>
                    				<tr>"""

    excel_start = """

                    					<td style="width: 7%;text-align: center; vertical-align: middle"><t1b>Download Values:</t1b></td>
                    					<td style="width: 7%;text-align: center; vertical-align: middle"><a href="http://civision.balafan.com:8010/report/unrestrained_shoring/excel/"""
    excel_start_specific = """

                    					<td style="width: 7%;text-align: left; vertical-align: middle"><t1b>Download Values:</t1b></td>
                    					<td style="width: 7%;text-align: left; vertical-align: middle"><a href="http://civision.balafan.com:8010/report/unrestrained_shoring/excel/"""

    excel_end = """
                            " target="_blank" ><img height = "20px" src="http://civision.balafan.com:8010/icon/PDF_Detailed"></a></td>
                            """
    excel_end_specific = """
                               " target="_blank" ><img height = "20px" src="http://civision.balafan.com:8010/icon/PDF_Detailed"></a></td><td style="width:76%"></td>
                               """
    end_table = """</tr>
                              </tbody>
                            </table>"""

    def general():
        general_t1 = """<table border="0" style="border-collapse: collapse; width: 100%;">
                			<tbody>
                				<tr><td style="width: 32.5%; vertical-align: text-top;font-size: 15px;  padding: 0px"><h3>
                				"""
        general_t1_end = """</h3></td>
                                  </tr>
                                </tbody>
                              </table>"""

        h2 = """
                  </t2b></td>
                  </tr>
                </tbody>
              </table>
                  """

        h4 = """
                  </tbody>
              </table>
                  """

        plot_row = """
                        <td style="width: 33.33%;text-align: center; vertical-align: middle" ><t2>
                        """
        three_inline = """
                                <td style="width: 33.33%;text-align: center; vertical-align: middle;height: 50px" ><t2>
                                """
        end_plot_row = end_three_inline = """
                        </t2></td>
                        """

        s = ""
        for header in range(len(titles[1])):
            s += general_t1 + titles[1][header] + general_t1_end
            s += m1
            s += h3
            if header == 0:  # general plots
                s += tr
                for plot in range(len(general_plot)):
                    s += plot_row + general_plot[plot] + end_plot_row

                #  download values for general plots
                s += start_table
                for plot_title in range(len(general_plot)):
                    s += excel_start + titles[3][plot_title] + excel_end
                s += end_table
            if header == 1:  # general values
                for i in range(len(general_values)):
                    if i == 0 or i == 3:  # three value in every line
                        s += tr
                    s += three_inline + general_values[i] + end_three_inline
                    if i == 2 or i == 5:
                        s += tr_end

        return s

    def final_solution(s):
        specific_t1 = """<table border="0" style="border-collapse: collapse; width: 100%;">
                    			<tbody>
                    				<tr>
                    				"""
        specific_t1_mid1 = """<td style="width: 20%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid2 = """<td style="width: 35%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid3 = """<td style="width: 45%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_end = """</h3></td>
                                      </tr>
                                    </tbody>
                                  </table>"""

        first_column = """
                                <td style="width: 20%;text-align: center; vertical-align: middle" ><t2>
                                """

        second_column = """
                                        <td style="width: 35%;text-align: center; vertical-align: middle", rowspan="2" ><t2>
                                        """
        third_column = """
                                                <td style="width: 15%;text-align: center; vertical-align: middle", rowspan="2" ><t2>
                                                """
        end_column = """
                                </t2></td>
                                """

        for i in range(len(specific_values)):
            # create titles
            s += specific_t1 + specific_t1_mid1 + titles[2][0] + specific_t1_mid2 + titles[2][1] + specific_t1_mid3 + \
                 titles[2][
                     2] + specific_t1_end

            # create reports
            s += start_table + excel_start_specific + titles[4][i] + excel_end_specific + end_table

            # add values
            s += m1
            s += h3
            ''' 0, 1 -> section name, max def
                2 -> PLOT
                3,4,5 -> DCR moment, shear and deflection
                '''
            s += tr
            s += first_column + specific_values[i][0] + end_column
            s += second_column + specific_plot[i] + end_column
            for j in range(2, 5):
                s += third_column + specific_values[i][j] + end_column
            s += tr_end + tr + first_column + specific_values[i][1] + end_column + tr_end

        return s

    S = general()
    export = html + head + body + div + title() + final_solution(S) + \
             div_end + body_end + html_end

    return export


def generate_html_response_surcharge_no_solution(output):
    html = "<html>"
    html_end = "</html>"

    head = """<head>
	<title>Output Summary</title>
	<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
	<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
	<style type="text/css">
		* {font-size: 10px; }
		body {
			font: 10px Arial, Helvetica, sans-serif;
			line-height: 1.0;
		}
		@media print {
			.pagebreak { page-break-before: always; }
		}
		@page {
			size: letter;
			margin: 1.5cm;
			@bottom-right {
				content: "Page " counter(page) " of " counter(pages);
			}
		}
		.custom-page-start {
			margin-top: 0px;
			margin-bottom: 0px;
		}
		h1 {color: #2f4f6e; font-size: 15px;}
		h2 {
			background: #96B9D0; font-size: 13px;
			padding-top: 3px;
			padding-bottom: 3px;
			padding-left: 3px;
			margin-bottom: 5px; margin-top: 5px;
			margin-left: -1px; margin-right: -1px;
		}
		h3 {
			background: #84c1ff; font-size: 13px;
			font-size: 10px; 
			margin-bottom: -1px; margin-top: -1px;
			margin-left: -1px; margin-right: -1px;
			padding-top: 8px;
			padding-bottom: 8px;
			padding-left: 8px;
		}
		t1 {display: block; font-size: 15px; font-style: italic; padding-left: 3px;}
		t1b {font-size: 15px; font-style: italic; font-weight: bold;}
		t2 {font-size: 15px;}
		t2b {font-size: 15px;font-weight: bold;}
		p {font-size: 10px;}
		td {vertical-align: top;}
	</style>
  </head>"""

    body = "<body>"
    body_end = "</body>"
    div = """<div class="custom-page-start"> <hr>"""
    div_start = """<div class="custom-page-start" style="width: 50%; : padding-right: 5px">"""
    div_end = "</div>"
    h1 = "<h1>"
    h1_title = "<h1 style='font-size: 15px'>"
    h1_end = "</h1>"
    table = "<table border=1>"
    table_end = "</table>"
    tbody = "<tbody>"
    tbody_end = "</tbody>"
    hr = "<hr>"
    tr = "<tr>"
    tr_end = "</tr>"
    th = "<th>"
    th_end = "</th>"
    td = "<td>"
    td_end = "</td>"

    def title():

        t1 = """		<table border="0" style="border-collapse: collapse; width: 100%;">
			<tbody>
				<tr>
					<td style="width: 100%;font-size: 15px;">
						<h2>"""

        t2 = """</h2>
            </td>
          </tr>
        </tbody>
      </table>
    <hr>"""

        title = h1_title + output[0][0] + h1_end + t1 + output[0][1] + t2

        return title

    def solutions():
        m1 = """
      <table border="0" style="border-collapse: collapse; width: 100%;">
          <tbody>
            <tr>
              <td style="width: 100%;"><t1b></t1b></td>
            </tr>
          </tbody>
        </table>
          """

        h1 = """
          <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
			<tbody>
				<tr>
					<td style="width: 100%;padding: 5px;border: 5px solid white;background-color: #bfd6f6  ;"><t2b>
          """
        h2 = """
          </t2b></td>
          </tr>
        </tbody>
      </table>
          """

        h3 = """
        <table border="1" bordercolor="#C0C0C0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
			<tbody style="width: 100%;padding: 5px;border: 5px solid white;background-color: #e7eff6 ">
          """

        h4 = """
          </tbody>
      </table>
          """

        h8 = f"""
        <td style="width: 10%;text-align: center;" ><t2>
        """
        h8_1 = f"""
                <td style="width: 10%;text-align: center;" colspan="{output[1][0] - 1}"><t2>
                """

        h9 = """
        </t2></td>
        """

        s = ""
        print(range(len(output[4])))
        for k in range(len(output[4])):
            c1 = 0
            c2 = 0
            c3 = 0
            # Table Solution Group Fields, Field labels, units and values
            for i in range(0, int(len(output[1]))):
                if i % 2 == 0:
                    s = s + h1 + str(output[1][i + 1]) + h2 + h3
                    s += tr
                    for j in range(output[1][i]):
                        if j == 0:
                            s = s + h8 + output[2][c1] + h9
                        else:
                            s = s + h8_1 + output[2][c1] + h9
                            break
                        c1 = c1 + 1
                    s += tr_end
                    for j in range(output[1][i]):
                        if j == 0:
                            s = s + tr
                        s = s + h8 + str(output[4][k][c3]) + h9
                        c3 = c3 + 1
                    s += tr_end
                    s = s + tbody_end + table_end
            s = s + m1 + hr

        return s

    export = html + head + body + div + title() + solutions() + \
             div_end + body_end + html_end

    return export


generate_html_response_cantilever_shoring_output = generate_html_response_cantilever_shoring(
    [['Cantilever Soldier Pile - Output Summary', 'Final Solution Alternatives'], ['General Plots', 'General Values'],
     ['Section', 'Deflection Plot', 'Checks'], ['load', 'shear', 'moment'],
     ['deflection0', 'deflection1', 'deflection2', 'deflection3']], [
        ['Excavation depth ( ft ) = 24.1', 'maximum Shear ( lb ) = 51691.1', 'maximum Moment ( lb-ft ) = 165739.69',
         'Y zero Shear ( ft ) = 9.17', 'Required Area ( in^2 ) = 3.26', 'Required Sx ( in^3 ) = 83.71'], [
            ['W18X86', 'Maximum Deflection ( in ) = 0.46', 'DCR Moment = 0.5', 'DCR Shear = 0.13',
             'DCR Deflection = 0.92'],
            ['W21X68', 'Maximum Deflection ( in ) = 0.48', 'DCR Moment = 0.6', 'DCR Shear = 0.16',
             'DCR Deflection = 0.95'],
            ['W24X62', 'Maximum Deflection ( in ) = 0.45', 'DCR Moment = 0.64', 'DCR Shear = 0.18',
             'DCR Deflection = 0.91'],
            ['W27X84', 'Maximum Deflection ( in ) = 0.25', 'DCR Moment = 0.39', 'DCR Shear = 0.13',
             'DCR Deflection = 0.49']]])
