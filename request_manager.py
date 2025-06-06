import requests
import re
import os
import sys
import dotenv
from bs4 import BeautifulSoup
from set import Set
from item import Item
from item_details import ItemDetails
from duckduckgo_search import DDGS
from urllib.parse import quote

base_url = 'https://www.pricecharting.com'
category_path = '/category/pokemon-cards'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
max_retry = 5
timeout_sec = 10

def get_post_response(url: str, timeout: int=1000, stream: bool=False):
    response = requests.post(url, headers=headers, timeout=timeout, stream=stream)
    return response

def get_post_response_body(url: str, timeout: int=1000):
    response = get_post_response(url, timeout, False)
    body = response.text
    return body

def get_all_sets() -> list[Set]:
    base_response = get_post_response_body(base_url + category_path)
    soup = BeautifulSoup(base_response, 'html.parser')

    result = []
    count = 1

    target_div = soup.find('div', class_='home-box all', style='margin-top: 0px;')
    if target_div:
        list_items = target_div.find_all('li')

        for li in list_items:
            result.append(Set(count, li.get_text().strip(), base_url + li.find('a').get('href')))
            count+=1
    else:
        raise Exception("Target div not found.")


    target_div = soup.find('div', class_='home-box', style='margin-top: 10px;')
    if target_div:
        list_items = target_div.find('ul', class_='newest').find_all('li')

        for li in list_items:
            result.append(Set(count, li.find('a').get_text().strip(), base_url + li.find('a').get('href')))
            count+=1
    else:
        raise Exception("Target div not found.")

    return result


def get_items_from_set(set: Set, cursor: int=None) -> list[str]:
    response = get_post_response_body(set.url + ('' if cursor is None else '?cursor=' + str(cursor)))

    soup = BeautifulSoup(response, 'html.parser')
    target_table = soup.find('table', class_='hoverable-rows', id='games_table').find('tbody')

    if target_table:
        table_rows = target_table.find_all('tr')

        result = []

        for row in table_rows:
            id = row.get('data-product')
            data = row.find('td', class_='title')
            result.append(Item(int(id), data.get_text().strip(), base_url + data.find('a').get('href'), set.id))

        if table_rows:
            result.extend(get_items_from_set(set, 50 if cursor is None else cursor + 50))
        return list(dict.fromkeys(result))
    else:
        raise Exception("Target table not found. " + url)

def strip_price_string(price: str) -> float:
    stripped = re.sub(r'[^0-9.]', '', price)
    return 0 if stripped == '' else float(stripped)

def get_item_details_from_item(item : Item) -> ItemDetails:
    for attempt in range(1, max_retry):
        try:
            response = get_post_response_body(item.url, timeout_sec)

            soup = BeautifulSoup(response, 'html.parser')
            details = ItemDetails(item_id=item.id)

            # find prices
            target_div = soup.find('div', id='full-prices')

            if target_div:
                table = target_div.find('table')

                rows = table.find_all('tr')

                for row in rows:
                    data = row.find_all('td')
                    category = data[0].get_text()
                    price = strip_price_string(data[1].get_text())

                    if category == 'Ungraded':
                        details.ungraded_price = price
                    elif category == 'Grade 1':
                        details.psa_1_price = price
                    elif category == 'Grade 2':
                        details.psa_2_price = price
                    elif category == 'Grade 3':
                        details.psa_3_price = price
                    elif category == 'Grade 4':
                        details.psa_4_price = price
                    elif category == 'Grade 5':
                        details.psa_5_price = price
                    elif category == 'Grade 6':
                        details.psa_6_price = price
                    elif category == 'Grade 7':
                        details.psa_7_price = price
                    elif category == 'Grade 8':
                        details.psa_8_price = price
                    elif category == 'Grade 9':
                        details.psa_9_price = price
                    elif category == 'PSA 10':
                        details.psa_10_price = price
            else:
                raise Exception("Price table not found. " + item.url)

            # find population
            target_table = soup.find('table', class_='hoverable-rows population')

            if target_table:
                body = target_table.find('tbody')
                data = body.find('tr').find_all('td')
                details.psa_1_pop = int(strip_price_string(data[1].get_text()))
                details.psa_2_pop = int(strip_price_string(data[2].get_text()))
                details.psa_3_pop = int(strip_price_string(data[3].get_text()))
                details.psa_4_pop = int(strip_price_string(data[4].get_text()))
                details.psa_5_pop = int(strip_price_string(data[5].get_text()))
                details.psa_6_pop = int(strip_price_string(data[6].get_text()))
                details.psa_7_pop = int(strip_price_string(data[7].get_text()))
                details.psa_8_pop = int(strip_price_string(data[8].get_text()))
                details.psa_9_pop = int(strip_price_string(data[9].get_text()))
                details.psa_10_pop = int(strip_price_string(data[10].get_text()))

            return details
        except: 
            print('retry number ' + str(attempt) + ' for item: ' + str(item.id))
    return None

