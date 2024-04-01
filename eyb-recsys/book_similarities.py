import json
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse import save_npz
from sklearn.metrics.pairwise import cosine_similarity

class ItemSimilarityConstructor:
    def __init__(self, user_item_filepath, outpath):
        self.user_item_df = pd.read_csv(user_item_filepath)
        print('User Item Matrix Shape', self.user_item_df.shape)
        self.user_item_df['book_id'] = self.user_item_df['book_id'].astype(str)
        self.outpath = outpath

    def _create_user_item_matrix(self):
        # create sparse matrix for efficient processing
        user_ids = self.user_item_df['shelf_id'].unique()
        item_ids = self.user_item_df['book_id'].unique()
        num_users = len(user_ids)
        num_items = len(item_ids)

        rows = []
        cols = []
        data = []

        for index, row in self.user_item_df.iterrows():
            user_index = np.where(user_ids == row['shelf_id'])[0][0]
            item_index = np.where(item_ids == row['book_id'])[0][0]
            rows.append(user_index)
            cols.append(item_index)
            data.append(1)  # Assume interaction exists, so set to 1

        # Create a CSR sparse matrix
        user_item_matrix = csr_matrix((data, (rows, cols)), shape=(num_users, num_items))
        print('User Item Matrix', user_item_matrix)

        save_npz(self.outpath + '/user_item_matrix.npz', user_item_matrix)

        user_index_mapping = {user_id: index for index, user_id in enumerate(user_ids)}
        item_index_mapping = {item_id: index for index, item_id in enumerate(item_ids)}

        with open(self.outpath + '/user_mapping.json', 'w') as f:
            json.dump(user_index_mapping, f)
        with open(self.outpath + '/item_mapping.json', 'w') as f:
            json.dump(item_index_mapping, f)

        return user_item_matrix

    def compute_item_similarities(self):
        user_item_matrix = self._create_user_item_matrix()
        similarities = cosine_similarity(user_item_matrix.T, dense_output=False)
        print('Computed similarities are:', similarities)
        print('Similarities matrix shape', similarities.shape)
        save_npz(self.outpath + '/similarities.npz', similarities)
