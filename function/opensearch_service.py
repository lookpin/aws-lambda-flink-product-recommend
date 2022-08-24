import json
import os
import boto3
import requests

from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from requests.structures import CaseInsensitiveDict

# headers = CaseInsensitiveDict()
# headers["Connection"] = "keep-alive"
# headers["Keep-Alive"] = "timeout=5, max=2"


class OpensearchService:

    def __init__(self):
        region = os.environ.get('AWS_REGION', 'test')
        self.host = os.environ.get('OPENSEARCH_ENDPOINT', 'test')
        credentials = boto3.Session().get_credentials()
        self.auth = AWSV4SignerAuth(credentials, region)
        self.headers = CaseInsensitiveDict()
        self.headers["Connection"] = "keep-alive"
        self.headers["Keep-Alive"] = "timeout=3, max=2"
        self.headers["Content-Type"] = "application/json"

        # self.client = OpenSearch(
        #     hosts=[{'host': self.host, 'port': 443}],
        #     http_auth=self.auth,
        #     use_ssl=True,
        #     verify_certs=True,
        #     connection_class=RequestsHttpConnection,
        #     timeout=3,
        #     max_retries=2,
        #     retry_on_timeout=True
        # )
        # print('OpenSearch client :', self.client)
        # print('self.client.ping() :', self.client.ping())

    # def search(self, index_name, query):
    #     print(query)
    #     print(index_name)
    #     response = None
    #     try:
    #         response = self.client.search(body=query, index=index_name)
    #     except Exception as e:
    #         print(e)
    #         print('ElasticSearch client connection issue')
    #         # self.client.close()
    #         raise e
    #     return response

    def search(self, index_name, query):
        url = 'https://' + self.host + ':443' + '/' + index_name + '/_search'
        print(url)
        # Make the signed HTTP request
        r = requests.get(url, auth=self.auth, headers=self.headers, data=json.dumps(query))
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*'
            },
            "isBase64Encoded": False
        }

        # Add the search results to the response
        response['body'] = r.text
        json_dict = json.loads(response.get('body'))
        print(json_dict)
        return json_dict

    def ping(self):
        return self.client.ping()
