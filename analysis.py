import pandas as pd
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt

assets_path = Path(__file__).parent/ 'assets' / '2024-04-07'
print(assets_path)
book_shelf_filepath = assets_path / 'in' / 'shelf_book.at-least-5-in-common.csv'

book_shelf_df = pd.read_csv(book_shelf_filepath)
value_counts_df = book_shelf_df['shelf_id'].value_counts().to_frame().reset_index()

shelf_counts = book_shelf_df['shelf_id'].value_counts()

filtered_df = book_shelf_df[book_shelf_df['shelf_id'].map(shelf_counts) <= 200]
print(filtered_df.head())
print(filtered_df.shape)
filtered_df.to_csv(assets_path / 'out' / 'shelf_book.at-least-5.no_outliers.csv')