import streamlit as st
import json
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="Next on the Menu",
    page_icon="🥗",
)

assets_path = Path(__file__).parent.parent.parent / 'assets' / '2024-02-01'
images_path = assets_path / 'images' / 'recipes'
recs_filepath = assets_path / 'out' / 'recs.json'
recipe_categories_filepath = assets_path / 'in' / 'recipe_category.csv'

# load necessary data: recipe recommendations and recipe categories.
with open(recs_filepath, 'r') as f:
    recipe_recs_data = json.load(f)
recipe_categories_df = pd.read_csv(recipe_categories_filepath)

# get the seeds - all items from the recipe recommendations data.
seeds = [item['recipe_name'] for item in recipe_recs_data]

def filter_recipes(recipe_name):
    for item in recipe_recs_data:
        if item['recipe_name'] == recipe_name:
            return item

def main():
    st.title("Data's Choice: What's Next on the Menu?")
    with st.sidebar:
        selected_recipe = st.selectbox(
            "Select Recipe",
            options=seeds,
            key='from_item'
        )
        with st.expander("Seed recipe details"):
            filtered_recipe = filter_recipes(selected_recipe)
            # Display image if URL exists
            if filtered_recipe['recipe_image_path']:
                st.image(filtered_recipe['recipe_image_path'])
            recipe_url = filtered_recipe['url']
            recipe_name = filtered_recipe['recipe_name']
            st.markdown(f"[{recipe_name}]({recipe_url})")
            st.write(f"**Author:** {filtered_recipe['author_name']}")
            st.write(f"**Book:** {filtered_recipe['book_title']}")
            if filtered_recipe['bookmark_name']:
                st.write(f"**Made on** {filtered_recipe['bookmark_name']}")

    recipe_search(selected_recipe)


def filter_dict_by_category(recipe_dict, id_list):
    # Filter the 'recs' list in the dictionary
    recipe_dict['recs'] = [rec for rec in recipe_dict['recs'] if rec['recipe_id'] in id_list]
    return recipe_dict

# Page for recipe search
def recipe_search(recipe_name):
    filtered_recipes = filter_recipes(recipe_name)
    print('Filtered recipes are', filtered_recipes, type(filtered_recipes))

    # Display filtered recipes
    st.subheader(f'More Shared Flavors with _{recipe_name}_')

    unique_categories = recipe_categories_df['category_name'].unique()
    selected_categories = st.sidebar.multiselect('In the Mood for...', sorted(unique_categories))
    # select the ids of the selected categories:
    selected_ids = recipe_categories_df.loc[recipe_categories_df['category_name'].isin(selected_categories)]['recipe_id'].tolist()
    if selected_categories:
        filtered_recipes = filter_dict_by_category(filtered_recipes, selected_ids)

    if len(filtered_recipes['recs']) > 0:
        num_items = st.sidebar.slider("How many recipes to display", 1, len(filtered_recipes['recs']),
                                      len(filtered_recipes['recs']))
        num_columns = 6
        num_rows = (num_items + num_columns - 1) // num_columns

        # Define the desired size for the images
        image_size = (100, 100)

        for i in range(num_rows):
            start_idx = i * num_columns
            end_idx = min((i + 1) * num_columns, num_items)
            row_recs = filtered_recipes['recs'][start_idx:end_idx]
            columns = st.columns(len(row_recs))

            for idx, rec in enumerate(row_recs):
                try:
                    columns[idx].image(rec['recipe_image_path'],
                                       #use_column_width=True,
                                       width=image_size[0],
                                       )
                except Exception as e:
                    print(e)
                    pass
                # Display the link
                columns[idx].write(f"[{rec['recipe_rec']}]({rec['url']})")
    else:
        st.write('No recipes found.')

    if st.session_state.get('prev_filter') != filtered_recipes:
        st.session_state['prev_filter'] = filtered_recipes
        st.rerun()


if __name__ == '__main__':
    main()
