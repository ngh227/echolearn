# app/services/s3_service.py
import boto3
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self):
        self.s3 = boto3.client('s3')
        transcribe_client = boto3.client('transcribe')
        self.bucket_name = 'echolearn-bucket'

    def upload_file(self, file_name, object_name=None):
        if object_name is None:
            object_name = file_name

        try:
            self.s3.upload_file(file_name, self.bucket_name, object_name)
        except ClientError as e:
            print(e)
            return False
        return True

    def generate_presigned_url(self, object_name, expiration=3600):
        try:
            response = self.s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': self.bucket_name,
                                                              'Key': object_name},
                                                      ExpiresIn=expiration)
        except ClientError as e:
            print(e)
            return None
        return response