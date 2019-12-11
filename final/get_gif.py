import giphy_client
import requests

api_instance = giphy_client.DefaultApi()

def get_gif_from_api(query):
 """
 Using giphy_client create an api instance,
 collect the url of the GIF based on the query and retrieve data from url.
 :param query:string
 :return url_content: requests.models.Response or string if there are no GIF's
 """
 #Giphy API Key.
 api_key = 'Zlnfm3OuFEhVERsFfVQ36pFOLbffdpuU'
 # Search query term or phrase.
 q = query
 # The maximum number of records to return.
 limit = 1
 # Specify default country for regional content.
 lang = 'en'
 # Used to indicate the expected response format.
 fmt = 'json'
 # Search Endpoint
 api_response = api_instance.gifs_search_get(api_key, q, limit=limit, lang=lang, fmt=fmt)
 #if data in response exits then return the content in the image.
 if api_response.data:
  #collect the url
  url=api_response.data[0].images.original.url
  #retrieve data from url
  url_content = requests.get(url)
  return(url_content)
 #if not return a string none.
 else:
  url_content='None'
  return(url_content)
