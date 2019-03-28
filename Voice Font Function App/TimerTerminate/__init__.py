import datetime
import logging
import os
import json

import azure.functions as func
from azure.storage.blob import BlockBlobService


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    #conect to storage account
    cwd = os.path.dirname(os.path.realpath(__file__))
    print(cwd)
    json_data=open(cwd + "/keys.json").read()
    data = json.loads(json_data)
    print(data)

    account = data["Storage"][0]["Account"]
    accountKey = data["Storage"][0]["Key"]
    storage = BlockBlobService(account, accountKey)

    ignore = ['azure-webjobs-hosts','azure-webjobs-secrets','azureappservice-run-from-package','function-releases','text']

    for container in storage.list_containers():
        if container.name not in ignore:
            properties = storage.get_container_properties(container.name)
            difference = datetime.datetime.now() - properties.properties.last_modified.replace(tzinfo=None)

            if difference > datetime.timedelta(minutes=10080):
                print('delete')
                print(difference)
                storage.delete_container(container.name)
        