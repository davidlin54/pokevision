from pathlib import Path
from item import Item
from filesystem_manager import FilesystemManager

training_prefix = "training/"

class LocalFilesystemManager(FilesystemManager):
    @staticmethod
    def create_dir_for_item(item: Item):
        Path(training_prefix + str(item.id)).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_dir_for_item(item: Item) -> str:
        return training_prefix + str(item.id) + '/'

    @staticmethod
    def save_image_to_file(content: bytes, file_name: str):
        with open(file_name, "wb") as f:
            f.write(content)

    @staticmethod
    def file_exists(file_name: str):
        file_path = Path(file_name)
        return file_path.exists()