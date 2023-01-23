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
	<script>
      function ShowAndHide(id) {
        var x = document.getElementById(id);
        if (x.style.display == "none") {
          x.style.display = "block";
        } else {
          x.style.display = "none";
        }
      }
    </script>
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
	<style>
      .menu {
        background: #84c1ff;
        height: 4rem;
      }
      .menu ol {
        list-style-type: none;
        margin: 0 auto;
        padding: 0;
      }
      .menu > ol {
        max-width: 1000px;
        padding: 0 2rem;
        display: flex;
      }
      .menu > ol > .menu-item {
        flex: 1;
        padding: 0.75rem 0;
      }
      .menu > ol > .menu-item:after {
        content: "";
        position: absolute;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        bottom: 5px;
        left: calc(50% - 2px);
        background: #feceab;
        will-change: transform;
        transform: scale(0);
        transition: transform 0.2s ease;
      }
      .menu > ol > .menu-item:hover:after {
        transform: scale(1);
      }
      .menu-item {
        position: relative;
        line-height: 2.5rem;
        text-align: center;
      }
      .menu-item a {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        display: block;
        color: #fff;
      }
      .sub-menu .menu-item {
        padding: 0.75rem 0;
        background: #84c1ff;
        opacity: 0;
        transform-origin: bottom;
        animation: enter 0.2s ease forwards;
      }
      .sub-menu .menu-item:nth-child(1) {
        animation-duration: 0.2s;
        animation-delay: 0s;
      }
      .sub-menu .menu-item:nth-child(2) {
        animation-duration: 0.3s;
        animation-delay: 0.1s;
      }
      .sub-menu .menu-item:nth-child(3) {
        animation-duration: 0.4s;
        animation-delay: 0.2s;
      }
      .sub-menu .menu-item:hover {
        background: #c4ddff;
      }
      .sub-menu .menu-item a {
        padding: 0 0.75rem;
      }
      @media screen and (max-width: 600px) {
        .sub-menu .menu-item {
          background: #c06c84;
        }
      }

      @media screen and (max-width: 600px) {
        .menu {
          position: relative;
        }
        .menu:after {
          content: "";
          position: absolute;
          top: calc(50% - 2px);
          right: 1rem;
          width: 30px;
          height: 4px;
          background: #fff;
          box-shadow: 0 10px #fff, 0 -10px #fff;
        }
        .menu > ol {
          display: none;
          background: #f67280;
          flex-direction: column;
          justify-content: center;
          height: 100vh;
          animation: fade 0.2s ease-out;
        }
        .menu > ol > .menu-item {
          flex: 0;
          opacity: 0;
          animation: enter 0.3s ease-out forwards;
        }
        .menu > ol > .menu-item:nth-child(1) {
          animation-delay: 0s;
        }
        .menu > ol > .menu-item:nth-child(2) {
          animation-delay: 0.1s;
        }
        .menu > ol > .menu-item:nth-child(3) {
          animation-delay: 0.2s;
        }
        .menu > ol > .menu-item:nth-child(4) {
          animation-delay: 0.3s;
        }
        .menu > ol > .menu-item:nth-child(5) {
          animation-delay: 0.4s;
        }
        .menu > ol > .menu-item + .menu-item {
          margin-top: 0.75rem;
        }
        .menu > ol > .menu-item:after {
          left: auto;
          right: 1rem;
          bottom: calc(50% - 2px);
        }
        .menu > ol > .menu-item:hover {
          z-index: 1;
        }
        .menu:hover > ol {
          display: flex;
        }
        .menu:hover:after {
          box-shadow: none;
        }
      }

      .sub-menu {
        position: absolute;
        width: 100%;
        top: 100%;
        left: 0;
        display: none;
        z-index: 1;
      }
      .menu-item:hover > .sub-menu {
        display: block;
      }

      @media screen and (max-width: 600px) {
        .sub-menu {
          width: 100vw;
          left: -2rem;
          top: 50%;
          transform: translateY(-50%);
        }
      }

      html,
      * {
        box-sizing: border-box;
      }
      *:before,
      *:after {
        box-sizing: inherit;
      }

      a {
        text-decoration: none;
      }
      buttom {
        cursor: pointer;
      }
      @keyframes enter {
        from {
          opacity: 0;
          transform: scaleY(0.98) translateY(10px);
        }
        to {
          opacity: 1;
          transform: none;
        }
      }
      @keyframes fade {
        from {
          opacity: 0;
        }
        to {
          opacity: 1;
        }
      }
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
    empty_line = "<p></p>"

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
        drop_down_1 = """<nav ">
        <ol>
        <h3 class="menu-item" style="cursor: pointer">"""
        drop_down_2 = """<ol class="sub-menu">"""
        drop_down_end = """</ol>
              </h3>
             </ol>
            </nav>"""
        specific_t1_mid1 = """<td  class="menu" style="width: 20%; text-align: center; vertical-align: middle;  padding: 0.1%">"""
        specific_t1_mid2 = """<td  class="menu" style="width: 35%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid3 = """<td  class="menu" style="width: 45%; text-align: center; vertical-align: middle;  padding: 0.1%"><h3>"""
        specific_t1_mid_end = """</h3></td>"""
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
                                                <td style="width: 11.25%;text-align: center; vertical-align: middle", height="90" ><t2>
                                                """
        image_column = """
                                        <td style="width: 33.75%;text-align: center; vertical-align: middle;background-color: white" colspan="3"  ><img src="D:\git\Shoring\database\section_picture_para_new.jpg" height = "360"></td>
                                        """
        image_column_prop = """
                                                <td style="width: 11.25%;text-align: right; vertical-align: middle;background-color: white" ><t2>
                                                """
        end_column = """
                                </t2></td>
                                """
        # create titles
        s += specific_t1 + specific_t1_mid1 + drop_down_1 + titles[2][0] + drop_down_2
        for i in range(len(specific_values)):
            drop_down_3 = f"""<h3
              style="cursor: pointer"
              class="menu-item"
              ONCLICK="ShowAndHide('{specific_values[i][0]}')"
            >
              {specific_values[i][0]}
            </h3>"""
            s += drop_down_3

        s += drop_down_end
        s += specific_t1_mid2 + titles[2][1] + specific_t1_mid_end + specific_t1_mid3 + \
             titles[2][
                 2] + specific_t1_end

        for i in range(len(specific_values)):
            drop_down_values = f"""<div style="display:none" id="{specific_values[i][0]}">"""
            s += drop_down_values

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
            for j in range(2, 6):
                s += third_column + specific_values[i][j] + end_column
            s += tr_end + tr + first_column + specific_values[i][1] + end_column
            s += image_column_prop + specific_values[i][6] + empty_line + specific_values[i][7] + empty_line + \
                 specific_values[i][8] + empty_line + specific_values[i][9] + empty_line + specific_values[i][
                     10] + end_column
            s += image_column + tr_end
            s += div_end
            s += div_end

        return s

    S = general()
    export = html + head + body + div + title() + final_solution(S) + \
             div_end + body_end + html_end

    return export


