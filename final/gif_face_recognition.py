import time
from datetime import datetime
from google.cloud import storage
from google.cloud import vision
import os
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')
PROJECT_ID = os.environ.get('PROJECT_ID')
def face_recognition(photo):
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
    # Use the Cloud Vision client to detect a face for the image.
    source_uri = 'gs://{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
    image = vision.types.Image(
        source=vision.types.ImageSource(gcs_image_uri=source_uri))
    faces = vision_client.face_detection(image).face_annotations

    # If a face is detected, display the joy, anger, suprise likelihood
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

    # Fetch the current date / time.
    current_datetime = datetime.now()

    # The name/ID for the new entity.
    name = blob.name

   # Construct the new entity facial_expression, set dictionary values like blob_name, storage_public_url, timestamp, anger, suprise and joy.
    facial_expression={}
    facial_expression['blob_name'] = blob.name
    facial_expression['image_public_url'] = blob.public_url
    facial_expression['timestamp'] = current_datetime
    facial_expression['joy'] = face_joy
    facial_expression['angry']=face_angry
    facial_expression['suprise']=face_suprise
    return(facial_expression)
