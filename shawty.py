import pandas as pd
from sqlalchemy import create_engine, Column, Text, Boolean, String, ARRAY, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import boto3
from PIL import Image
import io
import time
import joblib

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = 'sandi-bols'

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

    def get_data(self, id_array, cluster=None):
        if cluster:
            self.cluster = cluster
        if id_array:
            self.id_array = id_array

    def save_data(self, session):
        session.add(self)
        session.commit()

inspector = inspect(engine)
if not inspector.has_table('TEMPLATES'):
    Base.metadata.create_all(engine)

def extract_data():
    try:
        lines = session.query(TR).order_by(TR.id).all()
        data = []
        for line in lines:
            text = []
            textract_response = line.textract_response
            response_status = line.error_message
            if not response_status:
                textract_data = json.loads(textract_response)
                for block in textract_data.get('Blocks', []):
                    if block.get('BlockType') == 'LINE':
                        extracted_text = block.get('Text')
                        text.append(extracted_text)
                data.append({
                    'id': line.id,
                    'text': ' '.join(text),  # Join text lines into a single string
                })
        df = pd.DataFrame(data)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"Error extracting data: {e}")
        return pd.DataFrame()

# Extract data
df = extract_data()

# Text Preprocessing
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['text'])

# Elbow method to determine the optimal number of clusters
def find_optimal_clusters(data, max_k):
    iters = range(2, max_k+1, 2)
    sse = []
    for k in iters:
        sse.append(KMeans(n_clusters=k, init='k-means++', random_state=42).fit(data).inertia_)
        print(f'Fit {k} clusters')

    f, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Count')
    plt.show()

find_optimal_clusters(tfidf_matrix, 10)

# Perform KMeans clustering with the optimal number of clusters
optimal_clusters = 50  # Replace with the number determined by the elbow method
kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', random_state=42)
kmeans.fit(tfidf_matrix)
df['cluster'] = kmeans.labels_

# Save the trained KMeans model to a file
model_filename = 'kmeans_model.pkl'
joblib.dump(kmeans, model_filename)

# Save the TF-IDF vectorizer to a file
vectorizer_filename = 'tfidf_vectorizer.pkl'
joblib.dump(tfidf_vectorizer, vectorizer_filename)

# Set up AWS S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Print and display images for each cluster
for cluster in range(optimal_clusters):
    cluster_data = df[df['cluster'] == cluster]
    id_array = []
    for index, row in cluster_data.iterrows():
        id_array.append(row['id'])
        
    cluster_col = TEMPLATES()
    cluster_col.get_data(id_array=id_array, cluster=str(cluster))
    cluster_col.save_data(session)

# Load the saved KMeans model
kmeans = joblib.load(model_filename)

# Load the saved TF-IDF vectorizer
tfidf_vectorizer = joblib.load(vectorizer_filename)

# Function to make predictions on new data
def predict_cluster(new_text):
    # Transform the new text data using the loaded TF-IDF vectorizer
    new_text_tfidf = tfidf_vectorizer.transform([new_text])
    
    # Predict the cluster for the new text data
    cluster = kmeans.predict(new_text_tfidf)
    
    return cluster[0]

# # Example usage
# new_text = "Your input text here"
# predicted_cluster = predict_cluster(new_text)
# print(f"The predicted cluster for the input text is: {predicted_cluster}")
