import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import json
import os

TABLE_ARTICLE='Articles'
KEY_ITEMS='Items'
LSI_NAME='UrlIndex'
epoch = datetime.utcfromtimestamp(0)


aws_region = os.environ.get('aws_region') or 'eu-central-1'
dynamo_endpoint_url =os.environ.get('dynamo_endpoint_url') or 'http://localhost:8000'

dynamodb = boto3.resource('dynamodb', region_name=aws_region, endpoint_url=dynamo_endpoint_url)
client  = boto3.client('dynamodb', region_name=aws_region, endpoint_url=dynamo_endpoint_url)

def gettable(): return dynamodb.Table(TABLE_ARTICLE)

def datetime_to_seconds(dt):
    return int((dt - epoch).total_seconds())

def seconds_to_datetime(s):
    return datetime.fromtimestamp(s)

def article_to_dict(article):
    i = article.__dict__
    # datetime need to be converted
    i['updated'] = datetime_to_seconds(article.updated)
    # url is a reserved keyword for dynamodb
    i['uurl']=i['url']
    del i['url']
    return i

def exists(url, scraper_name):
    try:
        response = client.query(
            TableName=TABLE_ARTICLE,
            IndexName=LSI_NAME,
            Select='ALL_PROJECTED_ATTRIBUTES',
            ConsistentRead=True,
            ReturnConsumedCapacity='INDEXES',
            ScanIndexForward=True,
            Limit=1,
            KeyConditionExpression='uurl = :uurl and scraper = :scraper',
            ExpressionAttributeValues={":uurl": {"S": url}, ":scraper":{"S": scraper_name}}
        )
        return KEY_ITEMS in response and len(response[KEY_ITEMS])>0
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False

def insert_all(article_list):
    inserted=0
    table = gettable()
    with table.batch_writer(overwrite_by_pkeys=['uurl']) as batch:
        for article in article_list:
            item = article_to_dict(article)
            batch.put_item(Item=item)
            inserted+=1
    return inserted


def insert(article):
    table = gettable()
    item = article_to_dict(article)
    response = table.put_item(Item=item)

def drop():
    gettable().delete()
    init()

def findRecent(scraperName, maxAgeInDays=7):
    table = gettable()
    
    s = datetime_to_seconds( datetime.now() - timedelta(maxAgeInDays) )
    try:
        response = table.query(
            IndexName=LSI_NAME,
            KeyConditionExpression=Key('scraper').eq(scraperName) & Key('updated').gte(s)
        )
        output=[]
        for item in response[KEY_ITEMS]:
            item['updated'] = seconds_to_datetime(item['updated'])
            item['url'] = item['uurl']
            del item['uurl']
            output.append( type("Article",(object,),item) )
        return output

    except ClientError as e:
        print(e.response['Error']['Message'])


def init():

    try:
        table = gettable()   
        print('dynamodb table "{}" already existing, status is "{}"'.format(TABLE_ARTICLE, table.table_status))
    except:
        print('dynamodb table "{}" not existing, creating it'.format(TABLE_ARTICLE))
        table = dynamodb.create_table(
            TableName=TABLE_ARTICLE,
            KeySchema=[
                {
                    'AttributeName': 'uurl',
                    'KeyType': 'HASH' 
                },
                {
                    'AttributeName': 'scraper',
                    'KeyType': 'RANGE' 
                }           
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': LSI_NAME,
                    'KeySchema': [
                        {
                            'AttributeName': 'scraper',
                            'KeyType': 'HASH' 
                        },
                        {
                            'AttributeName': 'updated',
                            'KeyType': 'RANGE' 
                        }     
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput':{
                        'ReadCapacityUnits' : int(os.environ.get('dynamo_gsi_read_capacity')) if os.environ.get('dynamo_gsi_read_capacity') else 1,
                        'WriteCapacityUnits': int(os.environ.get('dynamo_gsi_write_capacity')) if os.environ.get('dynamo_gsi_write_capacity') else 1
                    }
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'scraper',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'updated',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'uurl',
                    'AttributeType': 'S' 
                }    
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits' : int(os.environ.get('dynamo_read_capacity'))  or 1,
                'WriteCapacityUnits': int(os.environ.get('dynamo_write_capacity')) or 1
            }
        )
        print('table "{}" created, status is "{}"'.format(TABLE_ARTICLE, table.table_status))

