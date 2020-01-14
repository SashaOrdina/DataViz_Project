import numpy as np
import pandas as pd
from datetime import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import numpy as np
import plotly.graph_objs as go
import plotly.offline as pyo
import calendar
import random


########################################## DATA PREPROCESSING ##########################################
df_all_trees = pd.read_csv("https://raw.githubusercontent.com/pedromcsantos/DataViz_Project/master/df_all_trees.csv")
categories_sum = pd.read_csv("https://raw.githubusercontent.com/pedromcsantos/DataViz_Project/master/categories_sum.csv")
success_rate_cat_perc = pd.read_csv("https://raw.githubusercontent.com/pedromcsantos/DataViz_Project/master/success_rate_cat_perc.csv")
success_rate_month_perc = pd.read_csv("https://raw.githubusercontent.com/pedromcsantos/DataViz_Project/master/success_rate_month_perc.csv")
con = pd.read_csv("https://raw.githubusercontent.com/pedromcsantos/DataViz_Project/master/conlolol.csv")

########################################## INTERACTIVE COMPONENTS ##########################################
cat_options = [dict(label=category, value = category) for category in categories_sum.main_category.unique()]

########################################## APP ##########################################
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Kickstarter Projects - Data Visualization')], className='Title'),
            html.H3("Explore startups", style={"margin-top": "0px"}),
    html.Div([# start row 1 flex display
        html.Div([
            html.Div([dcc.Graph(id = "sunburst")], className ='pretty_container'),
            html.Div([dcc.Graph(id="bubble")], className ='pretty_container'),
            html.Div([#Slider
                dcc.Slider(id="year_slider",
                           min=2009,
                           max=2017,
                           step=None,
                           marks={str(year): str(year) for year in categories_sum['year'].sort_values().unique()},
                           value=2017)
                ]),
        ],className='pretty eight columns'),
        html.Div([ #start right side pretty 8 cols
            html.Div([#container for 4 flashcards
                html.Div([html.Label(id='fc_1')], className='mini_container'),
                html.Div([html.Label(id='fc_2')], className='mini_container'),
                html.Div([html.Label(id='fc_3')], className='mini_container'),
                html.Div([html.Label(id='fc_4')], className='mini_container'),
            ], className ='row container-display'),
            html.Div([#Drop down
            dcc.Dropdown(
            id='cat_drop',
            options=cat_options,
            value='Games'
            )
            ]),
            html.Div([#linechart
            dcc.Graph(id="linechart")
            ], className ='pretty_container'),
            html.Div([#barchart
            dcc.Graph(id = "barchart")
            ], className = "pretty_container"),
        ],className = 'pretty four columns'), #end of pretty 8 cols
    ], className = 'row flex-display'),#end of row 1 flex display
    html.Div([# Parallel last row
        dcc.Graph(id="parallel")
        ], className = "row flex-display"),
],style={"display": "flex", "flex-direction": "column"},
)


########################################## CALL BACKS ##########################################

