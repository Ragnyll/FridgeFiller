import json
import requests
import secret


def item_search(item):
    response = requests.get("https://qpi.walmartlabs.com/v1/search?apiKey{" 
                           + secret.walmart_api_key + "}&lsPublisherId=\
                           {FridgeFiller}&query=" + item)
    return json.loads(response)


def ean_search(upc):
    response = requests.get("https://qpi.walmartlabs.com/v1/items?apiKey{" 
                           + secret.walmart_api_key + "}&lsPublisherId=\
                           {FridgeFiller}&upc=" + upc)
    return json.loads(response)

