import logging
import os
import io
import zipfile
import json
from datetime import datetime, timedelta
import pandas as pd

import azure.functions as func
from azure.storage.blob import (
    BlockBlobService,
    ContainerPermissions,
    BlobPermissions,
    PublicAccess,
)

def generate_sas_url(AZURE_ACC_NAME,AZURE_PRIMARY_KEY,AZURE_CONTAINER,AZURE_BLOB):
    block_blob_service = BlockBlobService(account_name=AZURE_ACC_NAME, account_key=AZURE_PRIMARY_KEY)    
    sas_url = block_blob_service.generate_blob_shared_access_signature(AZURE_CONTAINER,AZURE_BLOB,BlobPermissions.READ,datetime.utcnow() + timedelta(hours=1))
    return ('https://'+AZURE_ACC_NAME+'.blob.core.windows.net/'+AZURE_CONTAINER+'/'+AZURE_BLOB+'?'+sas_url)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    cwd = os.path.dirname(os.path.realpath(__file__))
    print(cwd)
    json_data=open(cwd + "/config.json").read()
    data = json.loads(json_data)

    account = data["Storage"][0]["Account"]
    accountKey = data["Storage"][0]["Key"]
    storage = BlockBlobService(account, accountKey)

    sessionID = req.params.get('sessionID')
    startTime = datetime.now().strftime('%Y%m%d%H%M')
    audiozipName = 'Recordings'+startTime
    textzipName = 'Statements'+startTime

    #open the text file
    harvard = pd.read_csv(cwd+"/Harvard Statements_clean.txt",sep='\t').drop(columns=['ID'])

    if not sessionID:
        return func.HttpResponse(
             "Please provide the Session ID",
             status_code=400
        )

    if storage.exists(sessionID) == False:
        return func.HttpResponse(
             "Session ID is not valid",
             status_code=400
        )


    a_file_like_object = io.BytesIO()
    audiozf = zipfile.ZipFile(a_file_like_object,'w')

    for blob in storage.list_blobs(sessionID):
        if '.wav' in blob.name:
            blob_bytes = storage.get_blob_to_bytes(sessionID,blob.name)
            audiozf.writestr(blob.name,blob_bytes.content)

    audiozf.close()

    t_file_like_object = io.BytesIO()
    textzf = zipfile.ZipFile(t_file_like_object,'w')

    for blob in storage.list_blobs(sessionID):
        if '.wav' in blob.name:
            #only send text files that have a wav
            #blob_bytes = storage.get_blob_to_bytes(sessionID,blob.name.replace('.wav','.txt'))

            textzf.writestr(blob.name.replace('.wav','.txt'),harvard.iloc[int(blob.name.replace('.wav',''))-1].to_csv (encoding = "utf-8", header = None, index = None, sep = '\t'))

    textzf.close()

    #Upload the zip to the blob
    storage.create_blob_from_bytes(sessionID,audiozipName+'.zip',blob = bytes(a_file_like_object.getvalue()))
    storage.create_blob_from_bytes(sessionID,textzipName+'.zip',blob = bytes(t_file_like_object.getvalue()))

    #generate SAS URLs
    audioZipURL = generate_sas_url(account,accountKey,sessionID,audiozipName+'.zip')
    txtURL = generate_sas_url(account,accountKey,sessionID,textzipName+'.zip')
 
    #make a simple json
    data = {"Audio URL": audioZipURL, "Text URL": txtURL}

    json_data = json.dumps(data)

    response = func.HttpResponse(json_data)
    return response




        
