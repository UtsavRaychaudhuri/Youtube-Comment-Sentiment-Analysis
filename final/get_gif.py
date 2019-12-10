import mimetypes
from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision
import giphy_client 
import time
import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint
from PIL import Image
import requests
from io import BytesIO
import urllib.request

api_instance = giphy_client.DefaultApi()

def get_gif_from_api(query):
 api_key = 'Zlnfm3OuFEhVERsFfVQ36pFOLbffdpuU' # str | Giphy API Key.
 q = query  # str | Search query term or prhase.
 limit = 1 # int | The maximum number of records to return. (optional) (default to 25)
 offset = 0 # int | An optional results offset. Defaults to 0. (optional) (default to 0)
 rating = 'g' # str | Filters results by specified rating. (optional)
 lang = 'en' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">$
 fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)


    # Search Endpoint
 api_response = api_instance.gifs_search_get(api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
 if api_response.data:
  url=api_response.data[0].images.original.url
  url_content = requests.get(url)
  return(url_content)
 else:
  url_content='None'
  return(url_content)

''' except ApiException as e:
  return "Exception when calling GIF's"'''
