import json
import os
import boto3
import requests

from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


class OpensearchService:

    def __init__(self):
        region = os.environ.get('AWS_REGION', 'test')
        self.host = os.environ.get('OPENSEARCH_ENDPOINT', 'test')
        credentials = boto3.Session().get_credentials()
        self.auth = AWSV4SignerAuth(credentials, region)
        self.headers = {"Content-Type": "application/json"}
        # self.client = OpenSearch(
        #     hosts=[{'host': self.host, 'port': 443}],
        #     http_auth=self.auth,
        #     use_ssl=True,
        #     verify_certs=True,
        #     connection_class=RequestsHttpConnection,
        #     timeout=30,
        #     max_retries=10,
        #     retry_on_timeout=True
        # )
        print('OpenSearch client :', self.client)

    def test_search(self, index_name, query):
        print(query)
        print(index_name)
        response = None
        try:
            response = self.client.search(body=query, index=index_name)
        except Exception as e:
            print(e)
            print('ElasticSearch client connection issue')
            self.client.close()
            raise e
        return response

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
        return json.loads(response.get('body'))

    def ping(self):
        return self.client.ping()
