# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    
    # Log request context for security audit
    request_context = event.get('requestContext', {})
    logger.info(json.dumps({
        'event': 'request_received',
        'request_id': context.request_id,
        'source_ip': request_context.get('identity', {}).get('sourceIp'),
        'user_agent': request_context.get('identity', {}).get('userAgent'),
        'request_time': request_context.get('requestTime'),
    }))
    
    try:
        if event.get("body"):
            item = json.loads(event["body"])
            logger.info(json.dumps({
                'event': 'processing_request',
                'item_id': item.get('id'),
            }))
            
            year = str(item["year"])
            title = str(item["title"])
            id = str(item["id"])
            
            dynamodb_client.put_item(
                TableName=table,
                Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
            )
            
            logger.info(json.dumps({
                'event': 'dynamodb_write_success',
                'item_id': id,
            }))
            
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
        else:
            logger.info(json.dumps({'event': 'processing_default_request'}))
            
            default_id = str(uuid.uuid4())
            dynamodb_client.put_item(
                TableName=table,
                Item={
                    "year": {"N": "2012"},
                    "title": {"S": "The Amazing Spider-Man 2"},
                    "id": {"S": default_id},
                },
            )
            
            logger.info(json.dumps({
                'event': 'dynamodb_write_success',
                'item_id': default_id,
            }))
            
            message = "Successfully inserted data!"
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": message}),
            }
    except Exception as e:
        logger.error(json.dumps({
            'event': 'error',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'request_id': context.request_id,
        }))
        raise
