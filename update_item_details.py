#!/usr/bin/env python3

from request_manager import *
from database_manager import *
from tqdm.asyncio import tqdm as tqdm_async
import threading
import asyncio

async def update_sets_and_items():
    sets = get_all_sets()

    for set in sets:
        insert_set(set)

    tasks = [asyncio.to_thread(get_items_from_set, set) for set in sets]

    with tqdm_async(total=len(tasks)) as progress_bar:
        for coro in asyncio.as_completed(tasks):
            items = await coro
            insert_items(items)
            progress_bar.update(1)

async def update_item_details_into_db():
    tasks = [asyncio.to_thread(get_item_details_from_item, item) for item in get_items_from_db()]

    items_details = []
    lock = threading.Lock()

    with tqdm_async(total=len(tasks)) as progress_bar:
        for coro in asyncio.as_completed(tasks):
            item_detail = await coro
            with lock:
                items_details.append(item_detail)
            progress_bar.update(1)

    insert_item_details(items_details)

if __name__ == "__main__":
    asyncio.run(update_sets_and_items())
    asyncio.run(update_item_details_into_db())