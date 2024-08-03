import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Float, inspect, Boolean, ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import random
import re

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
    combined_text = ''
    try:
        if textract_query:
            textract_data = json.loads(textract_query)
            response_status = textract_data.get('error_message')
            
            if not response_status:
                for block in textract_data.get('Blocks', []):
                    if block.get('BlockType') == 'LINE' and int(block.get('Confidence')) > 60:
                        extracted_text = block.get('Text', '')                     
                        combined_text = combined_text + extracted_text
    except Exception as e:
        print(f"Error processing textract_query: {e}")
    
    return clean_string(combined_text)  


# Define regular expressions and corresponding match groups for each cluster
regex_patterns = {
    0: (r'(PO|PC).*?(\d{10})', 2),   # Match 2nd group: 10-digit number
    1: (r'L\d{4}NXT', 0),            # Match entire pattern
    2: (r'NETWTPOUND.*?(\d{10})', 1),# Match 1st group: 10-digit number
    3: (r'(\d{10})JOBDETAILS|([A-Z]{3}BAK\d{3})|(CLR\d{10})|PO.{0,5}?(\d{10})', (1,2,3,4)),  # Match 1st group: 10-digit number
    4: (r'CLR(\d{10})', 0),          # Match entire pattern
    5: (r'CUSTOMERPONUMBER.*?(\d{10})', 1), # Match 10 digits number
    6: (r'PO.*?(\d{10})|(DC\d{7})', (1,2)),
    7: (r'PO.*?(\d{10})', 1),
    8: (r'PO.*?(C\d{5}-\d{4})', 1),
    9: (r'PO#?.*?(\d{10})', 1),
    10: (r'(\d{6})PRODUCT', 1),
    11: (r'PONUMBER.*?(\d{10})',1),
    12: (r'PO.*?(\d{10})', 1),
    13: (r'PO.*?(\d{10})|PO:.*?(\d{6})', (1,2)),
    14: (r'PO.*?(\d{10})|CLR(\d{10})', (1,2)),
    15: (r'([A-Z]{3}BAK\d{3})|([A_Z]{3}\d{10})|PO.{0,5}?(\d{10})|CUSTOMERPO#.*?(\d{10})|PURCHASEORDER:.*?(\d{6})', (1,2,3,4,5)),
    16: (r'PO.*?(\d{10})', 1),
    17: (r'PO.*?(\d{10})', 1),
    18: (r'PO.*?(\d{10})', 1),
    19: (r'PO#.*?(\d{10})SERVICE', 1),
    20: (r'PO.*?(\d{10})', 1),
    21: (r'PO.*?(\d{10})', 1),
    22: (r'PO#.*?(\d{5})', 1),
    23: (r'PO.*?(\d{10})', 1),
    24: (r'PONO.*?(CLR\d{10})', 1), 
    25: (r'PO:.*?(\d{10})', 1),
    26: (r'PO.*?(\d{10})', 1),
    27: (r'(CLR\d{10})|A\d{6}-\d{1}-\d{2}.*?(\d{10})',(1,2)),
    28: (r'(CLR\d{10})|PO.*?:.*?(\d{10})', (1,2)), 
    29: (r'L\d{4}NXT', 0), 
    30: (r'PONUMBER.*?(\d{10})', 1),
    31: (r'PO.*?(\d{10})', 1),
    32: (r'PO.*?(\d{10})', 1),
    33: (r'CUSTOMERPO.*?(\d{6})', 1),
    34: (r'CLR(\d{10})', 0),
    35: (r'PURCHASEORDER.*?(\d{10})', 1),
    36: (r'PO.*?(\d{10})', 1),
    37: (r'(PO|PC).*?(\d{10})', 2),
    38: (r'NUMBER.*?(\d{10})',1),
    39: (r'PONO.*?([A-Z]{3}\d{10})', 1),
    40: (r'PO.*?(\d{10})', 1),
    41: (r'(CLR\d{10})|(L\d{4}NXT)|([A-Z]{3}-[A-Z]{3}\d{10})', (1,2,3)),
    42: (r'PURCHASEORDER.*?(\d{10})', 1),
    43: (r'PO:.*?(\d{6})', 1),
    44: (r'PO.*?(\d{10})', 1),
    45: (r'PO:.*?(\d{6})', 1),
    46: (r'PO#.*?(\d{10})HAUL', 1),
    47: (r'PO:.*?(\d{10})', 1),
    48: (r'PO.*?(\d{10})', 1),
    49: (r'([A-Z]{3}BAK\d{3})|(CLR[A-Z]{3}\d{3})', (1,2)),
}

def search_PO(text, cluster):
    # Get the regex pattern and match groups for the specified cluster
    pattern_info = regex_patterns.get(cluster)
    
    if pattern_info:
        pattern, match_groups = pattern_info
        # Search for the pattern in the text
        match = re.search(pattern, text)
        if match:
            if isinstance(match_groups, tuple):
                # If match_groups is a tuple, iterate through the specified groups
                for group in match_groups:
                    group_match = match.group(group)
                    if group_match:  # If the group match is not empty, return it
                        return group_match
            else:
                # If match_groups is not a tuple, return the specific group
                return match.group(match_groups)
    return 'Manual Entry Flag'



total = 500
correct = 0

for i in range(0,50):
    print("Cluster: ",i)
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
                print(id + " : " + PO + " - " + str(actual_po[0][0]))
                if PO == str(clean_string(actual_po[0][0])) or PO == 'Manual Entry Flag':
                    correct +=1

accuracy = correct/total
print('Accuracy: ', accuracy)

                



            
                                                    
                                                                    
                                                                        
            
