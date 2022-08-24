import json
from redis import Redis


class RedisService:

    def __init__(self, host, port):
        try:
            self.redis = Redis(host=host, port=port, charset="utf-8", decode_responses=True)
        except BaseException as e:
            print(e)

    def ping(self):
        return self.redis.ping()

    def get_json(self, key):
        json_string = self.redis.get(key)
        if json_string is None:
            return None
        else:
            return json.loads(json_string)

    def get(self, key):
        return '2022-08-16'
        # return self.redis.get(key)

    def zrevrange(self, key, size):
        return self.redis.zrevrange(key, 0, size, withscores=True)

    def zrevrange_between_timestamp(self, key, start_timestamp, end_timestamp):
        print('start_timestamp :', start_timestamp)
        print('start_timestamp :', end_timestamp)
        return self.redis.zrangebyscore(key, start_timestamp, end_timestamp, withscores=True)
