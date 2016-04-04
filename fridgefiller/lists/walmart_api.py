from HTMLParser import HTMLParser
import requests
import secret


name_mapping = {
    'cost': 'salePrice',
    'unit': 'size',
    }
    

class Parser(HTMLParser):

    """
    Simple parser that concatenates html field data after removing surrounding tags.
    """
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.desc = ""

    def handle_data(self, data):
        #concatenate field data
        self.desc += data


def item_search(item):

    """
    Queries the walmart api with the given item string.
    Returns the list of items in the response.
    
    https://developer.walmartlabs.com/docs
    """

    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'query': item
    }
    response = requests.get('https://api.walmartlabs.com/v1/search', params=query)
    json = response.json()
    return json.get('items', {})


def upc_search(upc):

    """
    Queries the walmart api with the given upc code.
    Returns the list of items in the response.

    https://developer.walmartlabs.com/docs
    """
    
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'upc': upc
    }
    response = requests.get('https://api.walmartlabs.com/v1/items', params=query)
    json = response.json()
    return json.get('items', {})


def relevant_attributes(json, attrs):
    
    """
    Pulls item name and description from the first item available.
    Returns unescaped html for item description with html tags removed if they exist.
    """
    
    parser = Parser()
    item = {}
    item['item_name'] = json[0].get('name',"No name available.")
    item['item_desc'] = json[0].get('shortDescription', "")
    item['item_desc'] = item['item_desc'] if item['item_desc'] != "" else json[0].get('longDescription', "No description available.")
    # unescape and remove html tags
    desc = parser.unescape(item['item_desc'])
    parser.feed(desc)
    item['item_desc'] = parser.desc if parser.desc != "" else desc
    parser.desc = ""
    for attr in attrs:
        desc = parser.unescape(str(json[0].get(name_mapping[attr], "")))
        parser.feed(desc)
        item[attr] = parser.desc if parser.desc != "" else desc
        parser.desc = ""
    return item