def get_ebay_links_from_item(item: Item) -> list[str]:
    for attempt in range(1, max_retry):
        try:
            response = get_post_response_body(item.url, timeout_sec)

            soup = BeautifulSoup(response, 'html.parser')
            ebay_elements = soup.find_all('a', target='_blank', class_='js-ebay-completed-sale')

            result = []
            for ebay_element in ebay_elements:
                ebay_url = ebay_element.get('href').split('?')[0].replace('com', 'ca', 1)
                result.append(ebay_url)

            return result
        except:
            print('retry number ' + str(attempt) + ' for ebay links for item: ' + str(item.id))

    return []


def get_image_urls_from_item(item: Item) -> list[str]:
    for attempt in range(1, max_retry):
        try:
            response = get_post_response_body(item.url, timeout_sec)

            soup = BeautifulSoup(response, 'html.parser')
            extra_images = soup.find('div', id='extra-images')

            result = []
            all_images = extra_images.find_all('a')
            for image in all_images:
                result.append(image.get('href'))

            return result
        except:
            print('retry number ' + str(attempt) + ' for ebay image urls for item: ' + str(item.id))

    return []

def format_ebay_image_url(original_url: str) -> str:
    new_url = re.sub(r's-l\d+\.(jpg|jpeg|webp|png)', 's-l225.webp', original_url)
    return new_url

def get_image_url_from_ebay(ebay_url: str) -> str:
    for attempt in range(1, max_retry):
        try:
            response = get_post_response(ebay_url, timeout_sec, True)
            response.raise_for_status()

            # Accumulate chunks until we reach the end of </head> tag
            chunks = []
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                chunks.append(chunk)
                html_so_far = ''.join(chunks)
                if '</head>' in html_so_far.lower():
                    break
            response.close()

            soup = BeautifulSoup(html_so_far, 'html.parser')

            error = soup.find('div', class_='error-page-v2')
            if error:
                return None

            og_image = soup.find("meta", property="og:image")

            if og_image and og_image.get("content"):
                original_url = og_image["content"]
                return format_ebay_image_url(original_url)
        except Exception as e:
            print('retry number ' + str(attempt) + ' for image url from ebay url: ' + ebay_url + '. with error' + str(e))

def search_ebay_for_item(item: Item, set: Set, max_results: int = 1000) -> list[str]:
    keyword = '\"' + set.name.replace("Pokemon ", "") + '\" \"' + item.name.replace('[', '').replace(']', '') + '\"'
    keyword = re.sub(r'\b(19|20)\d{2}\b', '', keyword)

    # limit 240 and search best match first
    ebay_url = f"https://www.ebay.ca/sch/i.html?_nkw={quote(keyword)}&_ipg=240&_sop=12"
    for attempt in range(1, max_retry):
        try:
            result = []
            response = get_post_response_body(ebay_url, timeout_sec)

            soup = BeautifulSoup(response, 'html.parser')

            h1 = soup.find('h1', class_='srp-controls__count-heading')
            count = min(int(h1.find('span', class_='BOLD').get_text()), max_results)

            image_divs = soup.find('div', class_='srp-river-results clearfix').find_all('div', class_='s-item__image-wrapper image-treatment')

            for image_div in image_divs[:count]:
                image_url = image_div.find('img').get('src')
                image_url = format_ebay_image_url(image_url)
                result.append(image_url)

            return result
        except Exception as e:
            print('retry number ' + str(attempt) + ' for ebay search url: ' + ebay_url + '. with error' + str(e))

    return []

def fetch_image_from_url(image_url: str) -> bytes:
    for attempt in range(1, max_retry):
        try:
            response = requests.get(image_url, timeout=timeout_sec)

            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
        except:
            print('retry number ' + str(attempt) + ' for downloading image: ' + image_url)

def get_image_urls_from_ddg(prompt: str, images_requested: int) -> list[str]:
    # Search for images
    for attempt in range(1, max_retry):
        try:
            dotenv.load_dotenv()
            proxy = os.getenv('proxy_server')
            results = DDGS(proxy=proxy, timeout=20).images(keywords=prompt, max_results=images_requested)

            # Extract image URLs
            image_urls = [r["image"] for r in results]

            return image_urls
        except Exception as e:
            print(f"An error occured using duckduckgo_search: {e}")
    return []