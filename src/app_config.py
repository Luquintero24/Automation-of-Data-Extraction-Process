import os

from dotenv import load_dotenv

load_dotenv()

api_base_url = os.getenv('API_BASE_URL')
api_token = os.getenv('API_TOKEN')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
aws_region = os.getenv('AWS_REGION')

final_count = os.getenv('COUNT')
