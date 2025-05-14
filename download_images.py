#!/usr/bin/env python3

from request_manager import *
from database_manager import *
from filesystem_manager import *
from tqdm.asyncio import tqdm as tqdm_async
from tqdm import tqdm as tqdm
import asyncio

def download_item_images_and_save(filesystem_manager: FilesystemManager, item: Item):
    pc_image_urls = get_image_urls_from_item(item)

    for image_url in pc_image_urls:
        try:
            content = fetch_image_from_url(image_url)

            pc_image_id = image_url.split('/')[-2]
            extension = image_url.split('.')[-1]

            file_path = filesystem_manager.get_dir_for_item(item) + pc_image_id + '.' + extension

            if not filesystem_manager.file_exists(file_path):
                filesystem_manager.save_image_to_file(content, file_path)
        except:
            print("failed to download " + str(image_url) + ". " + e)

    for url in get_ebay_links_from_item(item):
        try:
            image_url = get_image_url_from_ebay(url)

            if image_url:
                content = fetch_image_from_url(image_url)

                ebay_id = url.split('/')[-1]
                extension = image_url.split('.')[-1]

                file_path = filesystem_manager.get_dir_for_item(item) + ebay_id + '.' + extension
                
                if not filesystem_manager.file_exists(file_path):
                    filesystem_manager.save_image_to_file(content, file_path)
        except Excecption as e:
            print("failed to download " + str(image_url) + ". " + e)


async def download_images_and_save(filesystem_manager: FilesystemManager, start_set: int=1):
    for set in range(start_set, get_set_count() + 1):
        items = get_items_from_db(set)

        tasks = [asyncio.to_thread(download_item_images_and_save, filesystem_manager, item) for item in items]

        print('working on set: ' + str(set))
        with tqdm_async(total=len(tasks)) as progress_bar:
            for coro in asyncio.as_completed(tasks):
                await coro
                progress_bar.update(1)

if __name__ == "__main__":
    asyncio.run(download_images_and_save(FilesystemManager.get_implementation()))

