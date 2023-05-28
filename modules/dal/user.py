from functools import reduce
import json
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
from pypika import Query, Table, Field
import psycopg2
import psycopg2.extras


def format_not_in(values):
    return ','.join('%s' for _ in values)


class UserDal:
    def __init__(self, postgres, logger) -> None:
        self.postgres = postgres
        self.logger = logger

    async def get_user_by_id(self, user_id: int):
        try:
            query = Query\
                .from_(Table('users'))\
                .select('gender', 'id', 'address')\
                .where(Field('id') == user_id)\
                .get_sql(quote_char=None)

            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchone()
            self.cursor.close()
            return result

        except Exception as e:
            print(e)

    async def get_all_descriptions_and_lvl_3_ids(self):
        try:
            table = Table('categories')
            query = Query\
                .from_(table)\
                .select('id', 'description')\
                .where(~table.description.isnull())\
                .get_sql(quote_char=None)
            
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.postgres.commit()
            return result
        except Exception as e:
            self.logger.error(e)

    async def save_tags(self, id, tags):
        try:
            cursor = self.postgres.cursor()
            cursor.setinputsizes(psycopg2.extensions.AsIs)
            tags_str = Json(tags)

            query = "UPDATE categories SET tags = %s WHERE id = %s"
            cursor.execute(query, (tags_str, id))
            cursor.close()
            self.postgres.commit()
            return True
        except Exception as e:
            self.logger.error(e)

    async def get_user_visits_by_id(self, id):
        try:
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = "SELECT DISTINCT v.category_id, c.description ,c.name, c.tags\
                    FROM visits v join categories c on v.category_id = c.id\
                    WHERE user_id={}".format(id)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.postgres.commit()
            return result
        except Exception as e:
            self.logger.error(e)

    async def get_categories_based_on_labels(self, tags, exluded_ids):

        try:
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.setinputsizes(psycopg2.extensions.AsIs)

            query = '''
                SELECT *
                FROM categories
                WHERE tags ?| %s
                AND id NOT IN ({})
            '''.format(format_not_in(exluded_ids))
                # AND is_online = false

            cursor.execute(query, (tags, *exluded_ids))
            result = cursor.fetchall()
            cursor.close()
            self.postgres.commit()
            return result
        except Exception as e:
            self.logger.error(e)

    async def get_categories_based_on_labels_no_exclude(self, tags):
        try:
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.setinputsizes(psycopg2.extensions.AsIs)

            query = '''
                SELECT *
                FROM categories
                WHERE tags ?| %s
            '''
                # AND is_online = false

            cursor.execute(query, (tags,))
            result = cursor.fetchall()
            cursor.close()
            self.postgres.commit()
            return result
        except Exception as e:
            self.logger.error(e)

    async def get_all_users_cursor(self):
        try:
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.setinputsizes(psycopg2.extensions.AsIs)
            
            query = '''
                SELECT id
                FROM users
            '''

            cursor.execute(query)
            return cursor

        except Exception as e:
            self.logger.error(e)
            return


    async def check_constarint_tags(self, ids):
        CONTSTRAINTS = ["TOUR", "NEWCAREER"]
        includes = []
        to_add = []
        try:
            cursor = self.postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.setinputsizes(psycopg2.extensions.AsIs)

            query = '''
                SELECT *
                FROM categories
                WHERE tags ?| %s
                AND id IN ({})
            '''.format(format_not_in(ids))

            cursor.execute(query, (CONTSTRAINTS, *ids))
            result = cursor.fetchall()

            for item in result:
                tags = item.get('tags')
                for tag in CONTSTRAINTS:
                    if tag in tags:
                        includes.append(tag)

            includes=list(set(includes))
            if len(includes) == len(CONTSTRAINTS):
                return []
            
            not_includes = list(set(CONTSTRAINTS) - set(includes))

            for tag in not_includes:
                query = '''
                    SELECT *
                    FROM categories
                    WHERE tags ?| %s
                    ORDER BY RANDOM()
                    LIMIT 1
                    '''

                if len(to_add):
                    query = '''
                        SELECT *
                        FROM categories
                        WHERE tags ?| %s
                        AND id NOT IN ({})
                        ORDER BY RANDOM()
                        LIMIT 1
                    '''.format(format_not_in(to_add))

                    cursor.execute(query, (not_includes, *to_add))
                else:
                    cursor.execute(query, (not_includes,))

                res = cursor.fetchall()
                to_add.append(res[0].get('id'))
            
            cursor.close()
            self.postgres.commit()
            return to_add
        except Exception as e:
            self.logger.error(e)

def create(postgres, logger):
    dal = UserDal(postgres, logger)
    return dal
 
