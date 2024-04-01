from pathlib import Path
from book_similarities import ItemSimilarityConstructor

if __name__ == '__main__':
    assets_path = Path(__file__).parent.parent / 'assets' / '2024-02-01'
    book_shelf_filepath = assets_path / 'in' / 'shelf_book.at-least-10-in-common.csv'
    output_path = str(assets_path / 'out')
    sim_matrix_constructor = ItemSimilarityConstructor(
        user_item_filepath=book_shelf_filepath,
        outpath=output_path
    )
    sim_matrix_constructor.compute_item_similarities()

