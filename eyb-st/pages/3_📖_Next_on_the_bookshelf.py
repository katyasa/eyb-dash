import sys
from pathlib import Path
import streamlit as st
import pandas as pd
book_recommender_path = Path(__file__).parent.parent.parent / 'eyb-recsys'
sys.path.insert(0, str(book_recommender_path))
from book_recommender import BookRecommender

def main():
    assets_path = Path(__file__).parent.parent.parent / 'assets' / '2024-02-01'
    book_shelf_filepath = assets_path / 'out' / 'shelf_book_filtered.csv'
    authorship_filepath = assets_path / 'in' / 'book_authorship.csv'
    author_filepath = assets_path / 'in' / 'author.csv'
    book_filepath = assets_path / 'in' / 'book.csv'

    similarities_filepath = assets_path / 'out' / 'similarities.npz'
    item_mapping_filepath = assets_path / 'out' / 'item_mapping.json'

    book_shelf_df = pd.read_csv(book_shelf_filepath)
    authorship_df = pd.read_csv(authorship_filepath)
    author_df = pd.read_csv(author_filepath)
    book_df = pd.read_csv(book_filepath, dtype={'id':str})

    st.set_page_config(
        page_title="Next on the Bookshelf",
        page_icon="📖",
    )

    st.title("Data's Choice: What's next on the Book Shelf?")

    my_user_history = book_shelf_df.loc[book_shelf_df['shelf_id'] == 'ksa']['book_id'].to_list()

    my_authorids = authorship_df.loc[authorship_df['book_id'].isin(my_user_history)]['author_id'].tolist()
    my_authors = author_df.loc[author_df['id'].isin(my_authorids), 'name'].tolist()
    selected_authors = st.sidebar.multiselect('Select authors:', my_authors)

    # Filter my_user_history to only include books written by the selected authors
    if selected_authors:  # Only filter if authors are selected
        print('Selected authors', selected_authors)
        selected_author_ids = author_df.loc[author_df['name'].isin(selected_authors), 'id'].tolist()
        print('Selected authors id', selected_author_ids)
        selected_book_ids = authorship_df.loc[authorship_df['author_id'].isin(selected_author_ids), 'book_id'].tolist()
        print('selected book ids', selected_book_ids)
        my_user_history = [book_id for book_id in my_user_history if book_id in selected_book_ids]

    print(79*'-')
    print('My User History', my_user_history)
    print(79*'-')

    # Get recommendations
    recommender = BookRecommender(user_history=my_user_history,
                                  similarity_matrix_filepath=similarities_filepath,
                                  item_mapping_filepath=item_mapping_filepath
                                  )

    # add an option to filter the recommended books by country:
    selected_countries = st.sidebar.multiselect('Select authors:', my_authors)

    # Filter my_user_history to only include books written by the selected authors
    if selected_countries:
        print('Selected authors', selected_authors)
        selected_author_ids = author_df.loc[author_df['name'].isin(selected_authors), 'id'].tolist()
        recommendations = recommender.get_recommendations()
        recommendations = [ rec for rec in recommendations if rec in selected_countries][:18]
    else:
        recommendations = recommender.get_recommendations(top_n=18)
    recommendations = [rec for rec in recommendations if rec not in my_user_history]
    if st.session_state.get('prev_recommendations') != recommendations:
        st.session_state['prev_recommendations'] = recommendations
        st.rerun()
    print('Recommendations:', recommendations)

    # Map book IDs to cover image URLs, book URLs, and titles
    book_id_to_cover_image_url = pd.Series(book_df.cover_image_url.values, index=book_df.id).to_dict()
    book_id_to_url = pd.Series(book_df.url.values, index=book_df.id).to_dict()
    book_id_to_title = pd.Series(book_df.title.values, index=book_df.id).to_dict()

    # Display recommendations
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

if __name__ == "__main__":
    main()

