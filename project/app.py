"""
A Bubble Tea flask app.
"""
from flask import Flask, redirect, request, url_for, render_template

from model_sqlite3 import model

app = Flask(__name__)
model = model()

"""
Function decorator === app.route('/',index())
"""
@app.route('/')
@app.route('/index')
def index():

   return render_template('index.html')

@app.route('/sign')
def sign():
 """
 renders to submit.html page
 """
 return render_template('submit.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    submits the bubble tea store location entries 
    """
    model.insert(request.form['name'], request.form['address'], request.form['city'], request.form['state'], request.form['zipcode'], request.form['message'])
    return redirect(url_for('index'))

@app.route('/view')
def view():
    """
    shows all the entries
    """
    entries = [dict(name=row[0], address=row[1], city=row[2], state=row[3], zipcode=row[4], signed_on=row[5], message=row[6] ) for row in model.select()]
    return render_template('view.html', entries=entries)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000, debug=True)

