from pathlib import Path
import pandas as pd

# The recipe URLs have be obtained: 1. from the EYB scraper. However, there's only about
# 2K images available on the site, so 2. I have to get more manually from random sites.
# This script reads the manually created recipe_image_url_manual.csv and recipe.csv
# and merges the image_urls into a new csv - image_url.csv


def create_csv_with_image_paths(recipe_file, images_file, outfile):
    recipe_df = pd.read_csv(recipe_file)
    print(recipe_df.columns)
    recipe_image_manual_df = pd.read_csv(images_file).drop_duplicates(subset=['recipe_id'])
    print(recipe_image_manual_df.columns)

    # Create a mapping series
    map_series = recipe_image_manual_df.set_index('recipe_id')['image_url']
    recipe_df['image_url'] = recipe_df['image_url'].fillna(recipe_df['id'].map(map_series))


    merged_df = recipe_df[['id', 'image_url']].rename(columns={'id': 'recipe_id'})
    merged_df.to_csv(outfile, index=False)


if __name__ == '__main__':
    assets_path = Path(__file__).parent / 'assets' / '2024-02-01'
    recipe_file = assets_path / 'in' / 'recipe.csv'
    recipe_images_manual = assets_path / 'out' / 'recipe_image_url_manual.csv'
    outfile = assets_path / 'out' / 'image_url.csv'
    create_csv_with_image_paths(recipe_file=recipe_file,
                                images_file=recipe_images_manual,
                                outfile=outfile
                                )

