import pandas as pd
from tqdm import tqdm
from pathlib import Path
from recipe_vectorizer import Vectorizer
from recipe_recommender import RecipeRecommender

if __name__ == "__main__":
    assets_path = Path(__file__).parent.parent / 'assets' / '2024-04-07'

    recipe_cooked_df = pd.read_csv(str(assets_path / 'out' / 'recipe_data.csv'))

    recipe_cook_df = recipe_cooked_df.drop_duplicates(subset=['recipe_name'])

    recipe_ingredient = pd.read_csv(assets_path / 'in' / 'recipe_ingredient.csv').dropna()
    recipe_df = pd.read_csv(assets_path / 'in' / 'recipe.csv')
    author_df = pd.read_csv(assets_path / 'in' / 'author.csv')
    author_df = pd.read_csv(assets_path / 'in' / 'author.csv')
    recipe_authorship_df = pd.read_csv(assets_path / 'in' / 'recipe_authorship.csv')
    book_df = pd.read_csv(assets_path / 'in' / 'book.csv', dtype={'id': int})
    bookmark_df = pd.read_csv(assets_path / 'in' / 'recipe_bookmark.csv')
    # I only need the dates when something was cooked
    bookmark_df = bookmark_df[~bookmark_df['bookmark_name'].isin(['Ottolenghi Guardian Book',
                                                                 "I've cooked this",
                                                                  "Favorite Recipes"
                                                                 ])]

    # remove those where there's a comment
    recipe_ingredient = recipe_ingredient.loc[~recipe_ingredient["ingredient_name"].str.contains("EYB Comments")]
    recipe_ingredient_df = recipe_ingredient.groupby('recipe_id')['ingredient_name'].agg(list).reset_index()
    merged_df = pd.merge(recipe_ingredient_df,
                         recipe_df[["id", "name", "book_id", "url"]],
                         left_on="recipe_id", right_on='id', how="left")
    # drop the old id used for recipe_id before merge
    merged_df = merged_df.drop(columns=['id'])

    # merge with author and author name
    merged_df = pd.merge(merged_df, recipe_authorship_df, on='recipe_id')
    merged_df = pd.merge(merged_df, author_df, left_on='author_id', right_on='id')
    merged_df = merged_df.rename(columns={'name_x': 'recipe_name',
                                          'name_y': 'author_name',
                                          })

    # drop the old id used for author_id before merge
    merged_df = merged_df.drop(columns=['id', 'author_id'])

    agg_funcs = { 'recipe_name': 'first',
                 'ingredient_name': 'first', 'book_id': 'first', 'url': 'first',
                 'author_name': lambda x: ' & '.join(x)}

    merged_df = merged_df.groupby('recipe_id', as_index=False).agg(agg_funcs)

    # merge with book to get the title
    merged_df = pd.merge(merged_df, book_df[['id', 'title']], left_on='book_id', right_on='id', how='left')
    merged_df['title'] = merged_df['title'].fillna('Online recipe')
    merged_df['recipe_name'] = merged_df['recipe_name'] + ' <> ' + merged_df['title']

    counts = merged_df['recipe_name'].value_counts()
    df_filtered = merged_df[merged_df['recipe_name'].isin(counts[counts >= 2].index)]

    # merge with recipe image paths
    recipe_images_df = pd.read_csv(str(assets_path / 'out' / 'image_url.csv'))
    merged_df = pd.merge(merged_df, recipe_images_df, on='recipe_id', how='left')

    # merge with recipe bookmarks to see how many items a recipe was cooked
    bookmark_df = bookmark_df.groupby('recipe_id', as_index=False).agg({'bookmark_name': lambda x: ' & '.join(x)})
    merged_df = pd.merge(merged_df, bookmark_df, on='recipe_id', how='left')

    # drop recipes from Larousse Gastronomique as they are boring
    merged_df = merged_df.loc[~merged_df['book_id'].isin([43535])]

    merged_df = merged_df.drop_duplicates(subset=['recipe_name']).reset_index(drop=True)

#    merged_df = merged_df.head(5000)

    recipe_ingredient_cooked_df = merged_df.loc[
        merged_df["recipe_id"].isin(recipe_cooked_df.recipe_id.unique())]
    recipe_ingredient_cooked_df = \
        recipe_ingredient_cooked_df.groupby(['recipe_id', 'recipe_name'])['ingredient_name']\
        .agg(list).reset_index()

    recipe_ingredient_not_cooked_df = merged_df.loc[
        ~merged_df["recipe_id"].isin(recipe_cooked_df.recipe_id.unique())
    ]
    recipe_ingredient_not_cooked_df = \
        recipe_ingredient_not_cooked_df.groupby(['recipe_id', 'recipe_name'])['ingredient_name']\
        .agg(list).reset_index()

    print(f'Total (unique) recipes: {merged_df.recipe_id.nunique()}')
    print(f'Total (unique) recipes cooked: {recipe_ingredient_cooked_df.recipe_id.nunique()}')
    print(f'Total (unique) recipes not cooked: {recipe_ingredient_not_cooked_df.recipe_id.nunique()}')
    print(merged_df.columns)

    vectorizer = Vectorizer()
    tfidf_matrix = vectorizer.fit_transform(merged_df)
    print('TFIDF Matrix shape', tfidf_matrix.shape)
    recommender = RecipeRecommender(merged_df, tfidf_matrix)
    recommendations = []
    for recipe_name, recipe_id, author_name, title, url, image_url, bookmark_name in \
            tqdm(zip(merged_df['recipe_name'],
                     merged_df['recipe_id'],
                     merged_df['author_name'],
                     merged_df['title'],
                     merged_df['url'],
                     merged_df['image_url'],
                     merged_df['bookmark_name']
                     ),
                 total=len(merged_df)):
        recs = recommender.get_recommendations(recipe_name, top_n=200)
        recommendations.append({'recipe_name': recipe_name,
                                'recipe_id': recipe_id,
                                'author_name': author_name,
                                'book_title': title,
                                'url': url,
                                'image_url': image_url,
                                'bookmark_name': bookmark_name,
                                'recs': recs
                                })

    # Create DataFrame from list of dictionaries with specified index
    recs_df = pd.DataFrame(recommendations)
    recs_df.to_json(assets_path / 'out' / 'recipe_recs.json', orient='records')
