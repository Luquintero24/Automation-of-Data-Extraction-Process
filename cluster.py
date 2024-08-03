import pandas as pd
from sqlalchemy import create_engine, Column, Text, Float, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load environment variables
load_dotenv()

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

# Extract data from database
def extract_data():
    try:
        features = session.query(FEATURES_PO).order_by(FEATURES_PO.id).all()
        data = []
        for feature in features:
            data.append({
                'id': feature.id,
                
                'vendor': feature.vendor
            })
        df = pd.DataFrame(data)
        # Drop rows with any NaN values
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"Error extracting data: {e}")
        return pd.DataFrame()

# Step 2: Preprocess the Data
def preprocess_data(df):
    # Normalize the features (width, height, top, left)
    # scaler = StandardScaler()
    # df[['width', 'height', 'top', 'left']] = scaler.fit_transform(df[['width', 'height', 'top', 'left']])
    
    # Convert vendor to numerical values
    df['vendor'] = df['vendor'].astype('category').cat.codes
    
    return df

# Step 3: Implement KMeans Clustering and Step 4: Determine the Optimal Number of Clusters using Elbow Method
def kmeans_elbow_method(df):
    features = df[[ 'vendor']]
    
    # Elbow method to find the optimal number of clusters
    sse = []
    k_range = range(1, 20)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=0).fit(features)
        sse.append(kmeans.inertia_)
    
    # Plot the elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, sse, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('SSE')
    plt.title('Elbow Method For Optimal k')
    plt.show()

# Step 5: Visualize and Analyze the Clusters
def visualize_clusters(df, n_clusters):
    features = df[['vendor']]
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(features)
    df['cluster'] = kmeans.labels_
    
    # Visualize the clusters
    # plt.figure(figsize=(10, 6))
    # plt.scatter(df['width'], df['height'], c=df['cluster'], cmap='viridis')
    # plt.xlabel('Width')
    # plt.ylabel('Height')
    # plt.title('Clusters Visualization')
    # plt.show()
    
    return df

# Main Function to Execute All Steps
def main():
    df = extract_data()
    if not df.empty:
        df = preprocess_data(df)
        kmeans_elbow_method(df)
        
        # Based on the elbow method, set the optimal number of clusters (e.g., 41)
        optimal_clusters = 41
        df = visualize_clusters(df, optimal_clusters)
        
         # Create and print dictionary of IDs and clusters
        id_cluster_dict = df.set_index('id')['cluster'].to_dict()
        print(id_cluster_dict)

        result = {}

        # Iterate through the data
        for key, value in id_cluster_dict.items():
            # If the class (value) is not in the result dictionary, add it with an empty list
            if value not in result:
                result[value] = []
            # Append the ID (key) to the list of the corresponding class (value)
            result[value].append(key)

        # Print the result in the desired format
        for key in sorted(result.keys()):
            print('-------------------------------------')
            print(f"---{key}---: {', '.join(result[key])}")

    else:
        print("No data to process.")

# Run the main function
if __name__ == "__main__":
    main()
