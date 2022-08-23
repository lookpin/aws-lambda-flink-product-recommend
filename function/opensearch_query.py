def query_kmeans_feature_model(vector_feature, k, unique_key, product_list):
    return {
        "query": {
            "knn": {
                "model_factor": {
                    "vector": vector_feature,
                    "k": k
                }
            }
        },
        "post_filter": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "unique_key": unique_key
                        }
                    }
                ],
                "must_not": [
                    {
                        "terms": {
                            "product_id": product_list
                        }
                    }
                ]
            }
        },
        "_source": {
            "includes": ["product_id", "division2", "model_factor", "model_version", "model_timestamp"]
        }
    }


def query_kmeans_feature_models(vector_feature_list, unique_key_list, product_list):
    return {
        "query": {
            "bool": {
                "should": vector_feature_list
            }
        },
        "post_filter": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "unique_key": unique_key_list
                        }
                    }
                ],
                "must_not": [
                    {
                        "terms": {
                            "id": product_list
                        }
                    }
                ]
            }
        },
        "_source": {
            "includes": ["id", "division2", "model_factor", "model_version", "model_timestamp"]
        }
    }


def query_filter_product_id(product_list):
    return {
        "query": {
            "terms": {
                "id": product_list
            }
        },
        "sort": [
            {"avg_satisfaction": "desc"}
        ],
        "_source": ["id", "model_factor", "division2", "division1", "avg_satisfaction"]
    }


def query_knn_feature_model(vector_feature_list, product_list):
    return {
        "query": {
            "bool": {
                "should": vector_feature_list
            }
        },
        "post_filter": {
            "bool": {
                "must_not": [
                    {
                        "terms": {
                            "id": product_list
                        }
                    }
                ]
            }
        },
        "_source": {
            "includes": ["id", "division2", "model_factor", "model_version", "model_timestamp"]
        }
    }


def get_vector_factor(vector, k):
    return {
        "function_score": {
            "query": {
                "knn": {
                    "model_factor": {
                        "vector": vector,
                        "k": k
                    }
                }
            }
        }
    }

# {
#   "query": {
#     "knn": {
#       "model_factor": {
#         "vector": [
#           0.011345541401273885,
#           0.00006634819532908705,
#           0.988588110403397
#         ],
#         "k": 3
#       }
#     }
#   },
#   "post_filter": {
#     "bool": {
#       "must": [
#         {
#           "term": {
#             "unique_key": 171
#           }
#         }
#       ],
#       "must_not": [
#         {
#           "terms": {
#             "product_id": [
#               1972392
#             ]
#           }
#         }
#       ]
#     }
#   }
# }
