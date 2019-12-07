# Imports the Google Cloud client library
import csv
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from youtubedata import callme_for_fetching_comments

# Instantiates a client
client = language.LanguageServiceClient()