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

# Define the TR table model
class TR(Base):
    __tablename__ = 'TR'
    id = Column(String, primary_key=True)
    image_processing_status = Column(Boolean, default=False)
    error_message = Column(Text, default=None)
    textract_response = Column(Text)


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

    def get_features(self, id, error, features, counter=None, vendor=None):
        self.id = id
        if features:
            self.width = features.get('Width')
            self.height = features.get('Height')
            self.left = features.get('Left')
            self.top = features.get('Top')
        if error: self.error_message = error 
        if counter: self.block_number = counter
        if vendor: self.vendor = vendor

    def save_features(self, session):
        session.add(self)
        session.commit()

def clean_text(text):
    text = text.replace("-", "").replace(".", "")

    text = text.replace(" ", "")

    text = text.upper()

    return text

def search_vendor(vendor):
    data = json.loads(vendor)
    vendor_name = data["vendor"]["name"]
    return vendor_name



def search_textract_response(id, keyword, row, vendor):
    if row:
        textract_response = row.textract_response
        response_status = row.error_message
        if not response_status:
            textract_data = json.loads(textract_response)
                # Extract the "Text" of the "BlockType": "LINE"
            flag = False
            counter = 0
            for block in textract_data.get('Blocks', []):               
                if block.get('BlockType') == 'LINE':
                    text = block.get('Text')    
                    text = clean_text(text)
                    counter = counter + 1
                    if keyword in text:
                        flag = True
                        features = block.get('Geometry').get('BoundingBox')
                        add_features = FEATURES_PO()
                        add_features.get_features(id, error=None, features=features, counter=counter, vendor= vendor)
                        session.add(add_features)
                        break            
            if not flag:#No match is found in the document
                add_features = FEATURES_PO()
                add_features.get_features(id,error="Match not found", features=None)
                add_features.save_features(session)
        else:
            print(f"textract_response is None for id {order.id}")
            print(f"Invalid JSON for id {order.id}")
            add_features = FEATURES_PO()
            add_features.get_features(id,error='tr does not exist', features=None)
            session.add(add_features)
    else:
        print("No rows found in the TR table.") 
    
inspector = inspect(engine)
if not inspector.has_table('FEATURES_PO'):
    Base.metadata.create_all(engine)

orders_query = session.query(BOL).order_by(BOL.id)

num_orders = orders_query.count()
for page in range(0, num_orders, 100):
    print(page)
    orders = orders_query.limit(100).offset(page).all()
    order_ids = [r.id for r in orders]
    trs = session.query(TR).where(TR.id.in_(order_ids)).all()

    for order in orders:
        tr = next(filter(lambda tr: tr.id == order.id, trs), None)
        if tr is not None:
            id = order.id
            keyword = order.purchase_order
            vendor = order.response
            vendor = search_vendor(vendor)
            if 'LOG-' in keyword:
                keyword = keyword.replace("LOG-", "")
            keyword= clean_text(keyword)
            search_textract_response(id, keyword, tr, vendor= vendor)
        
    session.commit()
