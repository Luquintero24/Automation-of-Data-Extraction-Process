import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Float, inspect, Boolean, ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import random

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

# Define the TR table model
class TR(Base):
    __tablename__ = 'TR'
    id = Column(String, primary_key=True)
    image_processing_status = Column(Boolean, default=False)
    error_message = Column(Text, default=None)
    textract_response = Column(Text)

class TEMPLATES(Base):
    __tablename__ = 'TEMPLATES'
    cluster = Column(Text, primary_key=True)
    id_array = Column(ARRAY(String))

class BOL(Base):
    __tablename__ = 'BOL'
    id = Column(Text, primary_key=True)
    ticket_num = Column(Text)
    purchase_order = Column(Text)
    weight = Column(Integer)
    sand_type = Column(Text)
    end_timestamp = Column(DateTime)
    db_insert_date = Column(DateTime)
    image_upload_status = Column(Text)
    response = Column(Text)

def clean_string(text):
    text = text.replace(" ","")
    text = text.upper()
    text = text.replace(".", "").replace(",","")


    return text

def get_string(textract_query):
    combined_text = []
    try:
        if textract_query:
            textract_data = json.loads(textract_query)
            response_status = textract_data.get('error_message')
            
            if not response_status:
                for block in textract_data.get('Blocks', []):
                    if block.get('BlockType') == 'LINE' and int(block.get('Confidence')) > 70:
                        extracted_text = block.get('Text', '')                     
                        combined_text.append(clean_string(extracted_text))
    except Exception as e:
        print(f"Error processing textract_query: {e}")
    
    return combined_text  

def search_PO(lines, cluster):
    for i in range(len(lines)):
        if cluster == 0:
            if 'PO#:' in lines[i] or 'PC#:' in lines[i]:
                return lines[i][4:]
            if "PO" in lines[i] or "PC" in lines[i]:
                return lines[i][3:]
        elif cluster == 1:
            if 'PO:' in lines[i]:
                return lines[i+1]
        elif cluster == 2:
            if 'NETWTPOUND' in lines[i]:
                 if len(lines[i+1]) == 10: return lines[i+1]
        elif cluster == 3:
            if 'NUMBER' in lines[i]:
                return lines[i][6:]
        elif cluster == 4:
            if 'PONO:' in lines[i]:
                return lines[i+1]
    return 'Manuel Entry Flag'




for i in range(0,5):
    id_array_query = session.query(TEMPLATES.id_array).filter(TEMPLATES.cluster == str(i)).all()
    id_arrays = [result.id_array for result in id_array_query]

    for id_array in id_arrays:
        random_sample = random.sample(id_array, min(len(id_array), 10)) 
        for id in random_sample:
            textract_query = session.query(TR.textract_response).filter(TR.id == str(id)).all()
            actual_po = session.query(BOL.purchase_order).filter(BOL.id == str(id)).all()
            if textract_query:
                textract_response = textract_query[0].textract_response
                combined_text = get_string(textract_response)
                PO = search_PO(combined_text, i)
                if actual_po is None : actual_po = 'Null'
                print(id + " : " + PO + " - " + str(actual_po[0]))
                



            
                                                    
                                                                    
                                                                        
            
