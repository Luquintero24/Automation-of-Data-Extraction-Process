import boto3
from botocore.exceptions import NoCredentialsError
import src.app_config as config
from datetime import datetime, timezone



class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region
        )

    def upload_to_s3(self, data, bucket, object_name):
        try:
            self.s3_client.upload_fileobj(data, bucket, object_name)
            print(f"Data uploaded to {bucket}/{object_name}")
            return "True"
        except NoCredentialsError:
            print("Credentials not available")
            return "False"
        

    # def fetch_bucket_content(self, bucket_name):
    #     try:
    #        return self.s3_client.list_objects_v2(Bucket = bucket_name)
    #     except NoCredentialsError:
    #         print("Credentials not available")
    #         return "False"
        
    def fetch_bucket_content(self, bucket_name):
       
        today = datetime.now(timezone.utc).date()
        
        # List objects in the bucket with pagination support
        response = self.s3_client.list_objects_v2(Bucket=bucket_name)
        
        while response:
            # Iterate over the objects in the current response
            for obj in response.get('Contents', []):
                if obj['LastModified'].date() == today:
                    yield obj
            
            # Check if more objects are available (pagination)
            if response.get('IsTruncated'):
                response = self.s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=response.get('NextContinuationToken')
                )
            else:
                break