import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import src.app_config as config


class TextractClient:
    def __init__(self):
        # Initialize Textract client
        self.textract_client = boto3.client(
            'textract',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region
        )

    def analyze_document(self, bucket_name, document_name):
            # Call Textract to analyze the document
            response = self.textract_client.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': document_name
                    }
                },
                FeatureTypes=["TABLES", "FORMS"]
            )

            return response

