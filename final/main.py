from flask import Flask, redirect, render_template, request, jsonify, Response
from nlp import get_sentiment_from_reviews
from get_gif import get_gif_from_api
from gif_face_recognition import face_recognition

app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    """    renders the homepage
    renders to youtube-giphy.html page """
    return render_template('youtube-giphy.html')


@app.route('/giphy',methods=['GET'])
def giphy():
    return render_template('homepage.html')


@app.route('/word', methods=['GET','POST'])
def submit():
    query = request.form['word']
    url_content=get_gif_from_api(query)
    if url_content=='None':
       return render_template('homepage.html')
    else:
       return Response(url_content,mimetype="image/gif",headers={"Content-disposition": "attachment; filename="+query+'.gif'})


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
     photo = request.files['file']
     facial_expression=face_recognition(photo)
     # Redirect to the home page.
     return render_template('homepage.html', facial_expression=facial_expression)


@app.route('/youtube_comment_analysis',methods=['GET'])
def youtube_comment_analysis():
    """
    Renders youtube.html page
    """
    return render_template('youtube.html')


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
