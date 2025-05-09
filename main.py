from crawl_pricecharting import *
from database_manager import *
from filesystem_manager import *
from tqdm import tqdm
from playwright.sync_api import sync_playwright

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

def insert_item_details_into_db():
	items_details = []
	for item in tqdm(get_items_from_db(), desc="fetching item details", unit="item"):
		for i in range(10):
			try:
				items_details.append(get_item_details_from_item(item))
				break
			except:
				print('try ' + str(i))

	insert_item_details(items_details)

# setup_training_directories()
for set in range(10, 305):
	items = get_items_from_db(set)
	num = 1
	for item in tqdm(items, desc="processing set: "+ str(set), unit="item"):
		if set == 10:
			num+=1
			if num < 180:
				continue
			else:
				for url in get_ebay_links_from_item(item):
					try:
						image_url = get_image_url_from_ebay(url)

						if image_url:
							content = fetch_image_from_url(image_url)

							ebay_id = url.split('/')[-1]
							extension = image_url.split('.')[-1]

							file_path = get_dir_for_item(item) + ebay_id + '.' + extension
							save_image_to_file(content, file_path)
					except:
						print("failed to download " + image_url)
		else:
			pc_image_urls = get_image_urls_from_item(item)

			for image_url in pc_image_urls:
				try:
					content = fetch_image_from_url(image_url)

					pc_image_id = image_url.split('/')[-2]
					extension = image_url.split('.')[-1]

					file_path = get_dir_for_item(item) + pc_image_id + '.' + extension
					save_image_to_file(content, file_path)
				except:
					print("failed to download " + image_url)

			for url in get_ebay_links_from_item(item):
				try:
					image_url = get_image_url_from_ebay(url)

					if image_url:
						content = fetch_image_from_url(image_url)

						ebay_id = url.split('/')[-1]
						extension = image_url.split('.')[-1]

						file_path = get_dir_for_item(item) + ebay_id + '.' + extension
						save_image_to_file(content, file_path)
				except:
					print("failed to download " + image_url)

# insert_item_details_into_db()