import pandas as pd
from sqlalchemy import create_engine, Column, Text, Boolean, String, ARRAY
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import boto3
import time
import joblib
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

# Uncomment the following line if tables need to be created
# Base.metadata.create_all(engine)

# Load the saved KMeans model
model_filename = 'kmeans_model.pkl'
kmeans = joblib.load(model_filename)

# Load the saved TF-IDF vectorizer
vectorizer_filename = 'tfidf_vectorizer.pkl'
tfidf_vectorizer = joblib.load(vectorizer_filename)

# Function to make predictions on new data
def predict_cluster(new_text):
    # Transform the new text data using the loaded TF-IDF vectorizer
    new_text_tfidf = tfidf_vectorizer.transform([new_text])
    
    # Predict the cluster for the new text data
    cluster = kmeans.predict(new_text_tfidf)
    
    return cluster[0]

# Example usage
# new_text = "Your input text here"
# predicted_cluster = predict_cluster(new_text)
# print(f"The predicted cluster for the input text is: {predicted_cluster}")

textract_query = session.query(TR).limit(100).all()
random_sample = random.sample(textract_query, min(len(textract_query), 10))

for r in random_sample:
    if r:
        textract_response = r.textract_response
        text = []

        id = r.id
        error = r.error_message
        if not error:
            textract_data = json.loads(textract_response)
            for block in textract_data.get('Blocks', []):
                if block.get('BlockType') == 'LINE':
                    extracted_text = block.get('Text')
                    text.append(extracted_text)
            text = ' '.join(text)
            predicted_cluster = predict_cluster(text)
            actual_cluster_array = session.query(TEMPLATES.id_array).filter(TEMPLATES.cluster == str(predicted_cluster)).all()
            actual_cluster_array = [item[0] for item in actual_cluster_array]  # Flatten the list
            if id in actual_cluster_array[0]:
                print(id + ' - ' + str(predicted_cluster) + ' - True')
            else:
                print(id + ' - ' + str(predicted_cluster) + ' - False')
