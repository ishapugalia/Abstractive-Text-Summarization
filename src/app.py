#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from nltk_summarization import nltk_summarizer
import os
import subprocess
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')


def predict(input):
    file = open("C:/Users/ISHA/Documents/GitHub/NLP-Project/src/demo/demo_data/1.story", "w");
    file.write(input);
    file.close();
    subprocess.call(['sh',"C:/Users/ISHA/Documents/GitHub/NLP-Project/src/demo/run.sh"]);
    # file = open("src/demo/fast_abs_rl-master/output/output/0.dec");
    # output = file.read();
    # file.close();
    subprocess.call(['sh',"src/demo/clean.sh"]);
    output = nltk_summarizer(input)

    return output

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        ## Called after submit button is clicked
        output = predict(request.form['input_text'])
        template = render_template('project.html', result=output)
        return template

    if request.method == 'GET':
        return render_template('project.html')


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

