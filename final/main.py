
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import logging
import os

from flask import Flask, redirect, render_template, request, jsonify, Response, send_file
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
from nlp import get_sentiment_from_reviews

CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


app = Flask(__name__)

@app.route('/word', methods=['GET','POST'])
def submit():
 query = request.form['word']

 api_instance = giphy_client.DefaultApi()
 api_key = 'Zlnfm3OuFEhVERsFfVQ36pFOLbffdpuU' # str | Giphy API Key.
 q = query  # str | Search query term or prhase.
 
 limit = 1 # int | The maximum number of records to return. (optional) (default to 25)
 offset = 0 # int | An optional results offset. Defaults to 0. (optional) (default to 0)
 rating = 'g' # str | Filters results by specified rating. (optional)
 lang = 'en' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">here</a>. (optional)
 fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)

 try: 
    # Search Endpoint
  api_response = api_instance.gifs_search_get(api_key, q, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
  url=api_response.data[0].images.original.url
 
  '''for i in range (0,len(api_response.data)):
  print(api_response.data[i].images.original.url)'''
 except ApiException as e:
  print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
 r = requests.get(url)
 img = Image.open(BytesIO(r.content))
 return Response(r,mimetype="image/gif",headers={"Content-disposition": "attachment; filename="+q+'.gif'})
@app.route('/giphy')
def homepage():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='Faces')
    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template('homepage.html', image_entities=image_entities)

@app.route('/youtube-comment-analysis',methods=['GET'])
def youtube-comment-analysis():
    return render_template('youtube.html')

@app.route('/analyse-comments',methods=['GET'])
def analyse_comments():
    search_text=request.form["name"]
    comment_analysis = get_sentiment_from_reviews(search_text)
    return render_template('youtube.html',analysis = comment_analysis)



 
@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    photo = request.files['file']

    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(
            photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Use the Cloud Vision client to detect a face for our image.
    source_uri = 'gs://{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
    image = vision.types.Image(
        source=vision.types.ImageSource(gcs_image_uri=source_uri))
    faces = vision_client.face_detection(image).face_annotations

    # If a face is detected, save to Datastore the likelihood that the face
    # displays 'joy,' as determined by Google's Machine Learning algorithm.
    if len(faces) > 0:
        face = faces[0]

        # Convert the likelihood string.
        likelihoods = [
            'Unknown', 'Very Unlikely', 'Unlikely', 'Possible', 'Likely',
            'Very Likely']
        face_joy = likelihoods[face.joy_likelihood]
        face_angry=likelihoods[face.anger_likelihood]
        face_suprise=likelihoods[face.surprise_likelihood]
    else:
        face_joy = 'Unknown'
        face_angry= 'Unknown'
        face_suprise='Unknown'
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    current_datetime = datetime.now()

    # The kind for the new entity.
    kind = 'Faces'

    # The name/ID for the new entity.
    name = blob.name

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, name)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity['blob_name'] = blob.name
    entity['image_public_url'] = blob.public_url
    entity['timestamp'] = current_datetime
    entity['joy'] = face_joy
    entity['angry']=face_angry
    entity['suprise']=face_suprise

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """ An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
