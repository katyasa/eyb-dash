from sklearn.feature_extraction.text import TfidfVectorizer

class Vectorizer():
    def __init__(self, max_tokens=5000, sequence_length=50):  # Set a fixed sequence_length
        self.vect = TfidfVectorizer()

    def clean_text(self, ingredient_list):
        import re, unidecode
        ingredients_list_clean = []
        for ingredient in ingredient_list:
            items = re.split(' |-', ingredient)
            # Get rid of words containing non alphabet letters
            items = [word for word in items if word.isalpha()]
            # Turn everything to lowercase
            items = [word.lower() for word in items]
            # remove accents
            items = [unidecode.unidecode(word) for word in items]
            if items:
                ingredients_list_clean.append(' '.join(items))
        return ' '.join(ingredients_list_clean)

    def fit_transform(self, recipe_data):
        recipe_data['ingredients_clean'] = recipe_data['ingredient_name']\
            .apply(lambda x: self.clean_text(x))
        tfidf_matrix = self.vect.fit_transform(recipe_data['ingredients_clean'])
        return tfidf_matrix
