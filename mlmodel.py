import boto3
import numpy as np
from scipy.linalg import svd
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import cosine_similarity
import cv2
import os
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration for AWS S3
class Config:
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')
    aws_region = os.getenv('AWS_REGION')

config = Config()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region_name=config.aws_region
)

def list_image_keys(bucket_name, max_keys):
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name)
    
    image_keys = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                if len(image_keys) < max_keys:
                    image_keys.append(obj['Key'])
                else:
                    return image_keys
    return image_keys

def download_images_from_s3(bucket_name, image_keys, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    local_image_paths = []
    for key in image_keys:
        local_path = os.path.join(download_dir, os.path.basename(key))
        try:
            s3_client.download_file(bucket_name, key, local_path)
            # Check if the file is a valid image
            with Image.open(local_path) as img:
                img.verify()  # Verify the image is valid
            local_image_paths.append(local_path)
        except Exception as e:
            print(f"Error downloading or verifying image {key}: {e}")
    
    return local_image_paths

# Preprocess image
def preprocess_image(image_path):
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (300, 300))  # Resize to a standard size
        image = cv2.equalizeHist(image)  # Normalize lighting conditions
        return image
    except Exception as e:
        print(f"Error preprocessing image {image_path}: {e}")
        return None

def compute_svd(image):
    U, S, Vt = svd(image, full_matrices=False)
    return S

def cosine_sim(matrix1, matrix2):
    return cosine_similarity([matrix1], [matrix2])[0][0]

def extract_text_lines(image_path):
    text = pytesseract.image_to_string(cv2.imread(image_path))
    lines = text.split('\n')
    return lines[:5], lines[-5:]  # Top-n and bottom-n lines

def fuzzy_match(text1, text2):
    return fuzz.ratio(text1, text2) / 100.0

def compute_combined_similarity(input_image_path, template_image_path, text_threshold):
    # Preprocess images
    input_image = preprocess_image(input_image_path)
    template_image = preprocess_image(template_image_path)
    
    # Compute SVD
    S_input = compute_svd(input_image)
    S_template = compute_svd(template_image)
    
    # Visual similarity
    sim_visual = cosine_sim(S_input, S_template)
    
    # Text similarity
    input_top, input_bottom = extract_text_lines(input_image_path)
    template_top, template_bottom = extract_text_lines(template_image_path)
    input_text = ' '.join(input_top + input_bottom)
    template_text = ' '.join(template_top + template_bottom)
    sim_text = fuzzy_match(input_text, template_text)
    
    # Combined similarity
    sim_combined = sim_visual + sim_text
    
    return sim_combined, sim_text

def find_best_template(input_image_path, template_paths, text_threshold=0.5):
    best_similarity = -1
    best_template = None
    
    for template_image_path in template_paths:
        sim_combined, sim_text = compute_combined_similarity(input_image_path, template_image_path, text_threshold)
        
        if sim_text >= text_threshold and sim_combined > best_similarity:
            best_similarity = sim_combined
            best_template = template_image_path
    
    return best_template if best_template else "Manual annotation required"

# Define S3 bucket
bucket_name = 'sandi-bols'

# List and download images from S3
image_keys = list_image_keys(bucket_name, max_keys=100)
image_paths = download_images_from_s3(bucket_name, image_keys, 'images')

# Use the first N images as templates
num_templates = 10
template_paths = image_paths[:num_templates]

# Compare each image against the templates
for image_path in image_paths[num_templates:]:
    best_template = find_best_template(image_path, template_paths)
    print(f"Best template for {os.path.basename(image_path)}: {os.path.basename(best_template)}")
