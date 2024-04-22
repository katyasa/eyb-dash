# Streamlit app of EYB
To get all running, there are several steps: 
1. Download data into `assets`
2. Run `data_processor.py` - pre-processes the data, filters some stuff, merges stuff etc
3. Run `generate_image_paths.py` - this is important as some exist on EYB (about 2K out of my 14K recipes) but the rest I need to manually find links.
   So this merges all neatly into a single output csv.
4. To get the recipe recommendations, run `create_recipe_recs.py`. This outputs `recs.json`
5. To get the book similarities, run `create_book_similarities`. This creates the similarity matrix and the item mappings which are then used by the
   app to compute the recommendations given user history. 
6. To get the book recommendations, run `create_book_recs.py`. This 
   computes the similarities given my own user history. To slow to do it on 
   the fly online
7. Now run the app with `streamlit run 0_....`  


## Recipes for the demo: 
* pea & ham pasta 
  * Only from this Author (Yotam Ottolenghi)
* ricotta and oregano meatballs 
  * In the mood for (Vegetarian)
* celebration cake
  * In the mood for (Cakes, large)
  
* ultimate traybake ragu
* walnut and halva cake
