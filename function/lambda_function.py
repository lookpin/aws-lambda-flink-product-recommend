

def lambda_handler(event, context):
    # return {'event': event, 'context': context}
    id = event['params']['path'].get('id', 0)  # coordi_id, product_id,
    recommend_type = event['params']['querystring'].get('recommendType', None)
    ids = event['params']['querystring'].get('ids', None)
    result = None
    statusCode = 200

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
