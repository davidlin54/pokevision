from request_manager import *
from database_manager import *
from tqdm.asyncio import tqdm as tqdm_async
import asyncio

async def setup_database():
    drop_all()
    create_db()
    create_set_table()
    create_item_table()
    create_item_details_table()
    sets = get_all_sets()

    for set in sets:
        insert_set(set)

    tasks = [asyncio.to_thread(get_items_from_set, set) for set in sets]

    with tqdm_async(total=len(tasks)) as progress_bar:
        for coro in asyncio.as_completed(tasks):
            items = await coro
            insert_items(items)
            progress_bar.update(1)

if __name__ == "__main__":
    asyncio.run(setup_database())