def generate_html_response_cantilever_shoring_no_solution(output):
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
					<td style="width: 15%;padding: 5px;border: 5px solid white;background-color: #bfd6f6  ;"><t2b>
          """
        h2 = """
          </t2b></td>
          <td style="width: 85%;padding: 5px;border: 5px solid white;background-color: #bfd6f6  ;"><t2b>
          """
        h1_2_end = """
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

        h8 = """
        <td style="width: 15%;text-align: center;" ><t2>
        """
        h8_1 = """
                <td style="width: 85%;text-align: center;"><t2>
                """

        h9 = """
        </t2></td>
        """

        s = ""
        s += h1 + output[1][0] + h2 + output[1][1] + h1_2_end + h3
        for i in range(len(output[2])):
            s += tr + h8 + str(output[2][i][0]) + h9 + h8_1 + str(output[2][i][1]) + h9
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
     ['deflection1', 'deflection2', 'deflection3', 'deflection4']],
    [['Excavation depth ( ft ) = 24.1', 'maximum Shear ( lb ) = 51691.1', 'maximum Moment ( lb-ft ) = 165739.69',
      'Y zero Shear ( ft ) = 9.17', 'Required Area ( in^2 ) = 3.26', 'Required Sx ( in^3 ) = 83.71'], [
         ['W18X86', 'Maximum Deflection ( in ) = 0.46', 'DCR Moment = 0.5', 'DCR Shear = 0.13', 'DCR Deflection = 0.92',
          'lagging status for timber size 3 x 16: \n\nPass!', 'd = 24 ( in )', 'h = 18.4 ( in )', 'b = 11.1 ( in )',
          'tw = 0.48 ( in )', 'tf = 0.77 ( in )'],
         ['W21X68', 'Maximum Deflection ( in ) = 0.48', 'DCR Moment = 0.6', 'DCR Shear = 0.16', 'DCR Deflection = 0.95',
          'lagging status for timber size 3 x 16: \n\nPass!', 'd = 24 ( in )', 'h = 21.1 ( in )', 'b = 8.27 ( in )',
          'tw = 0.43 ( in )', 'tf = 0.685 ( in )'],
         ['W24X62', 'Maximum Deflection ( in ) = 0.45', 'DCR Moment = 0.64', 'DCR Shear = 0.18',
          'DCR Deflection = 0.91', 'lagging status for timber size 3 x 16: \n\nPass!', 'd = 24 ( in )',
          'h = 23.7 ( in )', 'b = 7.04 ( in )', 'tw = 0.43 ( in )', 'tf = 0.59 ( in )'],
         ['W27X84', 'Maximum Deflection ( in ) = 0.25', 'DCR Moment = 0.39', 'DCR Shear = 0.13',
          'DCR Deflection = 0.49', 'lagging status for timber size 3 x 16: \n\nPass!', 'd = 30.0 ( in )',
          'h = 26.7 ( in )', 'b = 10.0 ( in )', 'tw = 0.46 ( in )', 'tf = 0.64 ( in )']]])

generate_html_response_cantilever_shoring_output_no_solution = generate_html_response_cantilever_shoring_no_solution(
    [['Cantilever Soldier Pile - Output Summary', 'Final Solution Alternatives'], ['Error NO.', 'Description'],
     [(1, 'You must define at least one load!')]])
