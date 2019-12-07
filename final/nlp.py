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
    callme_for_fetching_comments(search_text)
    #opens the comments.csv file for reading
    with open('comments.csv', mode='r') as csv_file:
    #converts csv into python dict for easy reading
    csv_reader = csv.DictReader(csv_file)
    myvideodb={}
    comment_analysis = {}
    #inserts a {"key":"value" of the form {"Video Title":"Comments on the video" into myvideodb}
    for row in csv_reader:
        if row['Title'] in myvideodb:
            myvideodb[row['Title']]+=row['Comment'] + ' '
        else:
            myvideodb[row['Title']]=row['Comment'] + ' '
    for title in myvideodb:
        print(title)
        document = types.Document(
        content=myvideodb[title],
        type=enums.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
        comment_analysis[title]={"Score":sentiment.score,"Magnitude":sentiment.magnitude}
    return comment_analysis