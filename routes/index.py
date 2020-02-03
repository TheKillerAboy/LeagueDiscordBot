import GLOBALS
from flask import render_template

@GLOBALS.app.route('/')
def index():
    return render_template('index.html')