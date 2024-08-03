from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from src.db.textract_response import textract_responses




class TextractProcessor():
    def __init__(self, db, s3_client, textract_client):
        self.s3_client = s3_client
        self.textract_client = textract_client
        self.db = db

    def process_bucket(self, bucket_name):
        try:
            # # Initialize S3 client
            # s3_client = boto3.client(
            #     's3',
            #     aws_access_key_id=AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            #     region_name=AWS_REGION
            # )

            # List objects in the bucket
            # response = self.s3_client.fetch_bucket_content(bucket_name)
            # print(response)

            # Process each object in the bucket
            for obj in self.s3_client.fetch_bucket_content(bucket_name):
                textract = textract_responses()
                document_name = obj['Key']
                print(f"Processing document: {document_name}")
                try:
                    textract_response = None
    
                    textract_response = self.textract_client.analyze_document(bucket_name, document_name)

                    # Save the response to the database
                    if textract_response is not None:
                        textract.from_textract_response(document_name, textract_response)
                        textract.save_textract_response_to_db(self.db.session, document_name)
                except Exception as error_message:
                        textract.from_textract_response(document_name, textract_response, str(error_message))
                        textract.save_textract_response_to_db(self.db.session, document_name)

            self.db.session.commit()
        except NoCredentialsError:
            print("Error: No AWS credentials found.")
        except PartialCredentialsError:
            print("Error: Incomplete AWS credentials provided.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
