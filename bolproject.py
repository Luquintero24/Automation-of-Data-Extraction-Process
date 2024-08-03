# import os
# import psycopg2
# import requests
# from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, inspect, desc
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from dotenv import load_dotenv
# from datetime import datetime, timezone
# import json
# from io import BytesIO
# import boto3
# from botocore.exceptions import NoCredentialsError
#
# from src.db.bol import BOL
# from src.db.db_connection import session, engine, Base
# from src.shandi_service import get_orders
#
# inspector = inspect(engine)
# if not inspector.has_table('BOL'):
#     Base.metadata.create_all(engine)
#
# for page in get_orders(BOL.latest_date(session)):
#     for order in page:
#         bol = BOL()
#         bol.from_json(order)
#         bol.upload_image_to_bucket()
#         bol.save(session)
#     session.commit()
#
#
#
#     counter += len(data)
#     print("Data successfully inserted into BOL table, entries - " + str(len(data)) + " | page - " + str(page) + " | total - " + str(counter))
#     page += 1
#
# print("Execution Complete")


