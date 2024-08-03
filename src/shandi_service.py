import json
import requests
import src.app_config as config


def get_orders_api(latest_date, page):
    endpoint = '/orders'
    url = f"{config.api_base_url}{endpoint}"
    params = {'endedSince': latest_date, 'pageLimit': '5', 'product': 'sandi', 'logisticsStatus': 'completed', 'page': page}
    headers = {'Authorization': f'Bearer {config.api_token}'}

    # Fetch data from API
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()
    # if response.status_code != 200:
    #     print(f"Failed to fetch data. Status code: {response.status_code}")
    #     print(response.json())
    #     exit()


def get_orders(latest_date):
    page = 1
    results = get_orders_api(latest_date, page)
    while len(results) > 0:
        yield results

        page += 1
        results = get_orders_api(latest_date, page)


        # JSON endpoint to fetch data

        # Parse JSON response
        # data = response.json()
        # json_string = json.dumps(data, indent=4)
        # print(/json_string)
