import json
import os
import uuid


def _get_table():
    """Lazily initialize DynamoDB table so tests that don't set env var don't need boto3."""
    table_name = os.environ.get('TICKETS_TABLE', '')
    if not table_name:
        return None
    try:
        import boto3
    except Exception:
        return None
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)


def lambda_handler(event, context):
    # Simple handler to create or fetch tickets depending on HTTP method
    table = _get_table()

    method = event.get('requestContext', {}).get('http', {}).get('method') if isinstance(event.get('requestContext'), dict) else None

    try:
        body = json.loads(event.get('body') or '{}')
    except Exception:
        body = {}

    if method == 'GET':
        # return a simple message or dummy list
        ticket_id = (event.get('pathParameters') or {}).get('id')
        if table and ticket_id:
            resp = table.get_item(Key={'id': ticket_id})
            item = resp.get('Item')
            return {'statusCode': 200, 'body': json.dumps({'ticket': item})}
        return {'statusCode': 200, 'body': json.dumps({'tickets': []})}

    # Default to creating/updating ticket
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
