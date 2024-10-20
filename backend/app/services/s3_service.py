# app/services/s3_service.py
import boto3
from botocore.exceptions import ClientError
import os
import logging
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME=os.getenv("S3_BUCKET_NAME")

class S3Service:
    def __init__(self, bucket_name=S3_BUCKET_NAME, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1'):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.logger = logging.getLogger(__name__)

    def upload_file(self, file_path, object_name=None):
        """Upload a file to S3 bucket"""
        if object_name is None:
            object_name = file_path

        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            self.logger.info(f"File {file_path} uploaded successfully to {self.bucket_name}/{object_name}")
            return True
        except ClientError as e:
            self.logger.error(f"Error uploading file to S3: {e}")
            return False

    # def download_file(self, object_name, file_path):
    #     """Download a file from S3 bucket"""
    #     try:
    #         self.s3.download_file(self.bucket_name, object_name, file_path)
    #         self.logger.info(f"File {object_name} downloaded successfully to {file_path}")
    #         return True
    #     except ClientError as e:
    #         self.logger.error(f"Error downloading file from S3: {e}")
    #         return False
    def download_file(self, bucket_name, object_key, local_path):
        try:
            self.s3.download_file(bucket_name, object_key, local_path)
            self.logger.info(f"File {object_key} downloaded successfully from {bucket_name} to {local_path}")
            return True
        except ClientError as e:
            self.logger.error(f"Error downloading file from S3: {e}")
            return False

    def generate_presigned_url(self, object_name, expiration=3600, http_method='put'):
        """Generate a presigned URL for uploading or downloading an object"""
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod=f'{http_method}_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            self.logger.info(f"Presigned URL generated for {object_name}")
            return url
        except ClientError as e:
            self.logger.error(f"Error generating presigned URL: {e}")
            return None
        
    def delete_file(self, object_name):
        """Delete a file from S3 bucket"""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            self.logger.info(f"File {object_name} deleted successfully from {self.bucket_name}")
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting file from S3: {e}")
            return False
        
    def list_files(self, prefix=''):
        """List files in the S3 bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            self.logger.info(f"Listed {len(files)} files from {self.bucket_name}")
            return files
        except ClientError as e:
            self.logger.error(f"Error listing files from S3: {e}")
            return []
##### TESTING ######
import os

def test_s3_service_with_real_file(file_path="/Users/maeve/Documents/animal-data", file_name="USA-SMR-1-2023-AQUA.pdf"):
    # Initialize S3Service
    s3_service = S3Service()

    # Full path to the file
    full_file_path = os.path.join(file_path, file_name)

    # Ensure the file exists
    if not os.path.exists(full_file_path):
        print(f"Error: File {full_file_path} does not exist.")
        return

    try:
        # Test file upload
        object_name = file_name
        assert s3_service.upload_file(full_file_path, object_name), "File upload failed"
        print(f"File {file_name} uploaded successfully")

        # Test list files
        files = s3_service.list_files()
        assert object_name in files, f"Uploaded file {file_name} not found in bucket"
        print("File listing successful")

        # Test generate presigned URL
        presigned_url = s3_service.generate_presigned_url(object_name, http_method='get')
        assert presigned_url is not None, "Failed to generate presigned URL"
        print(f"Presigned URL generation successful for {file_name}")
        print(f"Presigned URL: {presigned_url}")

        # Test file download
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads', f'downloaded_{file_name}')
        assert s3_service.download_file(object_name, download_path), "File download failed"
        print(f"File {file_name} downloaded successfully to {download_path}")

        # Verify downloaded content
        with open(full_file_path, 'rb') as original_file, open(download_path, 'rb') as downloaded_file:
            assert original_file.read() == downloaded_file.read(), "Downloaded content does not match original file"
        print("Downloaded content verified")

        print("All S3 operations tested successfully!")
        print(f"The file {file_name} remains in your S3 bucket.")

    except AssertionError as e:
        print(f"Test failed: {str(e)}")
    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
    finally:
        # Clean up downloaded file
        if os.path.exists(download_path):
            os.unlink(download_path)
            print(f"Cleaned up downloaded file: {download_path}")

if __name__ == "__main__":
    # Specify the path and filename of your test file
    file_path = "/Users/maeve/Documents/animal-data"
    file_name = "USA-SMR-1-2023-AQUA.pdf"
    
    test_s3_service_with_real_file(file_path, file_name)