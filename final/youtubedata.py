import csv
import os
import pickle
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
    #The youtube data api needs app credentials for working which expires after some amount
    # of time. So we are storing the credentials in a token.pickle which stores the credentials
    #in an encrypted form. 
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
            # Every time the credential expires it has to be refreshed which we are
            # achieving in the following function.
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
        # Youtube stores comments for videos in multiple pages
        #This function fetches the comments on a video in a page
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
    kwargs: Additional arguments which are set as query parameters
    param q: String, any search text that you want to search on youtube
    param eventType: String, The eventType parameter restricts a search to
    broadcast events. If you specify a value for this parameter, you must also
    set the type parameter's value to video. The accepted values are- completed,
    live, upcoming.
    param type: String, The type parameter restricts a search query to only retrieve
    a particular type of resource. The acceptable values are channel, playlist, video
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
    kwargs: Additional arguments which are set as query parameters
    param q: String, any search text that you want to search on youtube
    param eventType: String, The eventType parameter restricts a search to
    broadcast events. If you specify a value for this parameter, you must also
    set the type parameter's value to video. The accepted values are- completed,
    live, upcoming.
    param type: String, The type parameter restricts a search query to only retrieve
    a particular type of resource. The acceptable values are channel, playlist, video
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
