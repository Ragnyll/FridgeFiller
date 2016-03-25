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
    return relevant_attributes(parsed.get('items',[{}]))


def upc_search(upc):
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'upc': upc
    }
    response = requests.get('https://api.walmartlabs.com/v1/items', params=query)
    parsed = response.json()
    return relevant_attributes(parsed.get('items',[{}]))


def relevant_attributes(parsed):
    item = {}
    item['item_name'] = parsed[0].get('name',"")
    item['item_desc'] = parsed[0].get('shortDescription', False)
    item['item_desc'] = item['item_desc'] if item['item_desc'] else parsed[0].get('longDescription', "No description available.")
    return item
