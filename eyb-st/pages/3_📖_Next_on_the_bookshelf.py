import sys
from pathlib import Path
import streamlit as st
import pandas as pd
book_recommender_path = Path(__file__).parent.parent.parent / 'eyb-recsys'
sys.path.insert(0, str(book_recommender_path))
from book_recommender import BookRecommender

def load_data(assets_path):
    book_shelf_filepath = assets_path / 'in' / 'shelf_book.at-least-25-in-common.csv'
    authorship_filepath = assets_path / 'in' / 'book_authorship.csv'
    author_filepath = assets_path / 'in' / 'author.csv'
    book_filepath = assets_path / 'in' / 'book.csv'
    book_country_filepath = assets_path / 'in' / 'book_country.csv'

    book_shelf_df = pd.read_csv(book_shelf_filepath, dtype={'book_id': str})
    authorship_df = pd.read_csv(authorship_filepath, dtype={'book_id': str})
    author_df = pd.read_csv(author_filepath)
    book_df = pd.read_csv(book_filepath, dtype={'id': str})
    book_country_df = pd.read_csv(book_country_filepath, dtype={'book_id': str})
    return book_shelf_df, authorship_df, author_df, book_df, book_country_df

def filter_history_by_authors(my_user_history, selected_authors, author_df, authorship_df):
    selected_author_ids = author_df.loc[author_df['name'].isin(selected_authors), 'id'].tolist()
    print('Selected authors id', selected_author_ids)
    selected_book_ids = authorship_df.loc[authorship_df['author_id'].isin(selected_author_ids), 'book_id'].tolist()
    print('selected book ids', selected_book_ids)
    my_user_history = [book_id for book_id in my_user_history if book_id in selected_book_ids]
    return my_user_history

def filter_recommendations_by_country(recommendations, selected_countries):
    if selected_countries:
        print('Selected countries', selected_countries)
        recommendations = [rec for rec in recommendations if rec in selected_countries][:18]
    return recommendations

def display_recommendations(recommendations, book_df):
    # Map book IDs to cover image URLs, book URLs, and titles
    book_id_to_cover_image_url = pd.Series(book_df['cover_image_url'].values, index=book_df.id).to_dict()
    book_id_to_url = pd.Series(book_df['url'].values, index=book_df.id).to_dict()
    book_id_to_title = pd.Series(book_df['title'].values, index=book_df.id).to_dict()
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
                    book_id = rec
                    book_url = book_id_to_url[book_id]
                    cover_image_url = book_id_to_cover_image_url[book_id]
                    book_title = book_id_to_title[book_id]
                    columns[idx].image(cover_image_url, width=image_size[0])  # Display book cover image
                    columns[idx].write(f"[{book_title}]({book_url})")

                except Exception as e:
                    print(e)
                    pass
    else:
        st.write('No books found.')

def main():
    assets_path = Path(__file__).parent.parent.parent / 'assets' / '2024-02-01'
    similarities_filepath = assets_path / 'out' / 'similarities.npz'
    item_mapping_filepath = assets_path / 'out' / 'item_mapping.json'

    book_shelf_df, authorship_df, author_df, book_df, book_country_df = load_data(assets_path)

    st.set_page_config(
        page_title="Next on the Bookshelf",
        page_icon="📖",
    )

    st.title("Data's Choice: What's next on the Book Shelf?")

    my_user_history = book_shelf_df.loc[book_shelf_df['shelf_id'] == 'ksa']['book_id'].to_list()

    # my_authorids = authorship_df.loc[authorship_df['book_id'].isin(my_user_history)]['author_id'].tolist()
    # my_authors = author_df.loc[author_df['id'].isin(my_authorids), 'name'].tolist()
    # selected_authors = st.sidebar.multiselect('Filter user history:', my_authors)
    # print('Selected authors', selected_authors)
    # if selected_authors:
    #     my_user_history = filter_history_by_authors(my_user_history, selected_authors, author_df, authorship_df)

    print(79*'-')
    print('My User History', my_user_history, len(my_user_history))
    print(79*'-')

    # Get recommendations
    recommender = BookRecommender(user_history=my_user_history,
                                  similarity_matrix_filepath=similarities_filepath,
                                  item_mapping_filepath=item_mapping_filepath
                                  )

    recommendations = recommender.get_recommendations()

    # skip recommendations not contained in book.csv as those have no extra information
    recommendations = [rec for rec in recommendations if rec in book_df['id'].values]

    # # add an option to filter the recommended books by country:
    # my_countries = book_country_df['country_name'].unique()
    # selected_countries = st.sidebar.multiselect('Select country:', my_countries)
    # if selected_countries:
    #     recommendations = filter_recommendations_by_country(recommendations, selected_countries)[:18]
    # else:
    #     recommendations = recommendations[:18]
    #
    # if st.session_state.get('prev_recommendations') != recommendations:
    #     st.session_state['prev_recommendations'] = recommendations
    #     st.rerun()

    print('Recommendations:', recommendations)

    display_recommendations(recommendations, book_df)


if __name__ == "__main__":
    main()

