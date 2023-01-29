import copy
import sys
import json

from sympy import symbols
from sympy.solvers import solve
import numpy as np
import scipy.integrate as spi

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Layout


def calculator_depth(depth, delta_h, delta_h_decimal, soil_pressure, water_pressure):
    j = 0
    sigma_soil = []
    sigma_water = []
    for depth_list in depth:
        depth[j] = [
            round(i / pow(10, delta_h_decimal), delta_h_decimal) if i / pow(10, delta_h_decimal) <=
                                                                    depth[j][
                                                                        1] else depth_list[
                -1]
            for i in
            range(0, int((depth_list[1] + delta_h - depth_list[0]) * pow(10, delta_h_decimal)),
                  int(delta_h * pow(10, delta_h_decimal)))]
        # if j != 0:
        #     del depth[j][0]
        #     del soil_pressure[j][0]
        #     del water_pressure[j][0]

        # print(depth_list[-1])
        # print(depth[j][-1])
        # depth[j][-1] = depth_list[-1]

        soil = calculate_pressure(depth[j], soil_pressure[j])
        soil_copy = np.array(copy.deepcopy(soil))
        sigma_soil.append(soil_copy)
        soil.clear()
        water = calculate_pressure(depth[j], water_pressure[j])
        water_copy = np.array(copy.deepcopy(water))
        sigma_water.append(water_copy)
        water.clear()
        j += 1
    # edit depth for plot.
    for i in range(1, len(depth)):
        for j in range(len(depth[i])):
            depth[i][j] += depth[i - 1][-1]
    return depth, sigma_soil, sigma_water


def calculate_pressure(depth, pressure):
    z = symbols("z")
    try:
        equation = (pressure[1] - pressure[0]) / (depth[-1] - depth[0]) * z + pressure[0]
    except:
        equation = 0
    pressure_list = []
    for Z in depth:
        try:
            sigma = equation.subs(z, Z)
        except:
            sigma = 0
        pressure_list.append(sigma)
    return pressure_list


