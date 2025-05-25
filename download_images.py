#!/usr/bin/env python3

from request_manager import *
from database_manager import *
from filesystem_manager import *
from tqdm.asyncio import tqdm as tqdm_async
from tqdm import tqdm as tqdm
import asyncio
import config

def save_image_to_file(filesystem_manager: FilesystemManager, content: bytes, file_name: str, item: Item) -> bool:
    staging_file_path = filesystem_manager.get_dir_for_item(config.staging_dir, item) + file_name
    training_file_path = filesystem_manager.get_dir_for_item(config.training_dir, item) + file_name
    val_file_path = filesystem_manager.get_dir_for_item(config.val_dir, item) + file_name

    if not filesystem_manager.file_exists(staging_file_path) and not filesystem_manager.file_exists(training_file_path) and not filesystem_manager.file_exists(val_file_path):
        filesystem_manager.save_image_to_file(content, staging_file_path)
        return True

    return False

def download_item_images_and_save(filesystem_manager: FilesystemManager, item: Item, set: Set):
    filesystem_manager.create_dirs_for_item(item)
    image_count = filesystem_manager.get_num_images_for_item(item)

    if (image_count > config.max_images_per_item):
        return

    pc_image_urls = get_image_urls_from_item(item)

    for image_url in pc_image_urls:
        try:
            content = fetch_image_from_url(image_url)

            pc_image_id = image_url.split('/')[-2]
            extension = image_url.split('.')[-1]

            file_name = pc_image_id + '.' + extension
            saved_to_file = save_image_to_file(filesystem_manager, content, file_name, item)

            if saved_to_file:
                image_count += 1
        except Exception as e:
            print("failed to download " + str(image_url) + ". " + str(e))

    for url in get_ebay_links_from_item(item):
        try:
            image_url = get_image_url_from_ebay(url)

            if image_url:
                content = fetch_image_from_url(image_url)

                ebay_id = url.split('/')[-1]
                extension = image_url.split('.')[-1]

                file_name = ebay_id + '.' + extension
                saved_to_file = save_image_to_file(filesystem_manager, content, file_name, item)

                if saved_to_file:
                    image_count += 1
        except Exception as e:
            print("failed to download " + str(image_url) + ". " + str(e))

    # supplement images with duckduckgo images top results
    # if image_count < config.max_images_per_item:
    #     prompt = '\"' + set.name + '\"' + ' ' + item.name

    #     for image_url in get_image_urls_from_ddg(prompt, config.max_images_per_item - image_count):
    #         try: 
    #             content = fetch_image_from_url(image_url)

    #             image_name = str(hash(image_url))
    #             extension = image_url.split('.')[-1]

    #             file_name = image_name + '.' + extension
    #             saved_to_file = save_image_to_file(filesystem_manager, content, file_name, item)

    #             if saved_to_file:
    #                 image_count += 1
    #         except Exception as e:
    #             print("failed to download " + str(image_url) + ". " + str(e))


async def download_images_and_save(filesystem_manager: FilesystemManager, start_set: int=1):
    for set in range(start_set, get_set_count() + 1):
        items = get_items_from_db(set)

        tasks = [asyncio.to_thread(download_item_images_and_save, filesystem_manager, item, set) for item in items]

        print('working on set: ' + str(set))
        with tqdm_async(total=len(tasks)) as progress_bar:
            for coro in asyncio.as_completed(tasks):
                await coro
                progress_bar.update(1)

if __name__ == "__main__":
    # asyncio.run(download_images_and_save(FilesystemManager.get_implementation()))
    set = get_all_sets()[0]
    items = get_items_from_db(1)
    download_item_images_and_save(FilesystemManager.get_implementation(), items[0], set)

