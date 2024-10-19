import boto3

S3_BUCKET = "your-bucket-name"
s3 = boto3.client('s3')

def upload_file_to_s3(file, filename):
    try:
        s3.upload_fileobj(file, S3_BUCKET, filename)
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
