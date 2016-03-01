import requests
import secret


def item_search(item):
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'query': item
    }
    response = requests.get('https://api.walmartlabs.com/v1/search', params=query)
    parsed = response.json()
    return parsed.get('items',{})


def upc_search(upc):
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'upc': upc
    }
    response = requests.get('https://api.walmartlabs.com/v1/items', params=query)
    parsed = response.json()
    return parsed.get('items',{})

