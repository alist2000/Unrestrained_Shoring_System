from cgi import print_arguments
import copy
from operator import le
import pathlib

import sympy
import numpy as np
from Unrestrained_Shoring_System.soldier_pile.path import TEMPLATE_DIR, SCRIPT_DIR

# # --- Define Base Path for Report Templates ---
# # This ensures that paths are resolved correctly regardless of where this script is imported from.
# # The path is constructed relative to the location of this file.
# try:
#     # Get the directory containing this script (e.g., .../Unrestrained_Shoring_System/)
#     SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
#
#     # Define the path to the template directory, which is inside a 'reports' subfolder
#     TEMPLATE_DIR = SCRIPT_DIR / "reports" / "template"
#
#     # Ensure the directory exists, creating it if it doesn't. This prevents errors.
#     TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
#
# except NameError:
#     # Fallback for environments where __file__ is not defined (e.g., some interactive interpreters)
#     TEMPLATE_DIR = pathlib.Path("reports/template")
#     TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


def edit_equation(*equations):
    return_list = []
    for equation in equations:
        if type(equation) not in [float, int, str, np.float64, np.int64]:
            equation = round_number_equation(equation)
            equation = str(equation)
            equation = equation.replace("**", "<sup>")
            equation = edit_power(equation)
            equation = equation.replace("*", "&times;")
            return_list.append(equation)
        else:
            if type(equation) in [float, int, np.float64, np.int64]:
                equation = round(equation, 2)
            return_list.append(equation)
    return return_list


def round_number_equation(equation):
    new_args = ()
    for i in equation.args:

        if type(i) == sympy.core.Float:
            i = round(i, 2)
        elif type(i) == sympy.core.mul.Mul:
            new_args2 = ()
            for j in i.args:
                if type(j) == sympy.core.Float:
                    j = round(j, 2)
                new_args2 += (j,)
            i = i.func(*new_args2)

        new_args += (i,)

    edited_equation = equation.func(*new_args)
    return edited_equation


def edit_power(equation):
    equation_list_index = []
    for i in range(len(equation)):
        if equation[i] == ">":
            equation_list_index.append(i + 2)

    first_index = 0
    equation_list = []
    for i in range(len(equation_list_index)):
        equation_list.append(equation[first_index:equation_list_index[i]] + "</sup>")
        first_index += equation_list_index[i]
        if i:
            first_index -= equation_list_index[i - 1]
    try:
        if equation_list_index[-1] != len(equation):
            equation_list.append(equation[equation_list_index[-1]:])
    except:
        pass
    equation_new = ""
    for i in equation_list:
        equation_new += i
    if equation_new:
        return equation_new
    else:
        return equation


def surcharge_inputs(surcharge_type, q, l1, l2, teta, surcharge_depth, unit_system):
    surcharge_depth = round(surcharge_depth, 2)
    if unit_system == "us":
        length_unit = "ft"
        q_point = "lb"
        q_line = "lb/ft"
        q_strip = "lb/ft<sup>2</sup>"
    else:
        length_unit = "m"
        q_point = "lb"
        q_line = "N/m"
        q_strip = "N/m<sup>2</sup>"

    number_of_surcharge = 0
    for i in range(len(surcharge_type)):
        if surcharge_type[i] != "No Load":
            number_of_surcharge += 1

    table = f"""<tr>
            <td style="width: 25%;">
                <t1>Number of Surcharge Load:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{number_of_surcharge}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Surcharge Depth:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{surcharge_depth} {length_unit}</t2>
            </td>
        </tr>
        """
    for i in range(len(surcharge_type)):
        if surcharge_type[i] != "No Load":
            if "Point" in surcharge_type[i]:
                q_unit = q_point
            elif "Line" in surcharge_type[i]:
                q_unit = q_line
            else:
                q_unit = q_strip
            if l1[i] == "" or l1[i] is None:
                l1[i] = "-"

            if l2[i] == "" or l2[i] is None:
                l2[i] = "-"

            if teta[i] == "" or teta[i] is None:
                teta[i] = "-"
            table += f"""<tr>
                <td style="width: 25%;">
                    <t1>Load Type:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{surcharge_type[i]}</t2>
                </td>
                <td style="width: 25%;">
                    <t1>q:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{round(q[i], 2)} {q_unit}</t2>
                </td>
            </tr>
            <tr>
                <td style="width: 25%;">
                    <t1>L1:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{l1[i]} {length_unit}</t2>
                </td>
                <td style="width: 25%;">
                    <t1>L2:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{l2[i]} {length_unit}</t2>
                </td>
            </tr>
            <tr>
                <td style="width: 25%;">
                    <t1>&#952;:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{teta[i]} &deg;</t2>
                </td>
                <td style="width: 25%;">
                    <t1></t1>
                </td>
                <td style="width: 25%;">
                    <t2></t2>
                </td>
            </tr>"""

    if number_of_surcharge == 0:
        table += """<tr>
                <td style="width: 25%;">
                    <t1>There is No Surcharge Load.</t1>
                </td>

            </tr>"""

    # SURCHARGE FORMULA
    surcharge_type_set = set(surcharge_type)
    surcharge_type_set.discard("No Load")
    table2 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script type="text/javascript" id="MathJax-script" async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    </script>
    <title>Document</title>
