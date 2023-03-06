# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 20:45:05 2023

@author: katya
"""

#https://medium.com/analytics-vidhya/python-dash-data-visualization-dashboard-template-6a5bff3c2b76

import os
import base64
import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import plotly.express as px


# This loads the "cyborg" and "minty" themed figure template from
# dash-bootstrap-templates library, adds it to plotly.io and
# makes "cyborg" (The first template in the list) the default figure template.
load_figure_template(["minty", "sandstone"])

# load the dataset
DATA_FOLDER = 'assets/2023-02-05'
IMAGE_PATH = 'assets/mybooks.jpg'
file_path = os.path.join(DATA_FOLDER, 'recipe_data.csv')
recipes_df = pd.read_csv(file_path)

def process_input_data(data_df):
    '''
    Processes input data file: converts date field to time stamps, filters
    only values after Jan 2018, adds a field for month and year and
    splits title column into title and subtitle
    Return -> dataframe
    '''
    data_df = data_df[(data_df['date'] >= '2018-01-01') & (data_df['date'] < '2023-02-01')]
    data_df['month_year'] = pd.to_datetime(data_df['date']).dt.to_period('M')

    # new assets frame with split value columns
    title_col = data_df["title"].str.split(":", n=1, expand=True)
    # making separate first name column from new assets frame
    data_df["title"] = title_col[0]
    # making separate last name column from new assets frame
    data_df["subtitle"] = title_col[1]
    return data_df

def groupby_date(data):
    '''Groups data by date.
    Returns dataframe
    '''
    # note there are multiple recipe_id's per line - this is for two reasons:
    # 1. non-unique recipes are possible outwith a single month
    # 2. where recipe has two authors, there are two entries for recipe_id,
    # even within the same month
    data_by_date = data.groupby('date')['recipe_id'].nunique().reset_index()
    data_by_date = data_by_date.rename(columns={"recipe_id": "recipe_count"})
    return data_by_date

def groupby_date_and_author(data):
    '''Groups data by date and author.
    Returns dataframe
    '''
    data_by_date_and_author = data.groupby(['date', 'author_name'])['recipe_id'].\
        nunique().reset_index()
    data_by_date_and_author = data_by_date_and_author.rename(columns={'recipe_id': 'recipe_count'})
    return data_by_date_and_author


def groupby_cookbook(data):
    '''Groups data by cookbooks
    Returns dataframe
    '''
    data_by_cookbook = data.groupby('title')['recipe_id'].nunique().reset_index()
    data_by_cookbook = data_by_cookbook.rename(columns={"recipe_id": "recipe_count"})
    data_by_cookbook = data_by_cookbook.sort_values(by='recipe_count', ascending=False).head(20)
    return data_by_cookbook

def group_by_author(data):
    '''Groups data by author. Multiple authors per recipe are possible and these are treated as
    separate entries.
    Returns dataframe.
    '''
    data_by_author = data.groupby('author_name')['recipe_id'].nunique().reset_index()
    data_by_author = data_by_author.rename(columns={"recipe_id": "recipe_count"})
    data_by_author = data_by_author.sort_values(by='recipe_count', ascending=False).head(20)
    return data_by_author

def get_recipe_count(data):
    '''Gets counts for each recipe.
    Returns dataframe
    '''
    # because a recipe could appear in multiple rows when with multiple authors,
    # to get the right value counts, I need only the name and when it was cooked.
    data_count = data[['recipe_name', 'month_year']].drop_duplicates()
    data_count = data_count['recipe_name'].value_counts().reset_index()
    data_count = data_count. \
        rename(columns={'recipe_name': 'count', 'index': 'recipe_name'}).head(10)
    return data_count

# create data structures
recipes = process_input_data(recipes_df)
recipe_by_date = groupby_date(recipes)
recipe_by_date_and_author = groupby_date_and_author(recipes)
recipe_by_cookbook = groupby_cookbook(recipes)
recipe_by_author = group_by_author(recipes)
recipe_counts = get_recipe_count(recipes)


author_name_dropdown = dcc.Dropdown(options=recipe_by_date_and_author['author_name'].unique(),
                                    value='Jamie Oliver'
                                    )

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '15%',
    'padding': '20px 10px',
   # 'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '15%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'justify',
    'font-size': '12px'
   # 'color': '#191970',

}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
   # 'color': '#0074D9',
}

DROPDOWN_STYLE = dict( width='50%', display='inline-block')



def date_graph():
    '''Creates graph of progress over time.
    Returns plotly graph
    '''
    date_fig = px.line(recipe_by_date,
                       x="date",
                       y="recipe_count",
                       markers=True,
                       )
    date_fig.update_layout()
    date_fig.add_annotation(x="2018-09-01", y=40,
                       text="[Click on a dot to see breakdown by author]",
                       showarrow=True,
                       arrowhead=2,
                            )
    return date_fig

author_date_fig = px.bar(recipe_by_date_and_author, x="date", y="recipe_count")

sidebar = html.Div(
    [
        html.H6("Contents", className="display-6"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Progress Over Time", href="/over-time", active="exact"),
                dbc.NavLink("My Top", href="/my-top", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

background_text = dcc.Markdown('''
                            At the time of this writing, I own more than 90 cookbooks totalling 
                            more than 15.5K recipes. For the past few years, I’ve been 
                            taking note of each recipe I cook from my cookbooks and some online magazines, 
                            and I log these assets to [EatYourBooks (EYB)](https://www.eatyourbooks.com).
                            
                            EYB is website for all avid cookbook collectors. The EYB community 
                            have indexed about 12.3K cookbooks (or 2.3 million recipes) for 
                            recipe names and ingredients. As a member, I add my cookbooks to my 
                            virtual bookshelf.
                            
                            This means I have all recipe names, book titles and also all ingredients 
                            from my cookbooks that have been indexed (which is really most Anglophone books) 
                            in a digital format. I use that to bookmark every recipe 
                            I cook with the month and year when I cooked it. The assets I 
                            enter (my cookbooks and bookmarks) is available for download as .csv files 
                            directly from the website. Hurray! Having that database calls for some 
                            insights through cool visualisations. 
                        ''', style=TEXT_STYLE )
card_background = dbc.Card(
    [
        dbc.CardHeader("Background", style=CARD_TEXT_STYLE),
        dbc.CardBody([background_text]),
    ]#, style={ 'width' : '75%', 'height' : '50%'},

)
card_kpi_total_cookbooks = dbc.Card(
    [
        dbc.CardHeader("Total Cookbooks",
                       style=CARD_TEXT_STYLE
                       ),
        dbc.CardBody(
            [
                # html.H4("Total Cookbooks", className='card-title', style=CARD_TEXT_STYLE),
                html.P(f"{recipes['title'].nunique()}",
                       className="card-text",
                       style=CARD_TEXT_STYLE
                       )
            ]
        )
    ]
)

card_kpi_timeframe = dbc.Card(
    [ dbc.CardHeader("Time Period",
                     style=CARD_TEXT_STYLE
                     ),
      dbc.CardBody(
          [
              #html.H4("Time Period", className="card-title", style=CARD_TEXT_STYLE),
              html.P(f"{recipes['month_year'].min()} - {recipes['month_year'].max()}",
                     className="card-text",
                     style=CARD_TEXT_STYLE
                     )
                 ]
             )
      ]
)

card_kpi_total_recipes_cooked = dbc.Card(
    [
        dbc.CardHeader("Total Recipes Cooked",
                       style=CARD_TEXT_STYLE
                       ),
        dbc.CardBody(
            [
                #html.H4("Total Recipes Cooked", className="card-title", style=CARD_TEXT_STYLE),
                html.P(f"{recipe_by_date['recipe_count'].sum()}",
                       className="card-text",
                       style=CARD_TEXT_STYLE
                       )
            ]
        )
    ]
)

card_kpi_avg_per_month = dbc.Card(
    [ dbc.CardHeader("Average per Month",
                     style=CARD_TEXT_STYLE
                     ),
      dbc.CardBody(
          [
              # html.H4("Average Recipes per Month",
              # className="card-title", style=CARD_TEXT_STYLE),
              html.P(f"{round(recipe_by_date['recipe_count'].sum() / recipe_by_date.shape[0], 1)}",
                     className="card-text",
                     style=CARD_TEXT_STYLE
                     )
              ]
      )
      ]
)

cards_kpis = html.Div(
    [dbc.CardHeader('KPIs', style=CARD_TEXT_STYLE),
     html.Br(),
     dbc.CardBody(html.Div([
         dbc.Row([dbc.Col(card_kpi_total_cookbooks),
                  dbc.Col(card_kpi_timeframe),
                  dbc.Col(card_kpi_total_recipes_cooked),
                  dbc.Col(card_kpi_avg_per_month)
                  ]
                 )
     ]))])


def b64_image(image_filename):
    '''Convert a JPG image to a base 64 string
    for HTML displaying
    Returns base64 image
    '''
    with open(image_filename, 'rb') as input_file:
        image = input_file.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

card_mybooks_picture = dbc.Card( [dbc.CardHeader("My Bookshelf", style=CARD_TEXT_STYLE),
                                  dbc.CardImg(src=b64_image(IMAGE_PATH))]
                                 ,
                                 style={ 'height': '65%', 'width' : '65%'},
                                )
content_home = html.Div([dbc.Row([ dbc.Col(card_background), #width = 8, md=3
                                   dbc.Col(card_mybooks_picture)
                                ],
                                 align="end"
                                 ),
                         html.Br(),
                         dbc.Row([cards_kpis])
                         ])

content_over_time = dbc.Card([
    dbc.Button('🡠git s', id='back-button', outline=True, size="sm",
               className='mt-2 ml-2 col-1', style={'display': 'none'}
               ),
    dbc.Row(
        dcc.Graph(id='date-graph', figure=date_graph() ),
        justify='center'
    )
    ], className='mt-3'
)


# top_dropdown = dcc.Dropdown(id='top-dropdown',
#                             options=[{'label': 'Top 20 Cookbooks', 'value': 'title'},
#                                      {'label': 'Top 20 Authors', 'value': 'author_name'},
#                                      {'label': 'Top 10 Recipes', 'value': 'recipe_name'}
#                                      ],
#                             value='title',
#                             style=DROPDOWN_STYLE,
#                             )

def get_top_graph(data, x_axis, y_axis, xaxis_title, yaxis_title):
    top_graph = px.bar(data, x=x_axis, y=y_axis)
    top_graph.update_layout(autosize=True, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    top_graph.update_yaxes(automargin=True)
    return top_graph

top_cookbooks_graph = get_top_graph(recipe_by_date,
                                    recipe_by_cookbook['recipe_count'].to_list(),
                                    recipe_by_cookbook['title'].to_list(),
                                    xaxis_title="Count",
                                    yaxis_title='Cookbook Title'
                                    )

top_authors_graph = get_top_graph(recipe_by_author,
                                  recipe_by_author['recipe_count'].to_list(),
                                  recipe_by_author['author_name'].to_list(),
                                  xaxis_title="Count",
                                  yaxis_title='Author'
                                  )

top_recipes_graph = get_top_graph(recipe_counts,
                                  recipe_counts['count'].to_list(),
                                  recipe_counts['recipe_name'].to_list(),
                                  xaxis_title="Count",
                                  yaxis_title='Recipe'
                                  )
def get_top_content(figure, graph_id):
    top_content = dbc.Card(
        dbc.CardBody(
            [dbc.Row(dcc.Graph(id=graph_id, figure=figure), justify='center')]
            ), className="mt-3"
    )
    return top_content

top_cookbooks_content = get_top_content(top_cookbooks_graph, 'top_cookbooks_graph')
top_authors_content = get_top_content(top_authors_graph, 'top_authors_graph')
top_recipes_content = get_top_content(top_recipes_graph, 'top_recipes_graph')

content_my_top = dbc.Tabs(
    [
        dbc.Tab(top_cookbooks_content, label="My Top Cookbooks"),
        dbc.Tab(top_authors_content, label='My Top Authors'),
        dbc.Tab(top_recipes_content, label='Top Recipes')
    ]
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
app.title = "Insights from EYB"
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
application = app.server
#
#
# @app.callback(Output('top-graph', 'figure'), [Input('top-dropdown', 'value')])
# # graph plot and styling
# def update_graph(value):
#     x_values = None
#     y_values = None
#     title = None
#     data = None
#     font = None
#     if value == 'title':
#         x_values = recipes_by_cookbook['title'].to_list()
#         y_values = recipes_by_cookbook['recipe_count'].to_list()
#         data = recipes_by_cookbook
#         yaxis_title = 'Cookbook Title'
#         #font=dict( size=18, color="RebeccaPurple")
#     if value == 'author_name':
#         x_values = recipes_by_author['author_name'].to_list()
#         y_values = recipes_by_author['recipe_count'].to_list()
#         data = recipes_by_author
#         yaxis_title = 'Author'
#     if value == 'recipe_name':
#         x_values = recipes_count['recipe_name'].to_list()
#         y_values = recipes_count['count'].to_list()
#         data = recipes_count
#         yaxis_title = 'Recipe'
#
#     updated_fig = px.bar(data, orientation="h", x=y_values, y=x_values, title=title,  )
#     updated_fig.update_layout(autosize=True,
#                               xaxis_title="Count",
#                               yaxis_title=yaxis_title,
#                               font=font
#                               )
#     updated_fig.update_yaxes(automargin=True)
#     return updated_fig

#Callback
@app.callback(
    Output('date-graph', 'figure'),
    Output('back-button', 'style'),   # to hide/unhide the back button
    Input('date-graph', 'clickData'), # for getting the vendor name from graph
    Input('back-button', 'n_clicks')
)

def drilldown(click_data,n_clicks):
    '''Defines to display when drilling down
    Returns plotly figure
    '''
    # using callback context to check which input was fired
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == 'date-graph':
        # get month from clickData
        if click_data is not None:
            date = click_data['points'][0]['x']
            if date in recipe_by_date_and_author['date'].unique():
                # creating df for clicked date
                month_df = recipe_by_date_and_author[recipe_by_date_and_author['date'] == date]
                fig = px.bar(month_df, x='author_name', y='recipe_count' )
                date = date[:-3]
                fig.update_layout(title='Drill-down to {} by Author'.format(date),
                                  showlegend=False,
                                  template="sandstone"
                                  )
                return fig, {'display': 'block'}     #returning the fig and unhiding the back button
            return date_graph(), {'display': 'none'}     #hiding the back button
    return date_graph(), {'display': 'none'}

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

def render_page_content(pathname):
    if pathname == "/":
        return html.Div(
            children=
            [ html.H2('Data Vis in the Kitchen', style=CARD_TEXT_STYLE),
              html.H4('Where Food & Data Meet', style=CARD_TEXT_STYLE),
              html.Br(),
              html.P(content_home),
              ]
        )
    elif pathname == "/over-time":
        return html.Div(
            children=
            [ html.H4("Progress Over Time By Month", style=CARD_TEXT_STYLE),
              html.Br(),
              html.P(content_over_time)
            ]
        )
    else:
        if pathname == "/my-top":
            return html.Div(
                children=
                [ html.H4("My Top Cookbooks/ Authors / Recipes", style=CARD_TEXT_STYLE),
                html.Br(),
                html.P(content_my_top)
                ]
            )
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


app.config['suppress_callback_exceptions']=True

# if __name__=='__main__':
#     application.run(host='0.0.0.0', port='8080')
#
if __name__ == '__main__':
    app.run_server(debug=True)
