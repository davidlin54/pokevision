import config
import os
import shutil
import random
from pathlib import Path
from item import Item
from filesystem_manager import FilesystemManager
from tqdm import tqdm

class LocalFilesystemManager(FilesystemManager):
    @staticmethod
    def create_dir(path: str):
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod   
    def create_dirs_for_item(item: Item):
        item_relative_path = '/' + str(item.id)
        LocalFilesystemManager.create_dir(config.staging_dir + item_relative_path)
        LocalFilesystemManager.create_dir(config.training_dir + item_relative_path)
        LocalFilesystemManager.create_dir(config.val_dir + item_relative_path)

    @staticmethod   
    def get_dir_for_item(directory: str, item: Item) -> str:
        return directory + '/' + str(item.id) + '/'

    @staticmethod
    def save_image_to_file(content: bytes, file_name: str):
        with open(file_name, "wb") as f:
            f.write(content)

    @staticmethod
    def file_exists(file_name: str):
        file_path = Path(file_name)
        return file_path.exists()

    @staticmethod
    def get_num_images_for_item(item: Item) -> int:
        item_relative_path = '/' + str(item.id)

        staging_path = Path(config.staging_dir + item_relative_path)
        training_path = Path(config.training_dir + item_relative_path)
        val_path = Path(config.val_dir + item_relative_path)

        images_count = sum(1 for p in staging_path.iterdir() if p.is_file()) + sum(1 for p in training_path.iterdir() if p.is_file()) + sum(1 for p in val_path.iterdir() if p.is_file())

        return images_count

    @staticmethod
    def split_dataset(staging_dir: str, training_dir: str, val_dir: str, val_ratio: float):
        staging_path = Path(staging_dir)
        training_path = Path(training_dir)
        val_path = Path(val_dir)

        class_dirs = [d for d in staging_path.iterdir() if d.is_dir()]

        for class_dir in tqdm(class_dirs, desc="classes"):
            files = list(class_dir.glob("*"))
            random.shuffle(files)

            split_idx = int(len(files) * val_ratio)

            val_files = files[:split_idx]
            train_files = files[split_idx:]

            train_class_dir = training_path / class_dir.name
            val_class_dir = val_path / class_dir.name
            train_class_dir.mkdir(parents=True, exist_ok=True)
            val_class_dir.mkdir(parents=True, exist_ok=True)

            # Copy files
            for f in train_files:
                shutil.copy(f, train_class_dir / f.name)
            for f in val_files:
                shutil.copy(f, val_class_dir / f.name)

        # After copying, remove the files and folders under source_dir
        class_dirs = [d for d in staging_path.iterdir() if d.is_dir()]
        for class_dir in tqdm(class_dirs, desc="deleting classes"):
            if class_dir.is_dir():
                shutil.rmtree(class_dir)
            else:
                class_dir.unlink()