</head>
<body>"""
    for load in surcharge_type_set:
        if load == "Uniform":
            table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{load}</th>
            </td>
        </tr>
        </tbody> </table>
        <table><tbody>
        <tr>
            <td>&#963;<sub>h</sub> = K<sub>a</sub> &#215; Q </td>
          </tr>

        </tbody>
    </table>"""

        elif load == "Point Load":
            table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{load}</th>
            </td>
        </tr> </tbody></table>""" + """<table><tbody><tr>
            <td style="text-align: left;">
                For m &#8804; 0.4:
                </td>
            </tr>
          <tr>
            <td>
               <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <semantics>
    <mrow>
      <msub>
        <mi>&#x3C3;</mi>
        <mi>h</mi>
      </msub>
      <mo>=</mo>
      <mn>0.28</mn>
      <mrow data-mjx-texclass="ORD">
        <mfrac>
          <mrow data-mjx-texclass="ORD">
            <msub>
              <mi>Q</mi>
              <mi>p</mi>
            </msub>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <msup>
              <mi>H</mi>
              <mn>2</mn>
            </msup>
          </mrow>
        </mfrac>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mfrac>
          <msup>
            <mi>n</mi>
            <mn>2</mn>
          </msup>
          <mrow data-mjx-texclass="ORD">
            <mo stretchy="false">(</mo>
            <mn>0.16</mn>
            <mo>+</mo>
            <msup>
              <mi>n</mi>
              <mn>2</mn>
            </msup>
            <msup>
              <mo stretchy="false">)</mo>
              <mn>3</mn>
            </msup>
          </mrow>
        </mfrac>
      </mrow>
      <mo>.</mo>
    </mrow>
    <annotation encoding="application/x-tex">\sigma_h = 0.28{ {Q_p} \over {H^2}}{n^2 \over {(0.16 + n^2)^3} }.</annotation>
  </semantics>
</math>
                </td>
          </tr>
          <tr>
            <td style="text-align: left;">
                For m > 0.4:
                </td>
            </tr>
          <tr>
            <td >
                <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <semantics>
    <mrow>
      <msub>
        <mi>&#x3C3;</mi>
        <mi>h</mi>
      </msub>
      <mo>=</mo>
      <mn>1.77</mn>
      <mrow data-mjx-texclass="ORD">
        <mfrac>
          <mrow data-mjx-texclass="ORD">
            <msub>
              <mi>Q</mi>
              <mi>p</mi>
            </msub>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <msup>
              <mi>H</mi>
              <mn>2</mn>
            </msup>
          </mrow>
        </mfrac>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mfrac>
          <mrow>
            <msup>
              <mi>n</
              <mn>2</mn>
            </msup>
            <msup>
              <mi>m</mi>
              <mn>2</mn>
            </msup>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <mo stretchy="false">(</mo>
            <msup>
              <mi>m</mi>
              <mn>2</mn>
            </msup>
            <mo>+</mo>
            <msup>
              <mi>n</mi>
              <mn>2</mn>
            </msup>
            <msup>
              <mo stretchy="false">)</mo>
              <mn>3</mn>
            </msup>
          </mrow>
        </mfrac>
      </mrow>
      <mo>.</mo>
    </mrow>
    <annotation encoding="application/x-tex">\sigma_h = 1.77{{Q_p} \over {H^2}}{n^2 m^2 \over {(m^2 + n^2)^3} }.</annotation>
  </semantics>