def plotter_load(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top",
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    plot['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    plot.update_layout(layout)

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(242, 87, 87, 0.7)"
                               ))

    j = int(len(depth_final) / 5)
    arrow0 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[0],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[0],
        ay=depth_final[0],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )

    arrow1 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[j],
        ay=depth_final[j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow2 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[2 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[2 * j],
        ay=depth_final[2 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow3 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[3 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[3 * j],
        ay=depth_final[3 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow4 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[4 * j],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[4 * j],
        ay=depth_final[4 * j],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    arrow5 = go.layout.Annotation(dict(
        x=0.01,
        y=depth_final[5 * j - 1],
        xref="x", yref="y",
        text="",
        showarrow=True,
        axref="x", ayref='y',
        ax=sigma_final[5 * j - 1],
        ay=depth_final[5 * j - 1],
        arrowhead=3,
        arrowwidth=1.5,
        arrowcolor='#595959', )
    )
    list_of_all_arrows = [arrow0, arrow1, arrow2, arrow3, arrow4, arrow5]
    plot.update_layout(annotations=list_of_all_arrows)

    plot.update_layout(title_text='Load Diagram', title_y=0.96)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_shear(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top",
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    plot['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    plot.update_layout(layout)

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(152, 193, 217, 0.7)"
                               ))

    plot.update_layout(title_text='Shear Diagram', title_y=0.96)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_moment(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top",
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    plot['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    plot.update_layout(layout)

    zero_list = []
    for i in range(len(sigma_final)):
        zero_list.append(0)
    plot.add_traces(go.Scatter(x=zero_list, y=depth_final,
                               mode="lines", hoverinfo="skip", fill=None, connectgaps=True, showlegend=False,
                               line_color="#969696"))
    plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                               mode="lines", hoverinfo="skip", fill="tonexty", connectgaps=True, showlegend=False,
                               fillcolor="rgba(93, 211, 158, 0.7)"
                               ))

    plot.update_layout(title_text='Moment Diagram', title_y=0.96)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


def plotter_deflection(depth_final, sigma_final, x_title, y_title, x_unit, y_unit):
    plot = px.line(y=depth_final, x=sigma_final, color_discrete_sequence=["#595959"]).update_layout(
        xaxis_title=f"{x_title} ({x_unit})",
        yaxis_title=f"{y_title} ({y_unit})",
        xaxis={"side": "top",
               "zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#000000",
               "zerolinewidth": 7},
        yaxis={"zeroline": True,
               "mirror": "ticks",
               "zerolinecolor": "#969696",
               "zerolinewidth": 4}
    )
    plot['layout']['yaxis']['autorange'] = "reversed"
    layout = Layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )
    plot.update_layout(layout)

    # plot.write_html("output.html",
    #                 full_html=False,
    #                 include_plotlyjs='cdn')
    # plot.show()
    return plot


class diagram:
    def __init__(self, unit_system, surcharge_pressure, surcharge_depth, depth_active, depth_passive, active_pressure,
                 passive_pressure,
                 water_pressure_active,
                 water_pressure_passive):
        self.unit_system = unit_system

        for i in range(len(depth_active) - len(depth_passive)):
            depth_passive.insert(i, [0, 0])
            passive_pressure.insert(i, [0, 0])
        for i in range(len(depth_active) - len(water_pressure_active)):
            water_pressure_active.insert(i, [0, 0])
        for i in range(len(depth_active) - len(water_pressure_passive)):
            water_pressure_passive.insert(i, [0, 0])
        # for i in range(len(depth_active), 0, -1):
        #     try:
        #         a = depth_passive[i]
        #     except:
        #         depth_passive.insert(-i, [0, 0])
        #     try:
        #         a = passive_pressure[i]
        #     except:
        #         passive_pressure.insert(-i, [0, 0])
        #     try:
        #         a = water_pressure_active[i]
        #     except:
        #         water_pressure_active.insert(-i, [0, 0])
        #     try:
        #         a = water_pressure_passive[i]
        #     except:
        #         water_pressure_pass
        # ive.insert(-i, [0, 0])

        # surcharge must be checked also.
        self.depth_active = depth_active
        self.depth_passive = depth_passive
        self.active_pressure = active_pressure
        self.passive_pressure = passive_pressure
        self.water_pressure_active = water_pressure_active
        self.water_pressure_passive = water_pressure_passive
        self.surcharge_pressure = surcharge_pressure
        self.surcharge_depth = surcharge_depth

    def base_calculate(self, delta_h=0.01):
        depth_active = self.depth_active
        depth_passive = self.depth_passive
        active_pressure = self.active_pressure
        passive_pressure = self.passive_pressure
        water_pressure_active = self.water_pressure_active
        water_pressure_passive = self.water_pressure_passive
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        depth_active, sigma_active, sigma_water_a = calculator_depth(depth_active, delta_h, delta_h_decimal,
                                                                     active_pressure,
                                                                     water_pressure_active)
        depth_passive, sigma_passive, sigma_water_p = calculator_depth(depth_passive, delta_h, delta_h_decimal,
                                                                       passive_pressure,
                                                                       water_pressure_passive)
        # reshape passive parameters to active shape. must have same shapes.( for zero values. )
        for z in range(len(depth_passive)):
            if depth_passive[z] == [0, 0]:
                copy_list = copy.deepcopy(depth_active[z])
                depth_passive[z] = copy_list
                for i in range(len(copy_list)):
                    depth_passive[z][i] = 0
        for z in range(len(sigma_passive)):
            if list(sigma_passive[z]) == [0, 0]:
                copy_list = copy.deepcopy(sigma_active[z])
                sigma_passive[z] = copy_list
                for i in range(len(sigma_active[z])):
                    sigma_passive[z][i] = 0
        for z in range(len(sigma_water_p)):
            if list(sigma_water_p[z]) == [0, 0]:
                copy_list = copy.deepcopy(sigma_water_a[z])
                sigma_water_p[z] = copy_list
                for i in range(len(sigma_water_a[z])):
                    sigma_water_p[z][i] = 0
        sigma_active = np.array(sigma_active, dtype="object")
        sigma_passive = np.array(sigma_passive, dtype="object")
        sigma_water_a = np.array(sigma_water_a, dtype="object")
        sigma_water_p = np.array(sigma_water_p, dtype="object")
        sigma_final = sigma_active + sigma_water_a - sigma_passive - sigma_water_p

        surcharge_pressure = self.surcharge_pressure
        surcharge_depth = self.surcharge_depth

        # edit depth and sigma to be used in plotter functions.
        edited_depth = depth_active[0]
        edited_sigma = list(sigma_final[0])
        for i in depth_active[1:]:
            edited_depth += i
        edited_depth[0] = 0.0
        edited_depth = np.array(edited_depth)

        for i in sigma_final[1:]:
            edited_sigma += list(i)
        edited_sigma[0] = 0.0
        for i in range(len(edited_sigma)):
            edited_sigma[i] = float(edited_sigma[i])

        for i in range(len(surcharge_pressure)):
            edited_sigma[i] += surcharge_pressure[i]

        unique_depth = []
        for i in range(len(edited_depth)):
            if edited_depth[i] not in unique_depth:
                unique_depth.append(edited_depth[i])
            else:
                del edited_sigma[i]

        unique_depth = np.array(unique_depth)
        edited_sigma = np.array(edited_sigma)

        return unique_depth, edited_sigma

    def load_diagram(self, depth, sigma_final):
        unit_system = self.unit_system
        if unit_system == "us":
            load_unit = "lb/m"
            length_unit = "ft"
        else:
            load_unit = "10^6 N/m"
            length_unit = "m"

        plot = plotter_load(depth, sigma_final, "q", "Z", load_unit, length_unit)
        return plot

    def shear_diagram(self, depth, sigma_final):
        unit_system = self.unit_system
        if unit_system == "us":
            load_unit = "lb"
            length_unit = "ft"
        else:
            load_unit = "10^6 N"
            length_unit = "m"
        shear_values = []
        for i in range(len(depth)):
            try:
                shear = spi.simpson(sigma_final[:i], depth[:i])
            except:
                shear = 0
            shear_values.append(shear)
        shear_values = np.array(shear_values)

        plot = plotter_shear(depth, shear_values, "V", "Z", load_unit, length_unit)

        return plot, shear_values

    def moment_diagram(self, depth, shear_values):
        unit_system = self.unit_system
        if unit_system == "us":
            load_unit = "lb-ft"
            length_unit = "ft"
        else:
            load_unit = "10^6 N-m"
            length_unit = "m"
        moment_values = []
        for i in range(len(depth)):
            try:
                moment = spi.simpson(shear_values[:i], depth[:i])
            except:
                moment = 0
            moment_values.append(moment)
        moment_values[-1] = 0
        moment_values = np.array(moment_values)

        plot = plotter_moment(depth, moment_values, "M", "Z", load_unit, length_unit)

        return plot, moment_values
