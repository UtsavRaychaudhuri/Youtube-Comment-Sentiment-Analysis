# Imports the Google Cloud client library
import csv
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from youtubedata import callme_for_fetching_comments

# Instantiates a client
client = language.LanguageServiceClient()

def get_sentiment_from_reviews(search_text):
    #Calling videointelligence for fetching comments
    final_result = callme_for_fetching_comments(search_text)
    myvideodb = {}
    comment_analysis= {}
    for row in final_result:
        if row[1] in myvideodb:
            myvideodb[row[1]]+=row[2] + ' '
        else:
            myvideodb[row[1]]=row[2] + ' '
    for title in myvideodb:
        document = types.Document(
        content=myvideodb[title],
        language="EN",
        type=enums.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        # print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
        comment_analysis[title]={"Score":sentiment.score,"Magnitude":sentiment.magnitude}
    return comment_analysis