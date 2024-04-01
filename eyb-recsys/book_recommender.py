import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.sparse import load_npz, csr_matrix

class BookRecommender:
    def __init__(self, user_history,
                 similarity_matrix_filepath='similarities.npz',
                 item_mapping_filepath='item_mapping.json'):
        self.similarities = load_npz(similarity_matrix_filepath)
        with open(item_mapping_filepath, 'r') as f:
            self.item_mapping = json.load(f)
        self.user_history = [str(item) for item in user_history]

    def get_recommendations(self, top_n=12):
        user_vector = np.zeros(self.similarities.shape[0])
        # Update the user vector based on user history
        for item in self.user_history:
            if item in self.item_mapping:  # Check if the item exists in the item_index_mapping
                user_vector[self.item_mapping[item]] = 1
        user_vector_sparse = csr_matrix(user_vector)
        item_scores = user_vector_sparse.dot(self.similarities)
        item_scores_dense = item_scores.toarray()
        # Get the indices of the top N items
        top_item_indices = np.argsort(item_scores_dense)[::-1]

        top_items = [item for item, index in self.item_mapping.items()
                     if index in top_item_indices]

        recommended_items = [item for item in top_items if item not in self.user_history][:top_n]
        return recommended_items

# if __name__ == '__main__':
#     assets_path = Path(__file__).parent.parent / 'assets' / '2024-02-01' / 'in'
#
#     book_shelf_filepath = assets_path / 'shelf_book.at-least-10-in-common.csv'
#     authorship_filepath = assets_path / 'book_authorship.csv'
#     author_filepath = assets_path / 'author.csv'
#
#     # Get the recommendations based on the computed similarities
#     book_shelf_df = pd.read_csv(book_shelf_filepath)
#     authorship_df = pd.read_csv(authorship_filepath)
#     author_df = pd.read_csv(author_filepath)
#
#     user_histories = book_shelf_df.loc[book_shelf_df['shelf_id']=='ksa']['book_id'].to_list()
#     recommender = BookRecommender(user_histories)
#     recommendations = recommender.get_recommendations()[:12]
