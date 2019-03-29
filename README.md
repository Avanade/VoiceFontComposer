# Voice Font Composer

# Introduction 
The voice font composer is an Azure based web app based on Azure components to help record data to be fed into the Microsoft Voice Font Cognitive Service, currently in  preview. This small tool helps a user to record pre-determined phrases within the constraints required by the service. The output is a zip file containing the wav files, and a txt file containing the transcript for the user to read. [Microsoft Voice Fonts](https://westus.cris.ai/Home/CustomVoice)

# Getting Started
To install the voice fonts app on Azure you will need the following Azure services:
1.    An Azure blob storage contianer
2.    An Azure function app - Linux running python 
3.    An Azure web app - Linux running python

# Build and Test
The function app and web app can be built locally in visual studio code. The Azure extention to VS code can be used to deploy this code to the Azure services. The config.json files will need to be updated with the account name and key of the Azure storage container you would like to use as well as the URL of the function app - whether local or in Azure.
The function app and web app can be built locally in visual studio code. The Azure extention to VS code can be used to deploy this code to the Azure services.

For the Function App the config.json files will need to be updated with the account name and key of the Azure storage container you would like to use. N.B. that the function app is developed in Python 3.6.8 due to current constraints in Azure with the preview Python Function App offering.

For the Web App the URLs in the config.json will need to be changed to those of the services you have created, whether using an Azure host or a local host.
When using an Azure Web App the 'Startup File' should be set to 'gunicorn --bind=0.0.0.0 --timeout 600 --chdir voice_fonts app:app'
To run locally, start debugging with the Python:Flask debug configuration

# Related Projects

[JS Web Audio Recorder](https://github.com/higuma/web-audio-recorder-js)
