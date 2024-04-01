import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class RecipeRecommender:
    def __init__(self, recipe_data, tfidf_matrix):
        self.recipe_data = recipe_data
        self.tfidf_matrix = tfidf_matrix
        self.build_similarity_matrix()
        self.get_indices(recipe_data)

    def build_similarity_matrix(self):
        self.recipe_similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        print('Recipe similarity matrix', self.recipe_similarity_matrix.shape)

    def get_indices(self, recipe_data):
        recipe_data = recipe_data.drop_duplicates(subset=['recipe_name'])
        # generate mapping between recipes and index
        indices = pd.Series(recipe_data.index,
                            index=recipe_data['recipe_name']).drop_duplicates()
        self.indices = indices

    def get_recommendations(self, recipe_name, top_n=10):
        # get the index of the recipe that matches the title
        idx = self.indices[recipe_name]
        # get the pairwise similarity scores for the given recipe
        sim_scores = self.recipe_similarity_matrix[idx]
        # enumerate the similarity scores and sort based on them
        sim_scores_with_indices = list(enumerate(sim_scores))
        sim_scores_with_indices = sorted(sim_scores_with_indices,
                                         key=lambda x: x[1],
                                         reverse=True)
        sim_scores_with_indices = sim_scores_with_indices[1:top_n]
        # get indices
        recipe_indices = [i[0] for i in sim_scores_with_indices]
        # return the top_n most similar recipes
        recipe_recs = self.recipe_data['recipe_name'].iloc[recipe_indices].tolist()
        recipe_ids = self.recipe_data['recipe_id'].iloc[recipe_indices].tolist()
        book_ids = self.recipe_data['book_id'].iloc[recipe_indices].tolist()
        recipe_urls = self.recipe_data['url'].iloc[recipe_indices].tolist()
        recipe_image_paths = self.recipe_data['recipe_image_path'].iloc[recipe_indices].tolist()
        recs = [ {'recipe_id': recipe_id,
                  'recipe_rec': recipe_recs,
                  'book_id': book_id,
                  'url': recipe_url,
                  'recipe_image_path': recipe_image_path
                  }
                for recipe_id, recipe_recs, book_id, recipe_url, recipe_image_path
                 in zip(recipe_ids, recipe_recs, book_ids, recipe_urls, recipe_image_paths)
                ]

        return recs
