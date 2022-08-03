import os

import psycopg2


ENV = os.environ.get('ENV', 'test')

TABLE_ENV = ''

if ENV == 'staging':
    HOST = os.environ.get('STAGING_HOST', 'test')
    DB_NAME = os.environ.get('STAGING_DB_NAME', 'test')
    USER = os.environ.get('STAGING_USER', 'test')
    PASSWORD = os.environ.get('STAGING_PASSWORD', 'test')
else:
    HOST = os.environ.get('HOST', 'test')
    DB_NAME = os.environ.get('DB_NAME', 'test')
    USER = os.environ.get('USER', 'test')
    PASSWORD = os.environ.get('PASSWORD', 'test')


port = "5432"


class PsycopgClient:

    def __init__(self):
        try:
            self.connect = psycopg2.connect(user=USER,
                                            password=PASSWORD,
                                            host=HOST,
                                            port=port,
                                            database=DB_NAME)

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)

    def __del__(self):
        if self.connect:
            self.connect.close()
            print("PostgreSQL connection pool is closed")

    def get_data_from_query(self, query):
        response = None
        try:
            ps_cursor = self.connect.cursor()
            ps_cursor.execute(query)
            response = ps_cursor.fetchall()
            ps_cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            return response

    def convert_to_list_str(self, list):
        return '(' + ','.join(list) + ')'

    def get_product_category_query(self, product_id):
        return """
            select
              ppi.product_id as product_id
            , pc.division1
            , pc.division2
            from partner_product_infos ppi
                left join product_categories pc ON pc.id = ppi.category_id
            where ppi.product_id = {0}
        """.format(product_id)

    def get_products_category_query(self, product_id_list):
        str_list = self.convert_to_list_str(product_id_list)
        return """
            select
              ppi.product_id as product_id
            , pc.division1
            , pc.division2
            from partner_product_infos ppi
                left join product_categories pc ON pc.id = ppi.category_id
            where ppi.product_id in {0}
        """.format(str_list)

    def get_coordi_tags_query(self, coordi_id_list):
        str_list = self.convert_to_list_str(coordi_id_list)
        return """
            select
              coordination_id
            , coordination_tag_id
            from coordination_tags_coordinations
            where coordination_id in {0}
            order by coordination_id desc
        """.format(str_list)

    def get_coordi_unique_tags_query(self, coordi_id_list):
        str_list = self.convert_to_list_str(coordi_id_list)
        return """
            select
              coordination_id
            , coordination_unique_tag_id
            from coordination_unique_tags_coordinations
            where coordination_id in {0}
            order by coordination_id desc
        """.format(str_list)