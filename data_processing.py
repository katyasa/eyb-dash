#!/usr/bin/env python
#coding: utf-8

# Eat Your Books Project

# Data Processing

import pandas as pd

#data_folder_path = "assets/2023-02-05"
data_folder_path_in = "assets/2024-04-07"
data_folder_path_in = 'assets/2024-04-07/in'
data_folder_path_out = 'assets/2024-04-07/out'

# Examine Bookmarks

recipe_bookmark = pd.read_csv(data_folder_path_in + '/recipe_bookmark.csv')
print("----------------------------------------------------------------------")
print("Recipe bookmark")
print(recipe_bookmark.shape)
print(recipe_bookmark.head())
print("----------------------------------------------------------------------")


# Convert Date Column to Date Types

no_dates = ["I've cooked this"
            , 'Favorite Recipes'
            , 'Ottolenghi Guardian Book'
            ]

recipe_dates = recipe_bookmark.loc[~recipe_bookmark["bookmark_name"].isin(no_dates)]
recipe_dates['bookmark_name'] = recipe_dates['bookmark_name'].replace({'pre-2017': '2016-01'}).to_frame()
recipe_dates = recipe_dates.rename(columns={"bookmark_name": "date"})
print("----------------------------------------------------------------------")
print("Recipe Dates")
print(recipe_dates.head(100))
print(recipe_dates.shape)
print("----------------------------------------------------------------------")

### How Many Recipes Cooked

# first get the recipes that have a bookmark either "I've cooked this" or "Favourite Recipes"

recipe_cooked = recipe_bookmark.loc[recipe_bookmark['bookmark_name'].isin(["I've cooked this"])]
print("----------------------------------------------------------------------")
print("Recipe Cooked")
print(recipe_cooked.head())
print(recipe_cooked.shape)
print("----------------------------------------------------------------------")

#then merge those from above with those with a date, all with a date means they've been cooked

recipe_dates_cooked = recipe_dates.merge(recipe_cooked, on='recipe_id', how='outer')

print("----------------------------------------------------------------------")
print("Recipe Dates Cooked")
print(recipe_dates_cooked.head())
print(recipe_dates_cooked.shape)
print("----------------------------------------------------------------------")

# examine empty values
nulls = recipe_dates_cooked[recipe_dates_cooked.isna().any(axis=1)]
print("----------------------------------------------------------------------")
print("Recipe Dates Cooked Nulls")
print(nulls.head())
print(nulls.shape)
print("----------------------------------------------------------------------")
nulls.to_csv(data_folder_path_out + '/nulls.csv', index=False)
print("----------------------------------------------------------------------")


# merge recipe_id with authorship - more than one author per recipe
recipe_authorship = pd.read_csv(data_folder_path_in + '/recipe_authorship.csv')
recipe_dates_cooked_author = recipe_dates_cooked.merge(recipe_authorship,
                                                       on='recipe_id',
                                                       how='left'
                                                       )
print("Recipe authorship\n", recipe_dates_cooked_author.head(), recipe_dates_cooked_author.shape)


# merge above with author name
author = pd.read_csv(data_folder_path_in + '/author.csv')
print('Author\n', author.head())
recipe_dates_cooked_author_name = recipe_dates_cooked_author.merge(author,
                                                                    left_on='author_id',
                                                                    right_on='id',
                                                                    how='left'
                                                                    )
recipe_dates_cooked_author_name.drop(columns=['id'], inplace=True)
recipe_dates_cooked_author_name.rename(columns={"name": "author_name"},inplace=True)
print(recipe_dates_cooked_author_name.shape)
print("----------------------------------------------------------------------")

# merge above with book
recipe = pd.read_csv(data_folder_path_in + '/recipe.csv')
print('Recipe\n', recipe.head(), recipe.columns)
recipe_dates_cooked_author_name_book = recipe_dates_cooked_author_name.merge(recipe[['id', 'book_id', 'name']],
                                                                             left_on='recipe_id',
                                                                             right_on='id',
                                                                             how='left'
                                                                             )

