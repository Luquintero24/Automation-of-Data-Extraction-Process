import src.app_config as config
import requests
import json


class APIClient:
    def __init__(self):
        self.api_base_url = config.api_base_url
        self.api_token = config.api_token

    def fetch_data(self, endpoint, params):
        url = f"{self.api_base_url}{endpoint}"
        headers = {'Authorization': f'Bearer {self.api_token}'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(response.json())
            exit()
        return response.json()
