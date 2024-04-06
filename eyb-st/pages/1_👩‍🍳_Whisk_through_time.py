import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
START_DATE = '2018-01-01'
END_DATE = '2024-03-31'
from pathlib import Path

st.set_page_config(
    page_title="Through Time",
    page_icon="👩‍🍳",
)
# create data structures
def process_input_data(data_df):
   '''
   Processes input data file: converts date field to time stamps, filters
   only values after Jan 2018, adds a field for month and year and
   splits title column into title and subtitle
   Return -> dataframe
   '''
   data_df = data_df[(data_df['date'] >= START_DATE) & (data_df['date'] < END_DATE)]
   data_df['month_year'] = pd.to_datetime(data_df['date']).dt.to_period('M')
   print('>>> Data df', data_df['title'])
   # new assets frame with split value columns
   # title_col = data_df["title"].str.split(":", n=1, expand=True)
   # # making separate first name column from new assets frame
   # data_df["title"] = title_col[0]
   # # making separate last name column from new assets frame
   # data_df["subtitle"] = title_col[1]
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


DATA_FOLDER = Path(__file__).parent.parent.parent / 'assets'
MARCH_FILES_PATH = DATA_FOLDER.joinpath('2024-02-01/out')

file_path = MARCH_FILES_PATH / 'recipe_data.csv'

recipes_df = pd.read_csv(file_path)
recipes = process_input_data(recipes_df)
recipe_by_date = groupby_date(recipes)
recipe_by_date_and_author = groupby_date_and_author(recipes)

# def date_graph():
#     '''Creates graph of progress over time.
#     Returns Plotly graph
#     '''
#     date_fig = px.line(recipe_by_date,
#                        x="date",
#                        y="recipe_count",
#                        markers=True,
#                        )
#     date_fig.update_layout()
#     date_fig.add_hline(y=recipe_by_date['recipe_count'].mean(),
#                        line_dash="dot",
#                        line_color="grey",
#                        annotation_text="Average Per Month",
#                        annotation_position="right"
#                        )
#
#     return date_fig

def date_graph_altair(data, author_data):
    '''Creates graph of progress over time with linked histogram.
    Returns Altair chart
    '''
    # Define selection for the bar chart
    selection = alt.selection_point(fields=['date'], empty='all', on='click')

    # Bar chart
    chart = alt.Chart(data).mark_bar().encode(
        x='date:O',
        y='recipe_count:Q',
        color=alt.condition(selection, alt.value('steelblue'), alt.value('lightgray')),
        tooltip=['date', 'recipe_count']
    ).add_params(selection).properties(
        width=600,
        height=400
    )

    # Rolling mean line
    mean_line = alt.Chart(data).mark_line(color='red').transform_window(
        rolling_mean='mean(recipe_count)',
        frame=[-9, 0]
    ).encode(
        x='date:O',
        y='rolling_mean:Q'
    )

    # Linked histogram
    histogram = alt.Chart(author_data).mark_bar().encode(
        x='recipe_count:Q',
        y='author_name:N',
        color='author_name:N',
        tooltip=['author_name', 'recipe_count']
    ).transform_filter(
        selection
    ).properties(
        width=200,
        height=300
    )

    # Combine charts and display
    combined_chart = (chart + mean_line | histogram)
    st.altair_chart(combined_chart.interactive(), use_container_width=False)



def plot_over_time():
    st.title('Whisking Through Time')

    date_graph_altair(recipe_by_date, recipe_by_date_and_author)


# Streamlit app
if __name__ == "__main__":
    plot_over_time()