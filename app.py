"""
Simple Flask site to take in a topic and render a generated Obama speech.

* Requires Flask. (pip install flask)
* Assumes we can get the speech text by calling the speech() function from obama.py.

Usage:
$ python app.py
Browse to http://127.0.0.1:5000/.
"""
from flask import Flask, request, render_template

from obama import speech

app = Flask(__name__)

@app.route('/')
def home():
    topic = request.args.get('topic', '')
    if topic:
        result = speech(topic)
    else:
        result = 'Enter a topic to generate a speech.'
    return render_template('speech.html', speech=result)


if __name__ == '__main__':
    app.run()
