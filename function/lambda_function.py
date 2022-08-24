import json
import os
import boto3

from opensearch_service import OpensearchService
from realtime_recommend_service import RealTimeRecommendService


from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
realtime_service = None
opensearch = None

def db_connection():
    region = os.environ.get('AWS_REGION', 'test')
    host = os.environ.get('OPENSEARCH_ENDPOINT', 'test')
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, region)
    # self.headers = CaseInsensitiveDict()
    # # self.headers["Connection"] = "keep-alive"
    # # self.headers["Keep-Alive"] = "timeout=5, max=4"
    # self.headers["Content-Type"] = "application/json"

    opensearch = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30,
        max_retries=10,
        retry_on_timeout=True
    )
    print('opensearch init():', opensearch.ping())
    # realtime_service = RealTimeRecommendService()
    # opensearch = OpensearchService()
    # realtime_service.set_opensearch_service(opensearch)

db_connection()

def lambda_handler(event, context):
    print('opensearch.ping():', opensearch.ping())
    # print(event)
    # result = None
    # userType = event['queryStringParameters'].get('userType', None)
    # userId = event['queryStringParameters'].get('userId', None)
    # result = realtime_service.get_recommend_realtime_with_item(userType, userId)
    result = []
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'recommend_list': result
        }),
        "isBase64Encoded": False
    }

#
#
#
# def get_response_error_code():
#     return {
#         "statusCode": 400,
#         "body": {"error": "missing_parameter",
#                  "error_message": "Missing parameter id or recommend_type or ids missing querystring parameter"}
#     }
#
#
# def get_response_ids_error_code():
#     return {
#         "statusCode": 400,
#         "body": {"error": "wrong ids parameter", "error_message": "ids querystring parameter error"}
#     }
