"""
The flask application package and route/view rendering.
"""
import os
from flask import Flask, render_template, url_for
from datetime import datetime
import voice
import json
import requests
import urllib
import http

app = Flask(__name__)

global base_url

config_data=open("config.json").read()
data = json.loads(config_data)
base_url = data["FunctionApp"][0]["BaseURL"]

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/record', methods=['GET', 'POST'])
def record(): 
    "Renders the record page."
    #generate a new session_id:
    voice.statements.new_session()
    voice.statements.iterate()
    #initilise container space
    url = base_url + '/api/Initialise'
    params = {'sessionID': voice.statements.session_id}
    try:
        response = requests.post(url = url,params = params)
        print(response)
    except Exception as e:
        print('Error:')
        print(e)
    return render_template(
        'record.html', 
        ID = voice.statements.harvard['ID'][0],
        SessionID = voice.statements.session_id,
        message = voice.statements.harvard['Phrases'][0],
        title = 'Make a Recording',
        year=datetime.now().year)

@app.route('/next_clip')
def next_clip(): 
    "Renders the record page."
    i = voice.statements.iterator
    voice.statements.iterate()
    #save the clip
    return render_template(
        'record.html', 
        ID = voice.statements.harvard['ID'][i],
        SessionID = voice.statements.session_id,
        message = voice.statements.harvard['Phrases'][i],
        title = 'Make a Recording',
        year=datetime.now().year)

@app.route('/previous_clip')
def previous_clip(): 
    "Renders the record page."
    voice.statements.reverse_iterate()
    i = voice.statements.iterator
    return render_template(
        'record.html', 
        ID = voice.statements.harvard['ID'][i],
        SessionID = voice.statements.session_id,
        message = voice.statements.harvard['Phrases'][i],
        title = 'Make a Recording',
        year=datetime.now().year)

@app.route('/export')
def export():
        voice.statements.export_list()

        url = base_url+'/api/PassBlob'
        params = {'sessionID': voice.statements.session_id,
                'fileID': 'Statements.txt'}
        body = voice.statements.harvard.to_csv (encoding = "utf-8", header = None, index = None, sep = '\t')
        try:
            response = requests.post(url = url,params = params,data=body)
            code = response.status_code
            print(code)
            print(response.text)
        except Exception as e:
            print('Error:')
            print(e)

        zipUrl = base_url+'/api/zipfiles'
        zipParams = {'sessionID': voice.statements.session_id}
        try:
            response = requests.post(url = zipUrl,params = zipParams)
            code = response.status_code
            print(code)
            print('export response')
            print(response.text)
            result = json.dumps(response.json(), sort_keys=True, indent=2)
            parsedJson = json.loads(result)
        except Exception as e:
            print('Error:')
            print(e)

        return render_template(
            'finished.html', 
            message = 'Download your transcript and recordings',
            title = 'Download your recordings',
            txtURL = parsedJson['Text URL'],
            zipURL = parsedJson['Zip URL'],
            year=datetime.now().year)