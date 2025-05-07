from crawl_pricecharting import *
from database_manager import *
from filesystem_manager import *
from tqdm import tqdm

def setup_database():
	drop_all()
	create_db()
	create_set_table()
	create_item_table()
	create_item_details_table()
	sets = get_all_sets()
	for set in tqdm(sets, desc="processing sets", unit="set"):
		insert_set(set)
		items = get_items_from_set(set)
		insert_items(items)

def setup_training_directories():
	for item in get_items_from_db():
		create_dir_for_item(item)

items_details = []
for item in tqdm(get_items_from_db(), desc="fetching item details", unit="item"):
	for i in range(10):
		try:
			items_details.append(get_item_details_from_item(item))
			break
		except:
			print('try ' + str(i))

insert_item_details(items_details)