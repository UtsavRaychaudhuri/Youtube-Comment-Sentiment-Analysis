import csv
import os
import pickle
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = ["https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service(API_SERVICE_NAME,API_VERSION,SCOPES):
    """
    param API_SERVICE_NAME: String
    param API_VERSION: String
    param SCOPES: String
    :return: Youtube Cloud Discovery Resource Object
    """
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
            credentials.refresh(Request())
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_video_comments(youtube, **kwargs):
    """
    Get comments from the video
    param youtube: Resource object, has methods for interacting with the youtube cloud discovery api
    kwargs: Additional arguments passed to http request
    param q: String,
    param eventType: String,
    param type: String,
    return comments: List
    """
    comments = []
    results = ""
    try:
        #Fetch the comments of a video in a page
        results = youtube.commentThreads().list(**kwargs).execute()
    except HttpError:
        print("There was some errors listing the comments")
    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if len(comments)>5:
                break
        # Check if another page exists
        if 'nextPageToken' in results:
            if len(comments)>5:
                break
            kwargs['pageToken'] = results['nextPageToken']
            results = youtube.commentThreads().list(**kwargs).execute()
        else:
            break
    return comments

def get_videos(youtube, **kwargs):
    """
    Fetches videos from youtube based on a searchtext and returns the comments from the videos
    param youtube: Resource object, has methods for interacting with the youtube cloud discovery api
    kwargs: Additional arguments passed to http request
    param part: String
    param videoId: Integer
    param textFormat: String
    return final_result: List
    """
    final_results = []
    results = youtube.search().list(**kwargs).execute()
    i = 0
    max_pages = 3
    while results and i < max_pages:
        final_results.extend(results['items'])
        # Check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = youtube.search().list(**kwargs).execute()
            i += 1
        else:
            break
    return final_results

def search_videos_by_keyword(youtube, **kwargs):
    """
    Fetches videos from youtube based on a searchtext and returns the comments from the videos
    param youtube: Resource object, has methods for interacting with the youtube cloud discovery api
    kwargs: Additional arguments passed to http request
    param q: String
    param eventType: String
    param type: String
    return final_result: List
    """
    results = get_videos(youtube, **kwargs)
    final_result = []
    for item in results:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        comments = get_video_comments(youtube, part='snippet', videoId=video_id, textFormat='plainText')
        # make a tuple consisting of the video id, title, comment and add the result to 
        # the final list
        final_result.extend([(video_id, title, comment) for comment in comments]) 
    return final_result

def callme_for_fetching_comments(search_text):
    """
    Fetches comments from youtube using the youtube data api based on a search text
    :param search_text: String
    return final_comments: List
    """
    # When running locally, disable OAuthlib's HTTPs verification.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    youtube = get_authenticated_service(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,YOUTUBE_READ_WRITE_SSL_SCOPE)
    final_comments = search_videos_by_keyword(youtube, q=search_text, part='id,snippet', eventType='completed', type='video')
    return final_comments
