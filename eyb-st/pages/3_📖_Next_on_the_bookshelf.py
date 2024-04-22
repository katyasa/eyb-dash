import streamlit as st
import pandas as pd
import json
import random

from pathlib import Path

@st.cache_data
def load_data(assets_path):
    book_shelf_filepath = assets_path / 'in' / 'shelf_book.at-least-25-in-common.csv'
    authorship_filepath = assets_path / 'in' / 'book_authorship.csv'
    author_filepath = assets_path / 'in' / 'author.csv'
    book_filepath = assets_path / 'in' / 'book.csv'
    book_country_filepath = assets_path / 'in' / 'book_country.csv'
    book_recs_filepath = assets_path / 'out' / 'book_recs.json'

    book_shelf_df = pd.read_csv(book_shelf_filepath, dtype={'book_id': str})
    authorship_df = pd.read_csv(authorship_filepath, dtype={'book_id': str})
    author_df = pd.read_csv(author_filepath)
    book_df = pd.read_csv(book_filepath, dtype={'id': str})
    book_country_df = pd.read_csv(book_country_filepath, dtype={'book_id': str})
    with open(book_recs_filepath, 'r') as f:
        recs_data = json.load(f)

    recommendations = [list(item.values())[0] for item in recs_data]
    return book_shelf_df, authorship_df, author_df, book_df, book_country_df, recommendations

def filter_history_by_authors(my_user_history, selected_authors, author_df, authorship_df):
    selected_author_ids = author_df.loc[author_df['name'].isin(selected_authors), 'id'].tolist()
    print('Selected authors id', selected_author_ids)
    selected_book_ids = authorship_df.loc[authorship_df['author_id'].isin(selected_author_ids), 'book_id'].tolist()
    print('selected book ids', selected_book_ids)
    my_user_history = [book_id for book_id in my_user_history if book_id in selected_book_ids]
    return my_user_history

def filter_recommendations_by_country(recommendations, selected_countries, book_country_df):
    # filter the book country dataframe to only rows of the selected_countries
    filtered_book_country_df = book_country_df[book_country_df['country_name'].isin(selected_countries)]

    # Filter the list of book_ids to only those in the filtered dataframe
    recommendations = \
        [book_id for book_id in recommendations if book_id in filtered_book_country_df['book_id'].values][:18]
    return recommendations


def display_recommendations(recommendations, book_df, book_country_df, feel_lucky_n=5, top_n=18):
    # Map book IDs to cover image URLs, book URLs, and titles
    book_id_to_cover_image_url = pd.Series(book_df['cover_image_url'].values, index=book_df.id).to_dict()
    book_id_to_url = pd.Series(book_df['url'].values, index=book_df.id).to_dict()
    book_id_to_title = pd.Series(book_df['title'].values, index=book_df.id).to_dict()
    feel_lucky = st.sidebar.checkbox('I feel lucky', value=False)
    if feel_lucky:
        random_books = random.sample(recommendations[:200], feel_lucky_n)
        recommendations = [ rec for rec in recommendations if rec not in random_books][:top_n-feel_lucky_n]
        for random_book in random_books:
            recommendations.insert(random.randint(0, min(18, len(recommendations))), random_book)

    # add an option to filter the recommended books by country:
    my_countries = book_country_df['country_name'].unique()
    selected_countries = st.sidebar.multiselect('Select country:', my_countries)
    if selected_countries:
        recommendations = filter_recommendations_by_country(recommendations, selected_countries, book_country_df)

    else:
        recommendations = recommendations[:top_n]

    if len(recommendations) > 0:
        num_items = st.sidebar.slider("How many books to display", 1, len(recommendations), len(recommendations))
        num_columns = 6
        num_rows = (num_items + num_columns - 1) // num_columns

        # Define the desired size for the images
        image_size = (100, 100)

        for i in range(num_rows):
            start_idx = i * num_columns
            end_idx = min((i + 1) * num_columns, num_items)
            row_recs = recommendations[start_idx:end_idx]
            columns = st.columns(len(row_recs))

            for idx, rec in enumerate(row_recs):
                try:
                    book_url = book_id_to_url[rec]
                    cover_image_url = book_id_to_cover_image_url[rec]
                    book_title = book_id_to_title[rec]
                    columns[idx].image(cover_image_url, width=image_size[0])  # Display book cover image
                    #columns[idx].write(f"[{book_title}]({book_url})")
                    columns[idx].markdown(
                        f"<a style='color: #ADD8E6;' href='{book_url}' target='_blank'>{book_title}</a>",
                        unsafe_allow_html=True)


                except Exception as e:
                    print(e)
                    pass
    else:
        st.write('No books found.')

def main():

    st.set_page_config(
        page_title="Next on the Bookshelf",
        page_icon="📖",
    )

    st.title("What's next on the Book Shelf?")

    assets_path = Path(__file__).parent.parent.parent / 'assets' / '2024-04-07'

    book_shelf_df, authorship_df, author_df, book_df, book_country_df, recommendations = \
        load_data(assets_path)
    # skip recommendations not contained in book.csv as those have no extra information
    recommendations = [rec for rec in recommendations ] #if rec in book_df['id'].values]
    # if st.session_state.get('prev_recommendations') != recommendations:
    #     st.session_state['prev_recommendations'] = recommendations
    #     st.rerun()

    display_recommendations(recommendations, book_df, book_country_df, feel_lucky_n=5,top_n=18)

if __name__ == "__main__":
    main()