recipe_dates_cooked_author_name_book = recipe_dates_cooked_author_name_book.drop(columns=['id'])
recipe_dates_cooked_author_name_book.rename(columns={'name': 'recipe_name'}, inplace=True)
print(recipe_dates_cooked_author_name_book.shape)
print("----------------------------------------------------------------------")

# merge above with book title
book = pd.read_csv(data_folder_path_in + '/book.csv')
print('Book\n', book.head(), book.columns)

recipe_dates_cooked_author_name_book = recipe_dates_cooked_author_name_book.merge(book[['id', 'title']],
                                                                                  left_on='book_id',
                                                                                  right_on='id',
                                                                                  how='left')
recipe_dates_cooked_author_name_book['recipe_name'] = \
    recipe_dates_cooked_author_name_book['recipe_name'] + ' <> ' + recipe_dates_cooked_author_name_book['title']
recipe_dates_cooked_author_name_book.drop(columns=['id'], inplace=True)
print(recipe_dates_cooked_author_name_book.shape)

print("----------------------------------------------------------------------")
# merge above with recipe ingredient
recipe_ingredient = pd.read_csv(data_folder_path_in + '/recipe_ingredient.csv')
print('Recipe Ingredient\n', recipe_ingredient.head(), recipe_ingredient.columns)

print("----------------------------------------------------------------------")
# # Examine recipe category. Here I only want location category to plot on a map
# recipe_category = pd.read_csv(data_folder_path_in + '/recipe_category.csv')
# loc_categories = ['Spanish', 'Jewish', 'Russian', 'Vietnamese',
#                   'Argentinian', 'Australian', 'Afghan', 'Mexican', 'Chilean', 'Swedish', 'Mauritian',
#                   'Brazilian', 'Mediterranean', 'Egyptian', 'South American',
#                   'Greek', 'Asian', 'Georgian', 'British', 'New Zealand', 'Italian', 'Israeli', 'Iraqi',
#                   'Cypriot', 'Maltese', 'Thai', 'American', 'Chinese', 'Indian', 'Burmese', 'Middle Eastern',
#                   'Persian', 'Ethiopian', 'Moroccan', 'North African', 'Portuguese',
#                   'Turkish', 'Malaysian', 'Sri Lankan', 'Indonesian', 'English', 'Korean',
#                   'Corsican', 'Japanese', 'Scandinavian', 'Irish', 'Nepali', 'Swiss', 'Dutch', 'French',
#                   'Iranian', 'Scottish', 'Singaporean', 'Cuban', 'Palestinian', 'Chili',
#                   'Yemeni', 'Cajun & Creole', 'Jamaican', 'Eritrean', 'Syrian', 'Lebanese', 'Pakistani',
#                   'Tunisian', 'Azerbaijani', 'East European'
#                   ]
#
# recipe_location = recipe_category[recipe_category['category_name'].isin(loc_categories)]
#
# #replace location categories to actual country names
# loc_dict = {'Spanish': 'Spain', 'Jewish': 'Israel', 'Russian': 'Russia',
#             'Vietnamese': 'Vietnam', 'Argentinian': 'Argentina',
#             'Australian': 'Australia', 'Afghan': 'Afghanistan', 'Mexican': 'Mexico',
#             'Chilean': 'Chile', 'Swedish': 'Sweden', 'Mauritian': 'Mauritius',
#             'Brazilian': 'Brazil', 'Mediterranean': 'Italy',
#             'Egyptian': 'Egypt', 'South American': 'South America',
#             'Greek': 'Greece', 'Asian': 'Asia', 'Georgian': 'Georgia', 'British': 'United Kingdom',
#             'New Zealand': 'New Zealand', 'Italian': 'Italy', 'Israeli': 'Israel', 'Iraqi': 'Iraq',
#             'Cypriot': 'Cyprus', 'Maltese': 'Malta', 'Thai': 'Thailand', 'American': 'United States of America',
#             'Chinese': 'China', 'Indian': 'India', 'Burmese': 'Burma', 'Middle Eastern': 'Israel',
#             'Persian': 'Iran', 'Ethiopian': 'Ethiopia', 'Moroccan': 'Morocco', 'North African': 'Morocco',
#             'Portuguese': 'Portugal', 'Turkish': 'Turkey', 'Malaysian': 'Malaysia', 'Sri Lankan': 'Sri Lanka',
#             'Indonesian': 'Indonesia', 'English': 'United Kingdom',
#             'Korean': 'South Korea', 'Corsican': 'Corsica', 'Japanese': 'Japan',
#             'Scandinavian': 'Sweden', 'Irish': 'Ireland', 'Nepali': 'Nepal',
#             'Swiss': 'Switzerland', 'Dutch': 'Netherlands', 'French': 'France',
#             'Iranian': 'France', 'Scottish': "Scotland", 'Singaporean': 'Singapore',
#             'Cuban': 'Cuba', 'Palestinian': 'Palestine', 'Chili': 'Chile',
#             'Yemeni': 'Yemen', 'Cajun & Creole': 'New Orleans', 'Jamaican': 'Jamaica',
#             'Eritrean': 'Eritrea', 'Syrian': 'Syria', 'Lebanese': 'Lebanon',
#             'Pakistani': 'Pakistan', 'Tunisian': 'Tunisia', 'Azerbaijani': 'Azerbaijan',
#             'East European': 'Ukraine'
#             }
#
# recipe_location = recipe_location.replace({"category_name": loc_dict})
# recipe_location = recipe_location.rename(columns={'category_name': 'location'})
# print("Recipe Location", recipe_location.head())
#
# # merge with recipe_dates_cooked
#
# # keeping only recipe_id, recipe_name and location columns
# recipe_location = recipe_dates_cooked_author_name_book[['recipe_id', 'recipe_name']].\
#     merge(recipe_location, on='recipe_id', how='left').drop_duplicates()
#
print("----------------------------------------------------------------------")
print("----------------------------------------------------------------------")
print(recipe_dates_cooked_author.head(), recipe_dates_cooked_author.shape)
print(recipe_dates_cooked_author_name.head(), recipe_dates_cooked_author_name.shape)
print(recipe_dates_cooked_author_name_book.head(), recipe_dates_cooked_author_name_book.shape)
# print(recipe_location.head(), recipe_location.shape)


