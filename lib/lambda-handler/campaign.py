import json
import os
import uuid
import logging
import boto3
 
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
 
 
def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))
 
    if event['body'] is not None:
        body = event['body']
    else:
        body = event
    
    # campaign_id = body['campaignId']
    # redirect_url = body['redirectUrl']

    if event['pathParameters'] is not None:
        return redirect(event)
    
    
    return create_short_url(body)

    return {
        'statusCode': 200,
        'body': 'GET url/1/userId'
    }
 
 
def create_short_url(body):
    # Pull out the DynamoDB table name from environment
    table_name = os.environ.get('TABLE_NAME')
 
    # Parse targetUrl
    redirect_url = body['redirectUrl']
    campaign_id = body['campaign_url']
 
    client = boto3.client('dynamodb')
    response = client.describe_table(table_name)
    item_count = int(response['Table']['ItemCount'])

    # Create a unique id
    id = item_count + 1
    item = {
        'id': id,
        'redirect_url': redirect_url,
        'campaign_id': campaign_id
    }

    # Create item in DynamoDB
    response = client.put_item(
        TableName=table_name,
        Item=item
    )
  
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': response
    }
 
 
def redirect(event):
    # Parse redirect ID from path
    id = event['pathParameters']['proxy']
 
    # Pull out the DynamoDB table name from the environment
    table_name = os.environ.get('TABLE_NAME')
 
    # Load redirect target from DynamoDB
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("RESPONSE: " + json.dumps(response))
 
    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'No redirect found for ' + id
        }
 
    # Respond with a redirect
    return {
        'statusCode': 301,
        'headers': {
            'Location': item.get('redirect_url')
        }
    }