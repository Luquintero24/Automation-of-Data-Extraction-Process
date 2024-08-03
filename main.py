from src.db.db_connection import Database
from src.aws.s3_service import S3Client
from src.aws.textract_services import TextractClient
from src.api.api_client import APIClient
from src.data_processor.data_processor import BOLProcessor
from src.data_processor.textract_process import TextractProcessor


def main():
    db_bol = Database('BOL_test')
    s3_client = S3Client()
    api_client = APIClient()
    bol_processor = BOLProcessor(db_bol, s3_client, api_client)
    bol_processor.process()
    new_s3_client = S3Client()
    textract_client = TextractClient()
    db_bol.close_session()
    db_textract = Database('TR_test')
    textract_processor = TextractProcessor(db_textract, new_s3_client, textract_client)
    textract_processor.process_bucket('sandi-bols')
    


if __name__ == "__main__":
    main()
