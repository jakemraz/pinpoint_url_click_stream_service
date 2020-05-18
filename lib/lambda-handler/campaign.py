import json
import os
import uuid
import logging
import boto3
 
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

    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.scan()
    item_count = int(response['Count'])

    # Create a unique id
    id = item_count + 1
    item = {
        'id': id,
        'redirect_url': redirect_url,
        'campaign_id': campaign_id
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
    id = int(event['pathParameters']['proxy'])

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

    redirect_url = item.get('redirect_url')
    if redirect_url[:4] != "http":
        redirect_url = "http://" + redirect_url

    # Respond with a redirect
    return {
        'statusCode': 301,
        'headers': {
            'Location': redirect_url
        }
    }