</math>
                </td>
          </tr>

        </tbody>
    </table>"""
        elif load == "Line Load":
            table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{load} </th>
            </td>
        </tr>
        </tbody>
    </table>
    <table>
        <tbody>
        <tr>
            <td style="text-align: left;">
                For m &#8804; 0.4:
                </td>
            </tr>
          <tr> """ + """<td>
               <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub>
    <mi>&#x3C3;</mi>
    <mi>h</mi>
  </msub>
  <mo>=</mo>
  <mrow data-mjx-texclass="ORD">
    <mfrac>
      <mrow data-mjx-texclass="ORD">
        <msub>
          <mi>Q</mi>
          <mi>l</mi>
        </msub>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mi>H</mi>
      </mrow>
    </mfrac>
  </mrow>
  <mrow data-mjx-texclass="ORD">
    <mfrac>
      <mrow>
        <mn>0.2</mn>
        <mi>n</mi>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mo stretchy="false">(</mo>
        <mn>0.16</mn>
        <mo>+</mo>
        <msup>
          <mi>n</mi>
          <mn>2</mn>
        </msup>
        <msup>
          <mo stretchy="false">)</mo>
          <mn>2</mn>
        </msup>
      </mrow>
    </mfrac>
  </mrow>
  <mo>.</mo>
</math>
                </td>
          </tr>
          <tr>
            <td style="text-align: left;">
                For m > 0.4:
                </td>
            </tr>
          <tr>
            <td >
                <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub>
    <mi>&#x3C3;</mi>
    <mi>h</mi>
  </msub>
  <mo>=</mo>
  <mn>1.28</mn>
  <mrow data-mjx-texclass="ORD">
    <mfrac>
      <mrow data-mjx-texclass="ORD">
        <msub>
          <mi>Q</mi>
          <mi>l</mi>
        </msub>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mi>H</mi>
      </mrow>
    </mfrac>
  </mrow>
  <mrow data-mjx-texclass="ORD">
    <mfrac>
      <mrow>
        <msup>
          <mi>m</mi>
          <mn>2</mn>
        </msup>
        <mi>n</mi>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mo stretchy="false">(</mo>
        <msup>
          <mi>m</mi>
          <mn>2</mn>
        </msup>
        <mo>+</mo>
        <msup>
          <mi>n</mi>
          <mn>2</mn>
        </msup>
        <msup>
          <mo stretchy="false">)</mo>
          <mn>2</mn>
        </msup>
      </mrow>
    </mfrac>
  </mrow>
  <mo>.</mo>
</math>
                </td>
          </tr>
        </tbody>
    </table>"""
        elif load == "Strip Load":
            table2 += f"""
            <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{load}</th>
            </td>
        </tr>
        </tbody>
    </table> """ + """<table>
        <tbody>
          <tr>
            <td>
                <math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <semantics>
    <mrow>
      <msub>
        <mi>&#x3C3;</mi>
        <mi>h</mi>
      </msub>
      <mo>=</mo>
      <mrow data-mjx-texclass="ORD">
        <mfrac>
          <mrow data-mjx-texclass="ORD">
            <mn>2</mn>
            <mi>Q</mi>
          </mrow>
          <mrow data-mjx-texclass="ORD">
            <mi>&#x3C0;</mi>
          </mrow>
        </mfrac>
      </mrow>
      <mrow data-mjx-texclass="ORD">
        <mo stretchy="false">[</mo>
        <msub>
          <mrow data-mjx-texclass="ORD">
            <mi data-mjx-variant="-tex-calligraphic" mathvariant="script">B</mi>
          </mrow>
          <mi>R</mi>
        </msub>
        <mo>&#x2212;</mo>
        <mi>sin</mi>
        <mo data-mjx-texclass="NONE">&#x2061;</mo>
        <mrow data-mjx-texclass="ORD">
          <mi data-mjx-variant="-tex-calligraphic" mathvariant="script">B</mi>
        </mrow>
        <mi>cos</mi>
        <mo data-mjx-texclass="NONE">&#x2061;</mo>
        <mo stretchy="false">(</mo>
        <mn>2</mn>
        <mrow data-mjx-texclass="ORD">
          <mi data-mjx-variant="-tex-calligraphic" mathvariant="script">a</mi>
        </mrow>
        <mo stretchy="false">)</mo>
        <mo stretchy="false">]</mo>
      </mrow>
      <mo>.</mo>
    </mrow>
    <annotation encoding="application/x-tex">\sigma_h = { {2Q} \over {\pi}}{[\mathcal{B}_R - \sin\mathcal{B}\cos(2\mathcal{a})]}.</annotation>
  </semantics>
</math>
                </td>
          </tr>
        </tbody>
    </table>"""
    table2 += """</body>
</html>"""

    # Use with statement for safer file handling and constructed paths
    with open(TEMPLATE_DIR / "surcharge_input.html", "w") as f:
        f.write(table)
    with open(TEMPLATE_DIR / "surcharge_formula.html", "w") as f:
        f.write(table2)


