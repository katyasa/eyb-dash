# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 20:45:05 2023

@author: katya
"""

#https://medium.com/analytics-vidhya/python-dash-data-visualization-dashboard-template-6a5bff3c2b76
#https://awstip.com/docker-ize-a-python-dash-application-and-deploy-it-to-cloud-717a7c25de5b

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
DATA_FOLDER = 'assets/2023-03-11'
IMAGE_PATH_01 = 'assets/cookbooks01.JPG'
IMAGE_PATH_02 = 'assets/cookbooks02.JPG'
START_DATE = '2018-01-01'
END_DATE = '2023-03-01'

file_path = os.path.join(DATA_FOLDER, 'recipe_data.csv')
recipes_df = pd.read_csv(file_path)
recipe_location_df = pd.read_csv(os.path.join(DATA_FOLDER, 'recipe_data_location.csv')).dropna()
location_counts_df = recipe_location_df['location'].value_counts().reset_index()
location_counts_df = location_counts_df.rename(columns={'location': 'count', 'index': 'country'})

def process_input_data(data_df):
    '''
    Processes input data file: converts date field to time stamps, filters
    only values after Jan 2018, adds a field for month and year and
    splits title column into title and subtitle
    Return -> dataframe
    '''
    data_df = data_df[(data_df['date'] >= START_DATE) & (data_df['date'] < END_DATE)]
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

# author_name_dropdown = dcc.Dropdown(options=recipe_by_date_and_author['author_name'].unique(),
#                                     value='Jamie Oliver'
#                                     )

# the style arguments for the sidebar
SIDEBAR_STYLE = {'position': 'fixed', 'top': 0, 'left': 0, 'bottom': 0,
                  'width': '15%', 'padding': '20px 10px',
                  # 'background-color': '#f8f9fa'
                }
# the style arguments for the main content page.
CONTENT_STYLE = {'margin-left': '15%', 'margin-right': '5%', 'top': 0, 'padding': '20px 10px' }
TEXT_STYLE = {'textAlign': 'justify', 'font-size': '14px'}
CARD_TEXT_STYLE = {'textAlign': 'center'}

styles = {'sidebar': SIDEBAR_STYLE, 'content': CONTENT_STYLE,
          'text': TEXT_STYLE, 'card_text': CARD_TEXT_STYLE,
          }

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
    date_fig.add_hline(y=recipe_by_date['recipe_count'].sum() / recipe_by_date.shape[0],
                       line_dash="dot",
                       line_color="grey",
                       annotation_text="Average Per Month",
                       annotation_position="right"
                       )
    date_fig.add_annotation(x="2018-09-01", y=40,
                       text="[Click on any dot to see breakdown by author]",
                       showarrow=True,
                       arrowhead=2,
                            )
    return date_fig

def facetted_date_graph():
    '''Creates facetted graph of progress over time by author.
    Returns plotly graph
    '''
    authors = ['Yotam Ottolenghi', 'Nigella Lawson', 'Sabrina Ghayour',
               'Noor Murad', 'Jamie Oliver', 'Meera Sodha',
                'Georgina Hayden', 'Ixta Belfrage'
               ]
    sub_recipe_data = recipe_by_date_and_author.loc[recipe_by_date_and_author['author_name'].isin(authors)]
    fig = px.line(sub_recipe_data, x='date', y='recipe_count',
                       color="author_name",
                       facet_col="author_name",
                       facet_col_wrap=4,
                       facet_col_spacing=0.09,
                       facet_row_spacing=0.3,
                       #height=600, width=800,
                       )
    return fig

#author_date_fig = px.bar(recipe_by_date_and_author, x="date", y="recipe_count")

sidebar = html.Div(
    [html.H6("Contents", className="display-6"),
     html.Hr(),
     dbc.Nav([dbc.NavLink("Home", href="/", active="exact"),
              dbc.NavLink("Progress Over Time", href="/over-time", active="exact"),
              dbc.NavLink("My Top", href="/my-top", active="exact"),
              dbc.NavLink("Around The World", href="/around-the-world", active='exact')
              ],
             vertical=True,pills=True,
             ),
     ],
    style=styles['sidebar'],
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
                            enter (my cookbooks and bookmarks) are available for download as _.csv_ files 
                            directly from the website. Hurray! Having that database calls for some 
                            insights through cool visualisations. 
                        ''', style=styles['text'])

around_the_world_text = dcc.Markdown('''
                            EYB tags some recipes with a category, which, among other things, could be a 
                            location. The location is varied - could be a specific country (like 'Italy', 'India'), 
                            or not (like 'Jewish', 'Asia', 'Mediterranean'). I mapped these values to countries 
                            to be able to plot them on a choropleth map.\n
                             
                            Just as I was curious about the locations 
                            of my cuisine, these should be taken with a pinch of salt - recipes are eclectic, 
                            multi-cultural and multi-flavoured creations reminiscent of our own roots, inspirations, and
                            maybe trends.\n 
                            
                            What would be the location tag for _za'atar cacio e pepe_?  
                            ''', style=styles['text'])

def get_text_card(text, header_text):
    card_text = dbc.Card(
        [ dbc.CardHeader(header_text, style=styles['card_text']),
          dbc.CardBody([text]),
          ]#, style={ 'width' : '75%', 'height' : '50%'},
    )
    return card_text

def get_kpi_card(header, content):
    card = dbc.Card([dbc.CardHeader(header, style=styles['card_text']),
                     dbc.CardBody(
                         [ # html.H4("Time Period", className="card-title", style=styles['card_text']),
                           html.P(content, className="card-text", style=styles['card_text'])
                          ]
                         )
                     ]
                    )
    return card

card_kpi_timeframe = get_kpi_card('Analysed Time Period',
                                  f"{recipes['month_year'].min()} - {recipes['month_year'].max()}"
                                  )
card_kpi_total_cookbooks = get_kpi_card("Total (Indexed) Cookbooks",
                                        f"{recipes[['book_id', 'title', 'subtitle']].drop_duplicates().shape[0]}"
                                        )
card_kpi_total_recipes_cooked = get_kpi_card('Total Recipes Cooked',
                                             f"{recipe_by_date['recipe_count'].sum()}"
                                             )
card_kpi_avg_per_month = get_kpi_card("Average per Month",
                                      f"{round(recipe_by_date['recipe_count'].sum() / recipe_by_date.shape[0], 1)}"
                                      )
cards_kpis = html.Div(
    [dbc.CardHeader('KPIs', style=styles['card_text']),
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

def get_image_card(image_path, header):
    card = dbc.Card( [dbc.CardHeader(header, style=styles['card_text']),
                      dbc.CardImg(src=b64_image(image_path))
                      ],
                     #style={'height': '80%', 'width' : '65%'}
                     )
    return card


card_background = get_text_card(background_text, 'Background')
card_mybooks_picture_01 = get_image_card(IMAGE_PATH_01, 'My Bookshelf')
card_mybooks_picture_02 = get_image_card(IMAGE_PATH_02, 'My Bookshelf')

content_home = html.Div([dbc.Row([dbc.Col(card_mybooks_picture_02, sm=3),
                                  dbc.Col(card_background, sm=6), #width = 8, md=3
                                  dbc.Col(card_mybooks_picture_01, sm=3)
                                   ],
                                 align="center"
                                 ),
                         html.Br(),
                         dbc.Row([cards_kpis])
                         ])


content_over_time = dbc.Card([dbc.CardHeader('Growth Rate by Month', style=styles['card_text']),
                              dbc.CardBody([dbc.Button('Go Back', id='back-button', size="sm", color="dark",
                                                      className='col-1'# ml-2 col-1',
                                                      #style={'display': 'none'}
                                                    ),
                                           dbc.Row(dcc.Graph(id='date-graph', figure=date_graph()), justify='center')
                                           ]
                                          )
                              ]
                             )

content_over_time_by_author = dbc.Card([dbc.CardHeader('Growth Rate by Month Split By Author', style=styles['card_text']),
                                        dbc.CardBody(dbc.Row(dcc.Graph(figure=facetted_date_graph()), justify='center'))
                                        ])

# top_dropdown = dcc.Dropdown(id='top-dropdown',
#                             options=[{'label': 'Top 20 Cookbooks', 'value': 'title'},
#                                      {'label': 'Top 20 Authors', 'value': 'author_name'},
#                                      {'label': 'Top 10 Recipes', 'value': 'recipe_name'}
#                                      ],
#                             value='title',
#                             style=styles['dropdown'],
#                             )

def get_top_graph(data, x_axis, y_axis, xaxis_title, yaxis_title):
    top_graph = px.bar(data, x=x_axis, y=y_axis)
    top_graph.update_layout(autosize=True, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    top_graph.update_yaxes(automargin=True)
    return top_graph

top_cookbooks_graph = get_top_graph(recipe_by_date,
                                    recipe_by_cookbook['recipe_count'].to_list(),
                                    recipe_by_cookbook['title'].to_list(),
                                    xaxis_title="Number of Recipes Cooked from Title",
                                    yaxis_title='Cookbook Title'
                                    )

top_authors_graph = get_top_graph(recipe_by_author,
                                  recipe_by_author['recipe_count'].to_list(),
                                  recipe_by_author['author_name'].to_list(),
                                  xaxis_title="Number of Recipes Cooked from Author",
                                  yaxis_title='Author'
                                  )

top_recipes_graph = get_top_graph(recipe_counts,
                                  recipe_counts['count'].to_list(),
                                  recipe_counts['recipe_name'].to_list(),
                                  xaxis_title="Number of Times Recipe Cooked",
                                  yaxis_title='Recipe Name'
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


def get_choropleth(recipe_location_data):

    choropleth = px.choropleth(recipe_location_data,
                               locationmode="country names",
                               locations='country',
                               color='count',
                               color_continuous_scale="Greens",
                               range_color=[1, 110]
                               )
    choropleth.update_layout(#autosize=False,
                             margin=dict(l=0, r=0,b=0, t=0,pad=0, autoexpand=True),
                             #width=800,
                             # height=400,
                             )
    return choropleth

card_around_the_world_map = dbc.Card([dbc.CardHeader('Map (Hover Over Country)', style=styles['card_text']),
                                     dbc.CardBody(dbc.Row(dcc.Graph(figure=get_choropleth(location_counts_df)), justify='center'))
                                     ]
                                    )


card_around_the_world_background = get_text_card(around_the_world_text, 'About the Data')

content_around_the_world = html.Div([dbc.Row([dbc.Col(card_around_the_world_map, sm=8),
                                              dbc.Col(card_around_the_world_background, sm=4), #width = 8, md=3
                                              ],
                                             align="center"
                                             ),
                                     ])

content = html.Div(id="page-content", style=styles['content'])

app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE],
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
           )
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
                                  template="sandstone",
                                  )
                return fig, {'display': 'block'}     #returning the fig and unhiding the back button
            return date_graph(), {'display': 'none'}     #hiding the back button
    return date_graph(), {'display': 'none'}

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

def render_page_content(pathname):
    if pathname == "/":
        return html.Div(
            children=
            [ html.H2('Data Visualisation in the Kitchen', style=styles['card_text']),
              html.H4('Where Food & Data Meet', style=styles['card_text']),
              html.Br(),
              html.P(content_home),
              ]
        )
    elif pathname == "/over-time":
        return html.Div(
            children=
            [ html.H4("Progress Over Time", style=styles['card_text']),
              html.Br(),
              html.P(content_over_time),
              html.Br(),
              html.P(content_over_time_by_author)
            ]
        )
    elif pathname == "/my-top":
            return html.Div(
                children=
                [html.H4("My Top Cookbooks/ Authors / Recipes", style=styles['card_text']),
                html.Br(),
                html.P(content_my_top)
                ]
            )
    elif pathname == '/around-the-world':
        recipe_count = recipe_location_df.shape[0]
        return html.Div(
                children=[html.H4(f'Around The World in {recipe_count} Recipes', style=styles['card_text']),
                          html.Br(),
                          html.P(content_around_the_world)
                          ]
            )
    # If the user tries to reach a different page, return a 404 message
    else:
        return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


app.config['suppress_callback_exceptions']=True

if __name__=='__main__':
     application.run(host='0.0.0.0', port='8080')

# if __name__ == '__main__':
#     app.run_server(debug=True)
