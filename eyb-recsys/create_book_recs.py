import pandas as pd
from pathlib import Path
from book_recommender import BookRecommender

if __name__ == "__main__":
    assets_path = Path(__file__).parent.parent / 'assets' / '2024-04-07'

    book_shelf_filepath = assets_path / 'in' / 'shelf_book.at-least-25-in-common.csv'
    similarities_filepath = assets_path / 'out' / 'similarities.npz'
    item_mapping_filepath = assets_path / 'out' / 'item_mapping.json'

    book_shelf_df = pd.read_csv(book_shelf_filepath, dtype={'book_id': str})
    my_user_history = book_shelf_df.loc[book_shelf_df['shelf_id'] == 'ksa']['book_id'].to_list()


    print(79*'-')
    print('My User History', my_user_history, len(my_user_history))
    print(79*'-')

    # Get recommendations
    recommender = BookRecommender(user_history=my_user_history,
                                  similarity_matrix_filepath=similarities_filepath,
                                  item_mapping_filepath=item_mapping_filepath
                                  )

    recommendations = recommender.get_recommendations(top_n=5000)
    recs_df = pd.DataFrame(recommendations)
    recs_df.to_json(assets_path / 'out' / 'book_recs.json', orient='records')
