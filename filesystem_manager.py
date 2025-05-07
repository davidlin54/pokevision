from pathlib import Path
from item import Item

def create_dir_for_item(item: Item):
	Path("training/" + str(item.set_id) + "/" + item.id).mkdir(parents=True, exist_ok=True)