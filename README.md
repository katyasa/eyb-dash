# Streamlit app of EYB
To get all running, there are several steps: 
1. Download data into `assets`
2. Run `data_processor.py` - pre-processes the data, filters some stuff, merges stuff etc
3. Run `generate_image_paths.py` - this is important as some exist on EYB (about 2K out of my 14K recipes) but the rest I need to manually find links.
   So this merges all neatly into a single output csv.
4. To get the recipe recommendations, run `create_recipe_recs.py`. This outputs `recs.json`
5. To get the book similarities, run `create_book_similarities`. This creates the similarity matrix and the item mappings which are then used by the
   app to compute the recommendations given user history. This happens on the fly when loading the app. It's a bit slow with large matrixes. Buuu!
6. Now run the app with `streamlit run 0_....`  