# Imports the Google Cloud client library
import csv
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from youtubedata import callme_for_fetching_comments

# Instantiates a client
client = language.LanguageServiceClient()

def get_sentiment_from_reviews(search_text):
    """
    Calls the youtube data apis for fetching the videos and then
    comments from the videos and returns a dict object comment_analysis
    The structure of the object returned is {"String":{"String":Integer,"String":Integer}}
    {"Title of the video":
        {"Score":the score of the comments from -1 to 1, -1 being highly negative
        1 being highly positive
         "Magnitude":The score of how much positive or negative the comments are ranging from 0 to infinity
    }}
    param search_text: String
    return comment_analysis: dict
    """
    #Calling youtubedata for fetching comments
    final_result = callme_for_fetching_comments(search_text)
    myvideodb = {}
    comment_analysis= {}
    for row in final_result:
        #If title of the video in the dict add the comment to the key as a value
        if row[1] in myvideodb:
            myvideodb[row[1]]+=row[2] + ' '
        else:
            #add the title of the video as a key
            myvideodb[row[1]]=row[2] + ' '
    for title in myvideodb:
        document = types.Document(
        content=myvideodb[title],
        language="EN",
        type=enums.Document.Type.PLAIN_TEXT)
        # Detects the sentiment of the text
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        comment_analysis[title]={"Score":sentiment.score,"Magnitude":sentiment.magnitude}
    return comment_analysis