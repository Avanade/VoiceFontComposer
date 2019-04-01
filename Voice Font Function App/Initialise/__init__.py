import logging
import json
import os

import azure.functions as func
from azure.storage.blob import BlockBlobService

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #conect to storage account
    cwd = os.path.dirname(os.path.realpath(__file__))
    print(cwd)
    json_data=open(cwd + "/config.json").read()
    data = json.loads(json_data)
    print(data)

    account = data["Storage"][0]["Account"]
    accountKey = data["Storage"][0]["Key"]
    storage = BlockBlobService(account, accountKey)

    sessionID = req.params.get('sessionID')
    if not sessionID:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            sessionID = req_body.get('sessionID')

    if sessionID:
        try:
            storage.create_container(sessionID)
            return func.HttpResponse(f"The Session ID is {sessionID} - container created successfully")
        except:
            return func.HttpResponse(
             "Invalid account name, key, or container name",
             status_code=400
        )
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
