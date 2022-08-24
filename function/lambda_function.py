import json

from opensearch_service import OpensearchService
from realtime_recommend_service import RealTimeRecommendService

realtime_service = None
opensearch = None

def init():
    realtime_service = RealTimeRecommendService()
    opensearch = OpensearchService()
    realtime_service.set_opensearch_service(opensearch)

init()

def lambda_handler(event, context):
    print(event)
    result = None
    userType = event['queryStringParameters'].get('userType', None)
    userId = event['queryStringParameters'].get('userId', None)
    result = realtime_service.get_recommend_realtime_with_item(userType, userId)

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
