from HTMLParser import HTMLParser
import requests
import secret


class Parser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.desc = ""

    #def handle_starttag(self, tag, attrs):
    #    print "Encountered a start tag:", tag

    #def handle_endtag(self, tag):
    #    print "Encountered an end tag :", tag

    def handle_data(self, data):
        self.desc += data


def item_search(item):
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'query': item
    }
    response = requests.get('https://api.walmartlabs.com/v1/search', params=query)
    json = response.json()
    return json.get('items',{})


def upc_search(upc):
    query = {
        'apiKey': secret.walmart_api_key,
        'lsPublisherId': 'FrideFiller',
        'upc': upc
    }
    response = requests.get('https://api.walmartlabs.com/v1/items', params=query)
    json = response.json()
    return json.get('items', {})


def relevant_attributes(json):
    parser = Parser()
    item = {}
    item['item_name'] = json[0].get('name',"")
    item['item_desc'] = json[0].get('shortDescription', "")
    item['item_desc'] = item['item_desc'] if item['item_desc'] != "" else json[0].get('longDescription', "No description available.")
    desc = parser.unescape(item['item_desc'])
    parser.feed(desc)
    item['item_desc'] = parser.desc if parser.desc != "" else desc
    return item
