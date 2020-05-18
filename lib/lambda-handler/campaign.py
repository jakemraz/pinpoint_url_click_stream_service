import json
import os
import uuid
import logging
import boto3
import time
import datetime
 
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def handler(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    if event['body'] is not None:
        body = json.loads(event['body'])
    else:
        body = event

    if event['pathParameters'] is not None:
        return redirect(event)

    return create_short_url(body)
 
def create_short_url(body):
    # Pull out the DynamoDB table name from environment
    table_name = os.environ.get('TABLE_NAME')

    # Parse targetUrl
    redirect_url = body['redirectUrl']
    campaign_id = body['campaignId']
    pinpoint_application_id = body['pinpointApplicationId']

    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.scan()
    item_count = int(response['Count'])

    # Create a unique id
    id = item_count + 1
    item = {
        'id': id,
        'redirect_url': redirect_url,
        'campaign_id': campaign_id,
        'pinpoint_application_id': pinpoint_application_id
    }

    # Create item in DynamoDB
    response = table.put_item(
        Item=item
    )

    return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(item)
    }
 
 
def redirect(event):
    # Parse redirect ID from path
    proxy = event['pathParameters']['proxy']
    parsed = proxy.split('/')
    id = int(parsed[0])
    endpoint_id = parsed[1] if len(parsed) > 1 else None

    print(parsed)

    # Pull out the DynamoDB table name from the environment
    table_name = os.environ.get('TABLE_NAME')

    # Load redirect target from DynamoDB
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    print(response)

    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }

    # Put Pinpoint Event to mark as read this campaign
    pinpoint_application_id = item.get('pinpoint_application_id')
    putPinpointEvent(pinpoint_application_id, id, endpoint_id)

    redirect_url = item.get('redirect_url')
    if redirect_url[:4] != "http":
        redirect_url = "http://" + redirect_url

    print('redirect to ' + redirect_url)

    # Respond with a redirect
    return {
        'statusCode': 301,
        'headers': {
            'Location': redirect_url
        }
    }

def putPinpointEvent(pinpoint_application_id, id, endpoint_id):

    # Pull out the DynamoDB table name from the environment
    table_name = os.environ.get('TABLE_NAME')

    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }

    campaign_id = item.get('campaign_id')

    sec = int(time.time())
    KST = datetime.timezone(datetime.timedelta(hours=9))
    timestamp = datetime.datetime.fromtimestamp(sec, KST).isoformat()

    events_request = {
        'BatchItem': {}
    }

    batch_item = {
        "Endpoint": {
                    },
        "Events": {
            "key1": {
                "EventType": "sms.click",
                "Timestamp": timestamp,
                "AppVersionCode": campaign_id
            }
        }
    }
    
    events_request['BatchItem'][endpoint_id] = batch_item

    client = boto3.client('pinpoint')
    response = client.put_events(
        ApplicationId=pinpoint_application_id,
        EventsRequest=events_request
    )
    print('PutEvents response')
    print(response)

    return response


