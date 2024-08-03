import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Float, inspect, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables
load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL')
API_TOKEN = os.getenv('API_TOKEN')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Create database connection
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Define base for ORM
Base = declarative_base()

class FEATURES_PO(Base):
    __tablename__ = 'FEATURES_PO'
    id = Column(Text, primary_key=True)
    error_message = Column(Text, default=None)
    width = Column(Float)
    height = Column(Float)
    left = Column(Float)
    top = Column(Float)
    block_number = Column(Integer, default=None)
    vendor = Column(Text, default=None)


features = session.query(FEATURES_PO).order_by(FEATURES_PO.id).all()
vendor_names = [r.vendor for r in features]

vendors = []
for r in vendor_names:
    if r not in vendors:
        vendors.append(r)

vendors = list(set(vendors))
print(vendors)
print(len(vendors))




