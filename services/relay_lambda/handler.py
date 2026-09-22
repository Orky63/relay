import json
import os
import uuid
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TICKETS_TABLE', '')
table = dynamodb.Table(table_name) if table_name else None

def lambda_handler(event, context):
    # Simple handler to create a ticket
    body = {}
    try:
        body = json.loads(event.get('body') or '{}')
    except Exception:
        pass

    ticket = {
        'id': body.get('id') or str(uuid.uuid4()),
        'title': body.get('title', 'No title'),
        'status': body.get('status', 'open')
    }

    if table:
        table.put_item(Item=ticket)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'ticket': ticket})
    }
