from pathlib import Path
from item import Item

training_prefix = "training/"

def create_dir_for_item(item: Item):
	Path(training_prefix + str(item.id)).mkdir(parents=True, exist_ok=True)

def get_dir_for_item(item: Item) -> str:
	return training_prefix + str(item.id) + '/'

def save_image_to_file(content: bytes, file_name: str):
	with open(file_name, "wb") as f:
		f.write(content)