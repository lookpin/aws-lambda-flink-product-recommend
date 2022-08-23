from opensearch_service import OpensearchService
from realtime_recommend_service import RealTimeRecommendService
realtime_service = RealTimeRecommendService()

opensearch = OpensearchService()
realtime_service.set_opensearch_service(opensearch)

def lambda_handler(event, context):
    # return {'event': event, 'context': context}
    id = event['params']['path'].get('id', 0)  # coordi_id, product_id,
    recommend_type = event['params']['querystring'].get('recommendType', None)
    ids = event['params']['querystring'].get('ids', None)
    result = None
    statusCode = 200

    print(event)
    id = event['params']['path'].get('id', 0)  # coordi_id, product_id,
    recommend_type = event['params']['querystring'].get('recommendType', None)
    ids = event['params']['querystring'].get('ids', None)
    userType = event['params']['querystring'].get('userType', None)
    userId = event['params']['querystring'].get('userId', None)
    result = None
    statusCode = 200
    params = {'recommend_type': recommend_type, 'id': id, 'ids': ids, 'user_type': userType, 'user_id': userId}
    result = realtime_service.get_recommend_realtime_with_item(params.get('user_type'), params.get('user_id'))
    return result



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
