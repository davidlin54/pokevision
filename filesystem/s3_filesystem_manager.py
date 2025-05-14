from botocore.exceptions import NoCredentialsError
from item import Item
from filesystem_manager import FilesystemManager
import boto3
import dotenv
import os

class S3FilesystemManager(FilesystemManager):
    dotenv.load_dotenv()
    bucket_name = os.getenv('s3_bucket_name')
    
    @staticmethod
    def create_dir_for_item(item: Item):
        s3_client = boto3.client('s3')
        folder_path = str(item.id)
        try:
            # The folder is created by uploading an empty object with the folder path
            s3_client.put_object(Bucket=S3FilesystemManager.bucket_name, Key=folder_path)
        except NoCredentialsError:
            print("AWS credentials not found.")
        except Exception as e:
            print(f"Error creating directory in S3: {str(e)}")

    @staticmethod
    def get_dir_for_item(item: Item) -> str:
        return str(item.id) + '/'

    @staticmethod
    def save_image_to_file(content: bytes, file_name: str):
        s3_client = boto3.client('s3')
        try:
            s3_client.put_object(Bucket=S3FilesystemManager.bucket_name, Key=file_name, Body=content)
        except NoCredentialsError:
            print("AWS credentials not found.")
        except Exception as e:
            print(f"Error saving file to S3: {str(e)}")

    @staticmethod
    def file_exists(file_name: str) -> bool:
        s3_client = boto3.client('s3')
        try:
            s3_client.head_object(Bucket=S3FilesystemManager.bucket_name, Key=file_name)
            return True
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False
            else:
                return False