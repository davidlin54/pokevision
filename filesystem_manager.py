from pathlib import Path
from item import Item

def create_dir_for_item(item: Item):
	Path("training/" + item.id).mkdir(parents=True, exist_ok=True)