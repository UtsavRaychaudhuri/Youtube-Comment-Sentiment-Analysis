import giphy_client
import requests

api_instance = giphy_client.DefaultApi()

def get_gif_from_api(query):
 api_key = 'Zlnfm3OuFEhVERsFfVQ36pFOLbffdpuU' #Giphy API Key.
 q = query  # Search query term or phrase.
 limit = 1 # The maximum number of records to return.
 lang = 'en' # Specify default country for regional content.
 fmt = 'json' # Used to indicate the expected response format.


 # Search Endpoint
 api_response = api_instance.gifs_search_get(api_key, q, limit=limit, lang=lang, fmt=fmt)
 #if data in response exits then return the content in the image.
 if api_response.data:
  url=api_response.data[0].images.original.url
  url_content = requests.get(url)
  return(url_content)
 #if not return a string none.
 else:
  url_content='None'
  return(url_content)
