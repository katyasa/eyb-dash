import json
import pandas as pd
from pathlib import Path
import streamlit as st

assets_path = Path(__file__).parent.parent.parent / 'assets' / '2024-02-01'
images_path = assets_path / 'images' / 'recipes'
recs_filepath = assets_path / 'out' / 'recipe_recs.json'
recipe_categories_filepath = assets_path / 'in' / 'recipe_category.csv'
recipe_data_filepath = assets_path / 'out' / 'recipe_data.csv'
recipe_authorship_filepath = assets_path / 'in' / 'recipe_authorship.csv'

@st.cache_data
def load_data(recs_filepath, recipe_categories_filepath, recipe_data_filepath, recipe_authorship_filepath):
    with open(recs_filepath, 'r') as f:
        recipe_recs_data = json.load(f)
    recipe_categories = pd.read_csv(recipe_categories_filepath)
    recipe_data_df = pd.read_csv(recipe_data_filepath)
    recipe_authorship_df = pd.read_csv(recipe_authorship_filepath)
    return recipe_recs_data, recipe_categories, recipe_data_df, recipe_authorship_df

recipe_recs_data, recipe_categories, recipe_data_df, recipe_authorship_df = \
    load_data(recs_filepath, recipe_categories_filepath, recipe_data_filepath, recipe_authorship_filepath)

# Get the seeds - all items from the recipe recommendations data.
SEEDS = [item['recipe_name'] for item in recipe_recs_data]

def filter_recipes(recipe_name):
    for item in recipe_recs_data:
        if item['recipe_name'] == recipe_name:
            return item

def display_seed_recipe_details(selected_recipe):
    filtered_recipe = filter_recipes(selected_recipe)
    # Display image if URL exists
    if filtered_recipe['image_url']:
        st.image(filtered_recipe['image_url'], use_column_width=True)
    recipe_url = filtered_recipe['url']
    recipe_name = filtered_recipe['recipe_name'].split('<>')[0]
    st.markdown(f"[{recipe_name}]({recipe_url})")
    st.write(f"**Author:**  \n{filtered_recipe['author_name']}")
    st.write(f"**Book:**  \n {filtered_recipe['book_title']}")
    if filtered_recipe['bookmark_name']:
        st.write(f"**Made on:**  \n {filtered_recipe['bookmark_name']}")

def filter_dict_by_category(recipe_dict, id_list):
    # Filter the 'recs' list in the dictionary
    recipe_dict['recs'] = [rec for rec in recipe_dict['recs'] if rec['recipe_id'] in id_list]
    return recipe_dict

def display_filtered_recipes(filtered_recipes, num_items):
    num_columns = 6
    num_rows = (num_items + num_columns - 1) // num_columns

    # Define the desired size for the images
    image_size = (100, 100)

    for i in range(num_rows):
        start_idx = i * num_columns
        end_idx = min((i + 1) * num_columns, num_items)
        row_recs = filtered_recipes['recs'][start_idx:end_idx]
        columns = st.columns(num_columns)  # Always create 6 columns

        for idx, rec in enumerate(row_recs):
            try:
                columns[idx].image(rec['image_url'], width=image_size[0],use_column_width=True)
            except Exception as e:
                pass
            columns[idx].write(f"[{rec['recipe_rec']}]({rec['url']})")

def recipe_search(recipe_name):
    filtered_recipes = filter_recipes(recipe_name)
    print('Filtered recipes are', filtered_recipes, type(filtered_recipes))
    print(len(filtered_recipes['recs']))

    # Display filtered recipes
    recipe_name = recipe_name.split('<>')[0].strip()
    st.subheader(f'More Shared Flavours with *{recipe_name}*')

    # optional filter by category
    unique_categories = recipe_categories['category_name'].unique()
    selected_categories = st.sidebar.multiselect('In the Mood for...', sorted(unique_categories))
    # select the ids of the selected categories:
    selected_ids = recipe_categories.loc[recipe_categories['category_name'].isin(selected_categories)]['recipe_id'].tolist()
    if selected_categories:
        filtered_recipes = filter_dict_by_category(filtered_recipes, selected_ids)

    # optional filter by author
    unique_authors = recipe_data_df['author_name'].unique()
    selected_authors = st.sidebar.multiselect('Only from this author...', sorted(unique_authors))
    selected_authors_ids = recipe_data_df.loc[recipe_data_df['author_name'].isin(selected_authors)]['author_id']
    recipe_ids_by_selected_authors = \
        recipe_authorship_df.loc[recipe_authorship_df['author_id'].isin(selected_authors_ids)]['recipe_id'].tolist()
    if selected_authors:
        filtered_recipes = filter_dict_by_category(filtered_recipes, recipe_ids_by_selected_authors)

    # this truncates the list only for the entry (no filtered recs), the filter by author/ category is
    # applied to the original 200 list.
    filtered_recipes = {k: (val[:36] if k == 'recs' else val) for k, val in filtered_recipes.items()}

    if len(filtered_recipes['recs']) > 0:
        num_items = st.sidebar.slider("How many recipes to display", 0, len(filtered_recipes['recs']),
                                      len(filtered_recipes['recs']))
        display_filtered_recipes(filtered_recipes, num_items)
    else:
        st.write('No recipes found.')

    if st.session_state.get('prev_filter') != filtered_recipes:
        st.session_state['prev_filter'] = filtered_recipes
        st.rerun()

def main():
    st.title("What's Next on the Menu?")
    with st.sidebar:
        selected_recipe = st.selectbox(
            "Select Recipe",
            options=SEEDS
        )
        with st.expander("Recipe details"):
            display_seed_recipe_details(selected_recipe)

    recipe_search(selected_recipe)

if __name__ == "__main__":
    main()
