from abc import ABC, abstractmethod
from item import Item
import importlib
import dotenv
import os

class FilesystemManager(ABC):
    @staticmethod
    @abstractmethod
    def create_dir(path: str):
        pass

    @staticmethod
    @abstractmethod
    def get_dir_for_item(item: Item) -> str:
        pass

    @staticmethod
    @abstractmethod
    def save_image_to_file(content: bytes, file_name: str):
        pass

    @staticmethod
    @abstractmethod
    def file_exists(file_name: str):
        pass

    @staticmethod
    def get_implementation():
        module_name = 'filesystem.local_filesystem_manager'
        class_name = 'LocalFilesystemManager'

        dotenv.load_dotenv()
        filesystem = os.getenv('filesystem')
        if filesystem == 'aws':
            module_name = 'filesystem.s3_filesystem_manager'
            class_name = 'S3FilesystemManager'

        try:
            # Dynamically import the module
            module = importlib.import_module(module_name)
            
            # Get the class from the module
            implementation_class = getattr(module, class_name)
            
            # Return class
            return implementation_class
        except ModuleNotFoundError:
            print(f"Error: Module '{module_name}' not found.")
        except AttributeError:
            print(f"Error: Class '{class_name}' not found in module '{module_name}'.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")