@app.callback(
    [
        Output("sunburst","figure"),
        Output("bubble","figure"),
        Output("barchart","figure"),
        Output("linechart","figure"),
        Output("parallel","figure")
    ],
    [
        Input("year_slider", "value"),
        Input("cat_drop", "value")
    ]
)
def plots(year,cat):
    ########### Sunburst ###########
    data_sunburst = dict(type = "sunburst",
        labels=df_all_trees['id'],
        parents=df_all_trees['parent'],
        values=df_all_trees['value'],
        branchvalues='total',
        opacity=0.8,
        marker=dict(
            colors=df_all_trees['color'],
            colorscale='ice',
            showscale=False,  # 'GnBu'
            cmin=con["usd_pledged_real"].sum()/con["backers"].sum()),
        hovertemplate='<b>%{label} </b> <br> Backers: %{value}<br> Per Backer: %{color:.2f}',
        maxdepth=2
    )

    #layout_sunburst = margin=dict(t=5, b=5, r=5, l=5)

    ########### Bubble ###########
    categories_sum_0 = categories_sum.loc[categories_sum["year"] == year]
    data_bubble=[go.Scatter(
        x=categories_sum_0["x"],
        y=categories_sum_0["y"],
        mode='markers',
        text=round(categories_sum_0["usd_pledged_real"] / 1000, 0), textposition="top center",
        marker=dict(colorscale="viridis", showscale=True,
            colorbar=dict(title="Main Category", tickvals=list(range(1, 16)),
            ticklen=5,
            ticktext=categories_sum_0.sort_values("success_rank")["main_category"].unique()),
            color=categories_sum_0.success_rank,
            size=(categories_sum_0["pledged_minmax"])
            ),
        hovertext=categories_sum_0["category"] + "<br>" + round(categories_sum_0["usd_pledged_real"] / 1000000, 1).map(str) + "M $",
        hoverinfo="text")]
    layout_bubble=go.Layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    ########### barchart ###########
    data_bar = [
        go.Bar(
            x=success_rate_cat_perc.main_category,
            y=success_rate_cat_perc.failed,
            base=0,
            marker=dict(
                color='#cc0000'
            ),
            name='Failure',
            yaxis='y2'
        ),
        go.Bar(
            x=success_rate_cat_perc.main_category,
            y=success_rate_cat_perc.successful,
            base=0,
            marker=dict(
                color='#00802b'
            ),
            name='Successful'
        )
    ]

    layout_bar=go.Layout(
        yaxis2=dict(rangemode='nonnegative', overlaying='y', range=[100, -100],
                    tickvals=np.arange(0, 101, 20), tickmode='array'),
        title='Success vs Failure', xaxis=dict(title='Categories'),
        barmode='stack',
        yaxis=dict(range=[-100, 100], tickvals=np.arange(0, 101, 20), tickmode='array',
                   title='Percentage of Failure/Success')
    )

    ########### linechart ###########
    success_rate_month_perc_0 = success_rate_month_perc.loc[success_rate_month_perc.main_category == cat]

    x = success_rate_month_perc_0['month name']
    y = success_rate_month_perc_0['successful']

    data_line=go.Scatter(x=x, y=y, mode='lines+markers')
    best_month = success_rate_month_perc_0.loc[success_rate_month_perc_0["successful"] == success_rate_month_perc_0["successful"].max()]["month name"]
    best_month = best_month.to_string(index = False)

    layout_line=go.Layout(title= best_month+' is the best month to start a project in '+ cat, xaxis_title='Month', yaxis_title='Success Rate')

    ########### parallel ###########
    data_parallel=go.Parcoords(
        line=dict(color=con["success_rank"], colorscale="Electric"),
        dimensions=list([
            dict(range=[1, 15],
                 label='Amount of Projects Ranking', values=con['projects_rank'],
                 tickvals=list(range(1, 16)),
                 ticktext=con["projects_rank"].sort_values()["main_category"]),
            dict(range=[1, 15],
                 label='Backers Ranking', values=con['backers_rank']),
            dict(range=[1, 15],
                 label='Amount per Backer Ranking', values=con['amnt_per_backer_rank']),
            dict(range=[1, 15],
                 label='Pledged Dollars Ranking', values=con['usd_pledged_rank']),
            dict(range=[1, 15],
                 label='Success Rate Ranking', values=con['success_rank'],
                 tickvals=list(range(1, 16)),
                 ticktext=con["success_rank"].sort_values()["main_category"])]))

    return go.Figure(data=data_sunburst), \
           go.Figure(data=data_bubble, layout=layout_bubble),\
           go.Figure(data=data_bar, layout=layout_bar),\
           go.Figure(data=data_line, layout=layout_line),\
           go.Figure(data=data_parallel)

if __name__ == '__main__':
    app.run_server(debug=True)
