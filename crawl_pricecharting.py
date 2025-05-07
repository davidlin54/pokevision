import requests
from database_manager import *
from bs4 import BeautifulSoup
from set import Set
from item import Item

base_url = 'https://www.pricecharting.com'
category_path = '/category/pokemon-cards'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

def get_post_response(url: str):
	response = requests.post(url, headers=headers)
	body = response.text
	return body

def get_all_sets() -> list[Set]:
	base_response = get_post_response(base_url + category_path)
	soup = BeautifulSoup(base_response, 'html.parser')

	target_div = soup.find('div', class_='home-box all', style='margin-top: 0px;')

	if target_div:
	    list_items = target_div.find_all('li')

	    result = []

	    for li in list_items:
	    	result.append(Set(li.get_text().strip(), base_url + li.find('a').get('href')))

	    return result

	else:
	    raise Exception("Target div not found.")

def get_items_from_set(set: Set) -> list[str]:
	response = get_post_response(set.url)

	soup = BeautifulSoup(response, 'html.parser')
	target_table = soup.find('table', class_='hoverable-rows', id='games_table').find('tbody')

	if target_table:
		table_rows = target_table.find_all('tr')

		result = []

		for row in table_rows:
			id = row.get('data-product')
			data = row.find('td', class_='title')
			result.append(Item(id, data.get_text().strip(), base_url + data.find('a').get('href')))

		return result
	else:
	    raise Exception("Target table not found. " + url)

drop_all()
create_db()
create_set_table()
create_item_table()
sets = get_all_sets()
for id, set in enumerate(sets, 1):
	insert_set(set)
	items = get_items_from_set(set)
	insert_items(id, items)