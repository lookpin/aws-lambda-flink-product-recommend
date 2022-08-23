import datetime
import os
import time

from redis_service import RedisService
from opensearch_service import OpensearchService
from opensearch_query import query_filter_product_id, query_kmeans_feature_model, query_knn_feature_model, \
    query_kmeans_feature_models, get_vector_factor

RECENT_ACTION_ENDPOINT = os.environ.get('RECENT_ACTION_ENDPOINT', 'test')
RECENT_ACTION_ENDPOINT_PORT = os.environ.get('RECENT_ACTION_ENDPOINT_PORT', 'test')

RECENT_PRODUCT_CACHE_ENDPOINT = os.environ.get('RECENT_PRODUCT_CACHE_ENDPOINT', 'test')
RECENT_PRODUCT_CACHE_PORT = os.environ.get('RECENT_PRODUCT_CACHE_PORT', 'test')

RECENT_PRODUCT_CACHE_PREVIOUS_DAY = int(os.environ.get('RECENT_PRODUCT_CACHE_PREVIOUS_DAY', 7))

KST = datetime.timezone(datetime.timedelta(hours=9))


class RealTimeRecommendService():

    def __init__(self):
        super().__init__()
        print('init RealTimeRecommendService')
        self.index_cache = RedisService('flink-agg-prod.xa2joo.ng.0001.apn2.cache.amazonaws.com', 6379)
        self.recent_user_action_cache = RedisService(RECENT_ACTION_ENDPOINT, RECENT_ACTION_ENDPOINT_PORT)
        self.recent_view_product_cache = RedisService(RECENT_PRODUCT_CACHE_ENDPOINT, RECENT_PRODUCT_CACHE_PORT)
        self.duplicate_check_dict = {}
        self.recommend_product_list = []
        self.opensearch_service = None

    def set_opensearch_service(self, opensearch_service):
        self.opensearch_service = opensearch_service

    def get_recommend_item_list(self, product_id, recommend_type):
        return []

    def get_recommend_realtime_with_item(self, user_type, user_id):
        # user 최근 action_조회
        self.__clear_data()
        recent_product_list = self.__get_recent_view_product_list(user_id, user_type)

        if len(recent_product_list) > 0:
            print('recent_product_list')
            key = self.__get_recent_action_key(user_type, user_id)
            recent_action = self.recent_user_action_cache.get_json(key)
            if recent_action is not None:
                kmeans_response = self.get_kmeans_response(recent_action, recent_product_list)
                self.__set_response_product_list('product_id', kmeans_response)

            knn_index = self.__get_knn_index(self.index_cache.get('knn-review-index'))
            search_knn_product_model_response = self.get_recent_view_knn_model_product(knn_index, recent_product_list)
            print('search_knn_product_model_response :', search_knn_product_model_response)

            search_vector_feature_list = self.__search_knn_vector_feature_list(search_knn_product_model_response)
            print('search_vector_feature_list :', search_vector_feature_list)
            knn_response = self.__get_recommend_knn_model_response(knn_index, search_vector_feature_list,
                                                                   recent_product_list)
            print('knn_response :', knn_response)
            self.__set_response_product_list('id', knn_response)
        print('recommend_product_list finally : ', self.recommend_product_list)
        return self.recommend_product_list

    def __clear_data(self):
        self.recommend_product_list.clear()
        self.duplicate_check_dict.clear()

    def get_kmeans_response(self, recent_action, recent_product_list):
        response = None
        if recent_action is None:
            print('recent_action :', recent_action)

        if recent_action is not None:
            kmeans_cluster_index_date = self.index_cache.get('kmeans-cluster-index')
            print('kmeans_cluster_index_date :', kmeans_cluster_index_date)
            action_list = recent_action.get('action_list', [])

            if len(action_list) == 1:
                query = query_kmeans_feature_model(action_list[0].get('model_feature'), 3,
                                                   action_list[0].get('unique_division'),
                                                   recent_product_list)
                response = self.__get_opensearch_kmeans_response(kmeans_cluster_index_date, query)
            elif len(action_list) > 1:
                print('len(action_list) > 1')
                sort_view_count_action = self.__sort_view_count_and_timestamp(action_list)
                sort_event_time_action = self.__sort_timestamp(action_list)
                if kmeans_cluster_index_date is not None:
                    response = self.get_kmeans_response_by_event_time_and_view_count(kmeans_cluster_index_date,
                                                                                     sort_event_time_action,
                                                                                     sort_view_count_action,
                                                                                     recent_product_list)

        return response

    def __get_recent_action_key(self, user_type, user_id):
        return user_type.lower() + ":" + str(user_id)

    def __sort_view_count_and_timestamp(self, action_list):
        sort_list = sorted(action_list,
                           key=lambda x: (x['division_view_count'], x['start_event_time']),
                           reverse=True)
        return sort_list[0]

    def __sort_timestamp(self, action_list):
        sort_list = sorted(action_list, key=lambda x: x['start_event_time'], reverse=True)
        return sort_list[0]

    def get_kmeans_response_by_event_time_and_view_count(self, kmeans_cluster_index_date, event_time_action_value,
                                                         view_count_action_value, recent_product_list):
        if event_time_action_value is view_count_action_value:
            query = query_kmeans_feature_model(event_time_action_value.get('model_feature'), 3,
                                               event_time_action_value.get('unique_division'),
                                               recent_product_list)
            response = self.__get_opensearch_kmeans_response(kmeans_cluster_index_date, query)
            return response
        else:
            vector_feature_list = []
            unique_key_list = []
            self.__set_kmeans_multi_vector(event_time_action_value, unique_key_list, vector_feature_list)
            self.__set_kmeans_multi_vector(view_count_action_value, unique_key_list, vector_feature_list)

            query = query_kmeans_feature_models(vector_feature_list, unique_key_list,
                                                recent_product_list)

            response = self.__get_opensearch_kmeans_response(kmeans_cluster_index_date, query)
            return response

    def __get_opensearch_kmeans_response(self, index_current_date, query):
        index = self.__get_kmeans_multi_index(index_current_date)
        return self.opensearch_service.search(index, query)

    def __set_kmeans_multi_vector(self, action_value, unique_key_list, vector_feature_list):
        vector_feature_list.append(get_vector_factor(action_value.get('model_feature'), 3))
        unique_key_list.append(action_value.get('unique_division'))

    def __get_kmeans_multi_index(self, date):
        return 'kmeans-like-{date},kmeans-purchase-{date}'.format(date=date)

    def get_recent_view_knn_model_product(self, index_date, search_list):
        response = None
        if index_date is None:
            print('index_date is ', index_date)

        if index_date is not None:
            if len(search_list) > 0:
                response = self.__get_opensearch_knn_response(index_date,
                                                              query_filter_product_id(search_list))

        return response

    def __get_recent_view_product_list(self, user_id, user_type):

        print('recent_view_product')
        key = self.__get_recent_view_product_action_key(user_type, user_id)
        recent_view_product = self.recent_view_product_cache. \
            zrevrange_between_timestamp(key, self.__get_previous_timestamp(RECENT_PRODUCT_CACHE_PREVIOUS_DAY), self.__get_current_timestamp())

        print(recent_view_product)
        search_list = []
        for view_product in recent_view_product:
            search_list.append(int(view_product[0]))

        return search_list

    def __get_recent_view_product_action_key(self, user_type, user_id):
        return user_type.lower() + ":" + str(user_id) + ":recent_products"

    def __get_current_timestamp(self):
        return datetime.datetime.now(KST).strftime('%Y%m%d%H%M%S')

    def __get_previous_timestamp(self, days):
        previous_date = datetime.datetime.now(KST) - datetime.timedelta(days=days)
        return previous_date.strftime('%Y%m%d%H%M%S')

    def __get_opensearch_knn_response(self, index, query):
        return self.opensearch_service.search(index,
                                              query)

    def __get_knn_index(self, date):
        return 'knn-recommend-rating-products-{date}'.format(date=date)

    def __search_knn_vector_feature_list(self, knn_product_knn_model_factor_response):
        vector_feature_list = []
        k = 30
        for response in knn_product_knn_model_factor_response['hits']['hits']:
            vector_feature_list.append(get_vector_factor(response['_source']['model_factor'], k))

        return vector_feature_list



    def __get_recommend_knn_model_response(self, index, vector_feature_list, exclude_product_list):
        return self.__get_opensearch_knn_response(index,
                                                  query_knn_feature_model(vector_feature_list, exclude_product_list))

    def __set_response_product_list(self, key_str, response):
        print(response)
        print("response['hits']: ", response['hits'])
        if response is not None:
            for res in response['hits']['hits']:
                print('__set_response_product_list: {0} key_str: {1}'.format(res, key_str))
                id = res['_source'][key_str]
                print('id : {0}'.format(id))
                if self.duplicate_check_dict.get(id) is None:
                    self.recommend_product_list.append(self.__get_recommend_product_model_info(id, res))
                print('self.recommend_product_list : ', self.recommend_product_list)

    def __get_recommend_product_model_info(self, id, response):
        self.duplicate_check_dict[id] = id
        product_model_info = {'product_id': id,
                              'model_version': response['_source']['model_version'],
                              'model_timestamp': response['_source']['model_timestamp']}
        return product_model_info

    #
    #
    # def __set_recommend_product_format(self, recommend_product_id, movel_version, model_timestamp):
