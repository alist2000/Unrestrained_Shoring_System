from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# from IPython.core.display import display, HTML
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.express as px
from plotly.graph_objs import Layout

from sympy import symbols
from sympy.solvers import solve

import numpy as np

# setup
# display(HTML("<style>.container { width:50% !important; } .widget-select > select {background-color: gainsboro;}</style>"))
# init_notebook_mode(connected=True)

# %qtconsole --style vim

# dates
# StartA = '2009-01-01'
# StartB = '2009-03-05'
# StartC = '2009-02-20'
#
# FinishA='2009-02-28'
# FinishB='2009-04-15'
# FinishC='2009-05-30'
#
# LabelDateA='2009-01-25'
# LabelDateB='2009-03-20'
# LabelDateC='2009-04-01'
#
# # sample data
# df = [dict(Task="Task A", Start=StartA, Finish=FinishA),
#       dict(Task="Task B", Start=StartB, Finish=FinishB),
#       dict(Task="Task C", Start=StartC, Finish=FinishC)]
#
# # figure
# fig = ff.create_gantt(df)
#
# # add annotations
# annots =  [dict(x=LabelDateA,y=0,text="Task label A", showarrow=False, font=dict(color='white')),
#            dict(x=LabelDateB,y=1,text="Task label B", showarrow=False, font=dict(color='White')),
#            dict(x=LabelDateC,y=2,text="Task label C", showarrow=False, font=dict(color='White'))]
#
# # plot figure
# fig['layout']['annotations'] = annots
#
#
# # Step 1 - adjust margins to make room for the text
# fig.update_layout(margin=dict(t=150))
#
# # Step 2 - add line
# fig.add_shape(type='line',
#                 x0=LabelDateB,
#                 y0=0,
#                 x1=LabelDateB,
#                 y1=1,
#                 line=dict(color='black', dash='dot'),
#                 xref='x',
#                 yref='paper'
# )
#
# # Step 3 - add text with xref set to x
# # and yref set to 'paper' which will let you set
# # text outside the plot itself by specifying y > 1
# fig.add_annotation(dict(font=dict(color="black",size=10),
#                             #x=x_loc,
#                             x=LabelDateB,
#                             y=1.06,
#                             showarrow=False,
#                             text='<b>Today</b>',
#                             textangle=0,
#                             xref="x",
#                             yref="paper"
#                            ))
#
#
# fig.update_layout(
#     title_text="Academic year 2019/2020"
# )
depth_final = [i for i in range(100)]
x = symbols("x")
y = -x ** 2
sigma_final = []
for i in depth_final:
    sigma_final.append(float(y.subs(x, i)))

sigma_final[-1] = 0

# sigma_final = [j for j in range(255, 355)]
x_title = "x_title"
x_unit = "x_unit"
y_title = "y_title"
y_unit = "y_unit"
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
plot.add_traces(go.Scatter(x=sigma_final, y=depth_final,
                           mode="none", name="Max", hoverinfo="skip", fill="tozeroy",connectgaps= True, showlegend=False, fillcolor="rgba(242, 87, 87, 0.7)"
                           ))
# plot2 = px.area(sigma_final, x="xmodel", y="ymodel", color="nation", pattern_shape="nation", pattern_shape_map=["+"])
# plot2.show()
plot.show()
