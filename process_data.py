import config
import os
import shutil
import random
from filesystem.local_filesystem_manager import LocalFilesystemManager

def create_directories():
    LocalFilesystemManager.create_dir(config.staging_dir)
    LocalFilesystemManager.create_dir(config.training_dir)
    LocalFilesystemManager.create_dir(config.val_dir)

def download_new_images_from_s3():


if __name__ == "__main__":
    create_directories()
    download_new_images_from_s3()
    LocalFilesystemManager.split_dataset(config.staging_dir, config.training_dir, config.val_dir, 0.05)

