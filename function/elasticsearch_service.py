import json
import os
import boto3
from elasticsearch import helpers
import requests

# from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from elasticsearch import Elasticsearch
from requests.auth import HTTPBasicAuth


class ElasticsearchService():

    def __init__(self):
        self.host = os.environ.get('ES_HOST', 'test')
        self.password = os.environ.get('ES_PASSWORD', 'test')
        self.headers = {'content-type': 'application/json'}
        self.client = None
        self.set_client()

    def set_client(self):
        cloud_id = os.environ.get('CLOUD_ID', 'test')
        self.client = Elasticsearch(
            cloud_id=cloud_id,
            api_key=('oS6VtYIBdEw0LK8Ji-PA', 'mtOaHjqQRp6Wg3CtrJQKBg'),
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=1)

    def search(self, index_name, query):
        response = None
        try:
            # response = helpers.scan(index=index_name, client=self.client, query=query, request_timeout=10)
            response = self.client.search(body=query, index=index_name)

            print('search response :', response)
            # for i in response:
            #     print(i)
            # print('search response :', response)
        except Exception as e:
            print(e)
            print('ElasticSearch client connection issue')
            self.client.close()
            self.set_client()
            raise e
        return response

    # def search(self, index_name, query):
    #     print(self.host)
    #     url = self.host + '/' + index_name + '/_search'
    #     # Make the signed HTTP request
    #     session = requests.session()
    #     res = None
    #     try:
    #         r = session.get(url, auth=("elastic", self.password), headers=self.headers, data=json.dumps(query), timeout=30)
    #         response = {
    #             "statusCode": 200,
    #             "headers": {
    #                 "Access-Control-Allow-Origin": '*'
    #             },
    #             "isBase64Encoded": False
    #         }
    #
    #         # Add the search results to the response
    #         response['body'] = r.text
    #         res = json.loads(response.get('body'))
    #         print(res)
    #     except requests.exceptions.Timeout:
    #         print("timeout")
    #         session.close()
    #
    #     return res

    def ping(self):
        return self.client.ping()