def Formula(formula, soil_prop, retaining_height, unit_system):
    if unit_system == "us":
        length_unit = "ft"
        density_unit = "pcf"
        pressure_unit = "psf"
    else:
        length_unit = "m"
        density_unit = "N/m<sup>3</sup>"
        pressure_unit = "N/m<sup>2</sup>"

    if formula == "User Defined":
        [EFPa, EFPp, ka_surcharge] = soil_prop
        table_properties = f"""<tbody>
        <tr>
            <td style="width: 25%;">
                <t1>Retaining Height:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{retaining_height} {length_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Number of Soil Layer:</t1>
            </td>
            <td style="width: 25%;">
                <t2> 1 </t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>EFP<sub>a</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{EFPa[0]} {density_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>EFP<sub>p</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{EFPp[0]} {density_unit}</t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>K<sub>a</sub> Surcharge:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{ka_surcharge}</t2>
            </td>
            <td style="width: 25%;">
                <t1></t1>
            </td>
            <td style="width: 25%;">
                <t2></t2>
            </td>

        </tr>

        </tbody>"""
        table_main = f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 30%;">
                <t1>Formula: {formula}</t1>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>EFP<sub>a</sub></em>: {EFPa[0]} {density_unit}
                </t2>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>EFP<sub>p</sub></em>: {EFPp[0]} {density_unit}
                </t2>
            </td>
        </tr>
        </tbody>"""
    else:
        [ka, kp, gama, phi, beta_active, beta_passive, delta, heights] = soil_prop
        heights[-1] = "-"
        layer_number = len(gama)  # or any item in soil prop -> all of them have same length
        for i in soil_prop:
            if i is None or i == "":
                i = 0
        table_properties1 = f"""<tbody>
        <tr>
            <td style="width: 25%;">
                <t1>Retaining Height:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{retaining_height} {length_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Number of Soil Layer:</t1>
            </td>
            <td style="width: 25%;">
                <t2> {layer_number} </t2>
            </td>
        </tr>"""
        table_properties2 = ""
        len_passive = len(beta_passive)
        for i in range(layer_number - len_passive):
            beta_passive.insert(0, 0)
        for i in range(layer_number):
            table_properties2 += f"""
                <tr style="background-color:#CEE5F2">
                    <td style="width: 25%;">
                        <t1>Layer Number:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{i + 1}</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1>Height of Layer:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{heights[i]} {length_unit}</t2>
                    </td>
                </tr>
                <tr>
                    <td style="width: 25%;">
                        <t1>&#611;:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{gama[i]} {density_unit}</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1>&Phi;:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{phi[i]} &deg;</t2>
                    </td>
                </tr>
                <tr>
                    <td style="width: 25%;">
                        <t1>&#946; Active:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{beta_active[i]} &deg;</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1>&#946; Passive:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{beta_passive[i]} &deg;</t2>
                    </td>
                </tr>
                <tr>
                    <td style="width: 25%;">
                        <t1>&#948;:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{delta[i]} &deg;</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1></t1>
                    </td>
                    <td style="width: 25%;">
                        <t2></t2>
                    </td>

                </tr>

                </tbody>"""
        table_properties = table_properties1 + table_properties2

        table = """<tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Rankine Theory</t1>
            </td>
            <td style="width: 85%;">
                <t2>
                </t2>
            </td>
        </tr>
        </tbody>
    </table>

    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 70%;">
            $$K_a = {cos\beta {cos\beta - \sqrt{cos^2\beta-cos^2\phi} \over cos\beta + \sqrt{cos^2\beta-cos^2\phi}}}.$$
            </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        <tr>
            <td style="width: 70%;">
                $$K_p = {cos\beta {cos\beta + \sqrt{cos^2\beta-cos^2\phi} \over cos\beta - \sqrt{cos^2\beta-cos^2\phi}}}.$$
            </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Coulomb Theory</t1>
            </td>
            <td style="width: 85%;">
                <t2>
                </t2>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 70%;">
            $$K_a = {cos^2(\phi - \omega)\over cos^2\omega cos(\delta + \omega)[1 + \sqrt{sin(\delta + \phi) sin(\phi - \beta) \over cos(\delta + \omega) cos(\omega - \beta)}]^2}.$$
                     </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        <tr>
            <td style="width: 70%;">
                $$K_p = {cos^2(\phi + \omega)\over cos^2\omega cos(\delta - \omega)[1 - \sqrt{sin(\delta + \phi) sin(\phi + \beta) \over cos(\delta - \omega) cos(\beta - \omega)}]^2}.$$
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        </tbody>
    </table>
    """
        ka_string, kp_string = "", ""
        for i in ka:
            ka_string += str(round(i, 3)) + ", "
        ka_string = ka_string[:-2]
        for i in kp:
            kp_string += str(round(i, 3)) + ", "
        kp_string = kp_string[:-2]
        table2 = f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 30%;">
                <t1>Formula: {formula}</t1>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>K<sub>a</sub></em>: {ka_string}
                </t2>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>K<sub>p</sub></em>: {kp_string}
                </t2>
            </td>
        </tr>
        </tbody>"""
        table_main = table + table2

    with open(TEMPLATE_DIR / "soil_properties.html", "w") as f:
        f.write(table_properties)
    with open(TEMPLATE_DIR / "formula.html", "w") as f:
        f.write(table_main)


def section_deflection(unit_system, fy, section, A, Sx, Ix, V_max, M_max, deflection_max, allowable_deflection, number):
    deflection_max = round(deflection_max, 2)

    cross = section.find("X")
    part1 = section[:cross]
    part2 = section[cross + 1:]
    section = part1 + "&#215;" + part2

    pof = """0.25D <sub> 0 </sub>"""  # in general
    if unit_system == "us":
        fb = round(M_max * 12 / (Sx * 1000), 2)
        fb_unit = "ksi"
        fv = round(V_max / (A * 1000), 2)
        fv_unit = "ksi"
        force_unit = "lb"
        moment_unit = "lb-ft"
        deflection_unit = "in"
        A_unit = "in<sup>2</sup>"
        s_unit = "in<sup>3</sup>"
        I_unit = "in<sup>4</sup>"
    else:
        fb = round(M_max * 1000 / Sx)
        fb_unit = "Mpa"
        fv = round(V_max / A, 2)
        fv_unit = "MPa"
        force_unit = "N"
        moment_unit = "N-m"
        deflection_unit = "mm"
        A_unit = "mm<sup>2</sup>"
        s_unit = "mm<sup>3</sup>"
        I_unit = "mm<sup>4</sup>"

    # Corrected relative path for the image source
    # The HTML is in 'reports/template', the plot is in 'plot'. Path should be '../../plot/'
    img_src = f"../plot/deflection_output{str(number)}.png"

    table = f"""<table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 100%;"><h3>4.8 Section Design</h3></td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 25%;">
                    <b> Use: {section}:</b>
                </td>
                <td style="width: 25%;">
                    <t1> S<sub>x</sub> = {Sx} {s_unit}</t1>
                </td>
                <td style="width: 25%;">
                    <t1> I<sub>x</sub> = {Ix} {I_unit}</t1>
                </td>
                <td style="width: 25%;">
                    <t1> A = {A} {A_unit}</t1>
                </td>
            </tr>
            </tbody>
            </table>
            <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 50%;">
                    <t1> f<sub>v</sub>=V<sub>max</sub>/A ={fv} {fv_unit}</t1>
                </td>
                <td style="width: 50%;"></td>
            </tr>
            <tr>
                <td style="width: 30%;">
                    <t1> f<sub>v,max</sub>= 0.44 &#215; Fy = {0.44 * fy}</t1>
                </td>
                <td style="width: 70%;">
                    <b>{section} is satisfactory in shear</b>
                </td>
            </tr>
            <tr>
                <td style="width: 50%;">
                    <t1> f<sub>b</sub>=M<sub>max</sub>/S ={fb} {fb_unit}</t1>
                </td>
                <td style="width: 50%;"></td>
            </tr>
            <tr>
                <td style="width: 30%;">
                    <t1> f<sub>b,max</sub>= 0.66 &#215; Fy = {0.66 * fy}</t1>
                </td>
                <td style="width: 70%;">
                    <b>{section} is satisfactory in moment</b>
                </td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 100%;"><h3>4.9 Deflection Check</h3></td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="text-align: justify;text-justify: inter-word;">The deflection of the restrained soldier pile
                    is calculated using the moment area method, and the
                    deflection diagram is shown below. The maximum allowable deflection
                    is <b>{allowable_deflection} {deflection_unit}</b>; thus, section <b>{section}</b> satisfies the deflection criterion. The point of fixity is at <b>{pof}</b> below the
                    excavation line, per soil report.
                </td>
            </tr>
            </tbody>
        </table>

        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 50%;">
                    <b> Deflection<sub>max</sub> = {deflection_max} {deflection_unit}
                    </b>
                </td>
                <td style="width: 50%;">
                </td>
            </tr>
            <tr>
                <td style="width: 100%; text-align: center;">
                    <img style="width: auto; height: 370;  margin-top:0px;"
                         src="{img_src}"
                         alt="shear diagram">

            </tr>
            </tbody>
        </table>"""

    print("CHECK THIS OUT", TEMPLATE_DIR / f"section_deflection{number}.html")
    with open(TEMPLATE_DIR / f"section_deflection{number}.html", "w") as f:
        f.write(table)


def DCRs(DCR_moment, DCR_shear, DCR_deflection, DCR_lagging, lagging_status, number):
    DCR_moment = round(DCR_moment, 3)
    DCR_shear = round(DCR_shear, 3)
    DCR_deflection = round(DCR_deflection, 3)
    DCR_lagging = round(DCR_lagging, 3)
    moment_status = shear_status = deflection_status = "Pass"
    table = f"""<tr>
            <td style="width: 50%;">
                <t1b></t1b>
            </td>
            <td style="width: 20%; text-align: center;">
                <t1b>DCR</t1b>
            </td>
            <td style="width: 5%; text-align: center;">
                <t1b>Status</t1b>
            </td>
            <td style="width: 20%; text-align: center;">
                <t1b></t1b>
            </td>
            <td style="width: 5%; text-align: center;">
                <t1b></t1b>
            </td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Moment</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_moment}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{moment_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Shear</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_shear}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{shear_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Deflection</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_deflection}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{deflection_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Lagging (Moment Design)</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_lagging}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{lagging_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>"""

    with open(TEMPLATE_DIR / f"DCRs{number}.html", "w") as f:
        f.write(table)


def deflection_output(deflection_max, unit_system, number):
    deflection_max = round(deflection_max, 2)
    if unit_system == "us":
        deflection_unit = "in"
    else:
        deflection_unit = "mm"
    deflection_table2 = f"""<td style="width: 20%;">
                <t1b>Deflection Max</t1b>
            </td>
            <td style="width: 80%;">
                <t2>
                    {deflection_max} {deflection_unit}
                </t2>
            </td>"""

    with open(TEMPLATE_DIR / f"deflection_max{number}.html", "w") as f:
        f.write(deflection_table2)


def lagging_output(unit_system, spacing, d_pile, lc, ph, R, M_max, S_req, timber_size, S_sup, lagging_status, number):
    M_max = round(M_max / 1000, 1)
    S_req = round(S_req, 1)
    S_sup = round(S_sup, 1)
    lc = round(lc, 1)
    R = round(R, 1)

    if unit_system == "us":
        length_unit = "ft"
        density_unit = "pcf"
        force_unit = "lb"
        Sx_unit = "in<sup>3</sup>"
        moment_unit = "kip-ft"
    else:
        length_unit = "m"
        density_unit = "N/m<sup>3</sup>"
        force_unit = "N"
        Sx_unit = "mm<sup>3</sup>"
        moment_unit = "KN-m"

    table = f"""<table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 25%;">
                <t1> Pile Spacing:</t1>
            </td>
            <td style="width: 25%;">
                <t1> {spacing} {length_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> d<sub>pile</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {d_pile} {length_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1> L<sub>c</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t1> {lc} {length_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> PH<sub>max</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {ph} {density_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1> R = 0.5 &#215; (PH &#215;L<sub>c</sub>/2):</t1>
            </td>
            <td style="width: 25%;">
                <t1> {R} {force_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> M<sub>max</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {M_max} {moment_unit}</t1>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 100%;">
                <t1> S<sub>required</sub>= M<sub>max</sub>/F<sub>b</sub>= {S_req} {Sx_unit}</t1>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Try</t1>
            </td>
            <td style="width: 85%;">
                <t2>{timber_size} :
                </t2>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 100%;">
                <t1> S<sub>supplied</sub> = {S_sup} {Sx_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 100%;">
                <t1> Timber Moment Design: <b>{lagging_status}</b></t1>
            </td>
        </tr>
        </tbody>
    </table>"""
    with open(TEMPLATE_DIR / f"lagging_output{number}.html", "w") as f:
        f.write(table)


def pressure_table(active_pressure, passive_pressure, h_active, h_passive, unit_system):
    if unit_system == "us":
        pressure_unit = "Ksi"
    else:
        pressure_unit = "MPa"

    table1 = ""
    table2 = """<tr>
            <td>0</td>
            <td>0</td>
            <td>0</td>

          </tr>"""

    #  *** PUT ALL PRESSURE AS AN INDEX IN A LIST ***
    active_pressures = []
    passive_pressures = []
    for soil_or_water in active_pressure:
        for pressure in soil_or_water:
            for j in pressure:
                active_pressures.append(j)
    active_pressures = edit_equation(*active_pressures)

    soil_active = active_pressures[1:-2]
    water_active = active_pressures[-1]
    for soil_or_water in passive_pressure:
        for pressure in soil_or_water:
            for j in pressure:
                passive_pressures.append(j)

    passive_pressures = edit_equation(*passive_pressures)

    soil_passive = passive_pressures[1:-2]
    water_passive = passive_pressures[-1]

    # SUM EVERY HEIGHT WITH LAST INDEX
    h_active_edited = []
    for i in range(len(h_active)):
        h_active_edited.append(sum(h_active[:i + 1]))
    h_passive_edited = []
    for i in range(len(h_passive)):
        h_passive_edited.append(sum(h_passive[:i + 1]))

    i, j = 0, -1
    for pressure_value in soil_active:
        if i % 2 == 0:
            power = "-"  # negative power
            j += 1
        else:
            power = "+"  # positive power
        if i == len(soil_active) - 1:
            power = ""  # for last item we have no power.
            water_pressure = water_active
        else:
            water_pressure = "-"

        table1 += f"""<tr>
              <td>{h_active_edited[j]} <sup>{power}</sup></td>
              <td>{pressure_value} {pressure_unit}</td>
              <td> {water_pressure} </td>

            </tr>"""
        i += 1

    i, j = 0, -1
    for pressure_value in soil_passive:
        if i % 2 == 0:
            power = "-"  # negative power
            j += 1
        else:
            power = "+"  # positive power
        if i == len(soil_passive) - 1:
            power = ""  # for last item we have no power.
            water_pressure = water_passive
        else:
            water_pressure = "-"

        table2 += f"""<tr>
                  <td>{h_passive_edited[j]} <sup>{power}</sup></td>
                  <td>{pressure_value} {pressure_unit}</td>
                  <td> {water_pressure} </td>

                </tr>"""
        i += 1

    with open(TEMPLATE_DIR / "active_pressure_table.html", "w") as f:
        f.write(table1)
    with open(TEMPLATE_DIR / "passive_pressure_table.html", "w") as f:
        f.write(table2)


def force_arm(active_force, active_arm, passive_force, passive_arm, unit_system):
    if unit_system == "us":
        force_unit = "lb"
        arm_unit = "ft"
    else:
        force_unit = "N"
        arm_unit = "m"
    active_table = ""
    for i in range(len(active_force)):
        active_table += f"""
        <tr>
              <td>DR<sub>{i + 1}</sub></td>
              <td>{active_force[i]} {force_unit}</td>
              <td>{active_arm[i]} {arm_unit} </td>

            </tr>
        """
    passive_table = ""
    for i in range(len(passive_force)):
        passive_table += f"""
        <tr>
              <td>RS<sub>{i + 1}</sub></td>
              <td>{passive_force[i]} {force_unit}</td>
              <td>{passive_arm[i]} {arm_unit} </td>

            </tr>
        """
    with open(TEMPLATE_DIR / "force_active_table.html", "w") as f:
        f.write(active_table)
    with open(TEMPLATE_DIR / "force_passive_table.html", "w") as f:
        f.write(passive_table)
