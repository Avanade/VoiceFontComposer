import logging
import json
import os

import azure.functions as func
from azure.storage.blob import BlockBlobService


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # conect to storage account
    cwd = os.path.dirname(os.path.realpath(__file__))
    print(cwd)
    json_data = open(cwd + "/config.json").read()
    data = json.loads(json_data)
    print(data)

    account = data["Storage"][0]["Account"]
    accountKey = data["Storage"][0]["Key"]
    origin = data["FunctionApp"][0]["URL"]
    storage = BlockBlobService(account, accountKey)
    return_headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
    }

    sessionID = req.params.get("sessionID")
    fileID = req.params.get("fileID")
    body = req.get_body()

    if b"audio/wav" in body:
        blob = body.split(b"audio/wav\r\n\r\n")[1].split(
            b"----------------------------"
        )[0]
    elif b"audio/wave" in body:
        blob = body.split(b"audio/wave\r\n\r\n")[1].split(
            b"----------------------------"
        )[0]
    elif b"text/plain" in body:
        blob = body.split(b"text/plain\r\n\r\n")[1].split(
            b"----------------------------"
        )[0]
    else:
        blob = body

    if len(blob) == 0:
        return func.HttpResponse(
            "No valid file attatched - please add a binary file to the request body",
            status_code=400,
            headers=return_headers,
        )

    if not sessionID:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            sessionID = req_body.get("sessionID")

    if sessionID:
        try:
            storage.create_blob_from_bytes(sessionID, fileID, blob)
            response = func.HttpResponse(
                f"The Session ID is {sessionID} - Blob {fileID} created successfully",
                headers=return_headers,
            )

            return response
        except:
            return func.HttpResponse(
                "Invalid account name, key, or container name",
                status_code=400,
                headers=return_headers,
            )
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400,
            headers=return_headers,
        )
