import logging
import os
import zipfile
import json
from datetime import datetime, timedelta

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
    zipName = 'Recordings'+startTime

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


    pathBase = str(os.path.dirname(os.path.realpath(__file__)) + '/' + zipName)
    print(pathBase)
    if not os.path.exists(pathBase):
        os.makedirs(pathBase)

    for blob in storage.list_blobs(sessionID):
        storage.get_blob_to_path(sessionID, blob.name, pathBase+'/'+blob.name)

    zf = zipfile.ZipFile(pathBase+'/'+zipName+".zip", "w")

    for filename in os.listdir(pathBase):
        if filename.endswith(".wav"):            
            zf.write(os.path.join(pathBase, filename),filename)
        else:
            print('something else')
    zf.close()

    #Upload the zip to the blob
    storage.create_blob_from_path(sessionID,zipName+'.zip',pathBase+'/'+zipName+".zip")

    #remove all files
    for file in os.scandir(pathBase):
        os.unlink(file.path)

    #rename the statements text file
    if not storage.exists(sessionID,'Statements.txt'):
        return func.HttpResponse(
             "Text file expected",
             status_code=400
        )

    blob_url = storage.make_blob_url(sessionID, 'Statements.txt')
    newName = 'Statements'+startTime+'.txt'
    storage.copy_blob(sessionID, newName, blob_url)

    #generate SAS URLs
    zipURL = generate_sas_url(account,accountKey,sessionID,zipName+'.zip')
    txtURL = generate_sas_url(account,accountKey,sessionID,newName)
 
    #make a simple json
    data = {"Zip URL": zipURL, "Text URL": txtURL}

    json_data = json.dumps(data)

    response = func.HttpResponse(json_data)
    return response




        