print(">>> Validate >>>", recipe_dates_cooked_author_name_book
      .loc[recipe_dates_cooked_author_name_book['date']=='2023-12']['recipe_id'].nunique())
recipe_dates_cooked_author_name_book = recipe_dates_cooked_author_name_book.reset_index(drop=True)
recipe_dates_cooked_author_name_book = \
    recipe_dates_cooked_author_name_book.dropna(subset=['author_id', 'author_name', 'book_id', 'recipe_name', 'title'])
recipe_dates_cooked_author_name_book.to_csv(data_folder_path_out + '/recipe_data.csv', index=False)

# #recipe_location.to_csv(data_folder_path_out + '/recipe_data_location.csv', index=False)
# # print("----------------------------------------------------------------------")
#
recipes_cooked = recipe_dates_cooked_author_name_book.recipe_id.values.tolist()
print("----------------------------------------------------------------------")
print("Number of recipes cooked", len(recipes_cooked))
print("----------------------------------------------------------------------")

recipes_total = recipe['id'].values.tolist()
print("----------------------------------------------------------------------")
print("Number of total ", len(recipes_total))
print("----------------------------------------------------------------------")

unfound_count = 0
unfounds = list()

for recipe in recipes_cooked:
    if recipe not in recipes_total:
        unfound_count += 1
        unfounds.append(recipe)
print("----------------------------------------------------------------------")
print("Recipes in cooked not in total", unfound_count)
print(unfounds)
print("----------------------------------------------------------------------")
