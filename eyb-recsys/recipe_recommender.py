import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class RecipeRecommender:
    def __init__(self, recipe_data, tfidf_matrix):
        self.recipe_data = recipe_data
        self.tfidf_matrix = tfidf_matrix
        self.build_similarity_matrix()

    def build_similarity_matrix(self):
        self.recipe_similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        print('Recipe similarity matrix', self.recipe_similarity_matrix.shape)

    def get_indices(self):
        # generate mapping between recipes and index
        indices = pd.Series( self.recipe_data.index,
                            index=self.recipe_data['recipe_name'])
        return indices

    def get_recommendations(self, recipe_name, top_n=100):
        indices = self.get_indices()
        # get the index of the recipe that matches the recipe name
        idx = indices[recipe_name]
        # get the pairwise similarity score for the given recipe
        sim_scores = self.recipe_similarity_matrix[idx]
        # enumerate the similarity scores and sort based on them
        sim_scores_with_indices = list(enumerate(sim_scores))
        sim_scores_with_indices = sorted(sim_scores_with_indices,
                                         key=lambda x: x[1],
                                         reverse=True)
        sim_scores_with_indices = sim_scores_with_indices[1:top_n+1]
        # get indices
        recipe_indices = [i[0] for i in sim_scores_with_indices]
        # return the top_n most similar recipes
   #     recipe_recs = [self.recipe_data['recipe_name'].iloc[i].split("<>")[0] for i in recipe_indices]
        recipe_recs = self.recipe_data['recipe_name'].iloc[recipe_indices].tolist()
        # get rid of the appended title as the page with recs gets too cluttered
        recipe_recs = [recipe_name.split("<>")[0] for recipe_name in recipe_recs]
        recipe_ids = self.recipe_data['recipe_id'].iloc[recipe_indices].tolist()
        book_ids = self.recipe_data['book_id'].iloc[recipe_indices].tolist()
        recipe_urls = self.recipe_data['url'].iloc[recipe_indices].tolist()
        image_urls = self.recipe_data['image_url'].iloc[recipe_indices].tolist()
        recs = [{'recipe_id': recipe_id,
                 'recipe_rec': recipe_recs,
                 'book_id': book_id,
                 'url': recipe_url,
                 'image_url': image_url
                 }
                for recipe_id, recipe_recs, book_id, recipe_url, image_url
                in zip(recipe_ids, recipe_recs, book_ids, recipe_urls, image_urls)
                ]

        return recs
