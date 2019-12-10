
from datetime import datetime
import logging
import os

from flask import Flask, redirect, render_template, request, jsonify, Response
from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision

from nlp import get_sentiment_from_reviews
from get_gif import get_gif_from_api

CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')
PROJECT_ID = os.environ.get('PROJECT_ID')

app = Flask(__name__)

@app.route('/word', methods=['GET','POST'])
def submit():
 query = request.form['word']
 url_content=get_gif_from_api(query)
 if url_content=='None':
  return render_template('homepage.html')
 else:
  return Response(url_content,mimetype="image/gif",headers={"Content-disposition": "attachment; filename="+query+'.gif'})


@app.route('/giphy',methods=['GET'])
def giphy():
    return render_template('homepage.html')

@app.route('/youtube_comment_analysis',methods=['GET'])
def youtube_comment_analysis():
    """
    Renders youtube.html page
    """
    return render_template('youtube.html')

@app.route('/',methods=['GET'])
def home():
    """    renders the homepage
    renders to youtube-giphy.html page """
    return render_template('youtube-giphy.html')

@app.route('/analyse-comments',methods=['GET','POST'])
def analyse_comments():
    """
    Handles search text from the form and passes the searchtext to
    get_sentiment_from_reviews.
    After processing renders view.html.
    """
    search_text=request.form["name"]
    comment_analysis = get_sentiment_from_reviews(search_text)
    return render_template('view.html',comment_analysis = comment_analysis)

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    photo = request.files['file']

    # Create a Cloud Storage client.
    #storage_client = storage.Client()
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
    entity={}
    #entity = datastore.Entity(key)
    entity['blob_name'] = blob.name
    entity['image_public_url'] = blob.public_url
    entity['timestamp'] = current_datetime
    entity['joy'] = face_joy
    entity['angry']=face_angry
    entity['suprise']=face_suprise
    
    # Save the new entity to Datastore.
    #datastore_client.put(entity)

    # Redirect to the home page.
    #return redirect('/giphy', entity=entity)
    return render_template('homepage.html', entity=entity)
    #return jsonify(entity['blob_name'])

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
