#!/usr/bin/env python3

from request_manager import *
from database_manager import *
from filesystem_manager import *
from tqdm.asyncio import tqdm as tqdm_async
from tqdm import tqdm as tqdm
import asyncio
import hashlib
import config
import sys

def string_to_filename_hash(s):
    # Use SHA-256 for strong, consistent hashing
    return hashlib.sha256(s.encode()).hexdigest()

def save_image_to_file(filesystem_manager: FilesystemManager, image_url: str, item: Item) -> bool:
    image_url = image_url.split('?')[0]
    image_name = string_to_filename_hash(image_url)
    extension = image_url.split('.')[-1]

    file_name = image_name + '.' + extension
    staging_file_path = filesystem_manager.get_dir_for_item(config.staging_dir, item) + file_name
    training_file_path = filesystem_manager.get_dir_for_item(config.training_dir, item) + file_name
    val_file_path = filesystem_manager.get_dir_for_item(config.val_dir, item) + file_name

    if filesystem_manager.file_exists(staging_file_path) or filesystem_manager.file_exists(training_file_path) or filesystem_manager.file_exists(val_file_path):
        return False

    content = fetch_image_from_url(image_url)

    filesystem_manager.save_image_to_file(content, staging_file_path)
    return True

def download_item_images_and_save(filesystem_manager: FilesystemManager, item: Item, set: Set):
    filesystem_manager.create_dirs_for_item(item)
    image_count = filesystem_manager.get_num_images_for_item(item)

    if (image_count > config.max_images_per_item):
        return

    pc_image_urls = get_image_urls_from_item(item)

    for image_url in pc_image_urls:
        try:
            saved_to_file = save_image_to_file(filesystem_manager, image_url, item)

            if saved_to_file:
                image_count += 1
        except Exception as e:
            print("failed to download " + str(image_url) + ". " + str(e))

    for url in get_ebay_links_from_item(item)[:config.max_images_per_item + 1]:
        try:
            image_url = get_image_url_from_ebay(url)

            if image_url:
                saved_to_file = save_image_to_file(filesystem_manager, image_url, item)

                if saved_to_file:
                    image_count += 1
        except Exception as e:
            print("failed to download " + str(image_url) + ". " + str(e))

    # search ebay for item
    if image_count < config.max_images_per_item:
        image_urls = search_ebay_for_item(item, set, config.max_ebay_search_images)
        for image_url in image_urls:
            try: 
                saved_to_file = save_image_to_file(filesystem_manager, image_url, item)

                if saved_to_file:
                    image_count += 1
            except Exception as e:
                print("failed to download " + str(image_url) + ". " + str(e))

    # supplement images with duckduckgo images top results
    if image_count < config.min_images_per_item:
        prompt = '\"' + set.name + '\"' + ' ' + item.name

        for image_url in get_image_urls_from_ddg(prompt, config.max_ddg_images):
            try: 
                saved_to_file = save_image_to_file(filesystem_manager, image_url, item)

                if saved_to_file:
                    image_count += 1
            except Exception as e:
                print("failed to download " + str(image_url) + ". " + str(e))


async def download_images_and_save(filesystem_manager: FilesystemManager, start_set: int=1):
    for set_id in range(start_set, get_set_count() + 1):
        set = get_set_from_db(str(set_id))
        items = get_items_from_db(str(set_id))

        tasks = [asyncio.to_thread(download_item_images_and_save, filesystem_manager, item, set) for item in items]

        with tqdm_async(total=len(tasks), desc='working on set: ' + str(set_id)) as progress_bar:
            for coro in asyncio.as_completed(tasks):
                try:
                    await coro
                except Exception as e:
                    print(f"error downloading images for item: {e}")
                progress_bar.update(1)

if __name__ == "__main__":
    log_file = open('output.log', 'w')
    sys.stdout = log_file
    filesystem_manager = FilesystemManager.get_implementation()
    filesystem_manager.create_dir(config.staging_dir)
    filesystem_manager.create_dir(config.training_dir)
    filesystem_manager.create_dir(config.val_dir)
    asyncio.run(download_images_and_save(filesystem_manager, 1))

