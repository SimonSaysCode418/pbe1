import copy

import psycopg2
from shapely import to_geojson

from database.create_tables import create_raw_tables
from database.create_tables import create_building_tables
from database.create_tables import create_pipe_tables


class DataBaseService:
    def __init__(self):
        self.connection = psycopg2.connect(user="pbe1",
                                           password="FH2023Aachen!",
                                           host="85.215.240.105",
                                           port="5432",
                                           database="miesheimer_weg_neu")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()
        self.cursor.close()

    def write_data_to_database(self, table, columns, data: list):
        for row in data:
            insert_item = copy.deepcopy(row)
            if hasattr(insert_item, 'geometry'):
                insert_item.geometry = to_geojson(insert_item.geometry)
            try:
                column_names = ', '.join("\"{c}\"".format(c=c) for c in columns)
                placeholder = ', '.join("%s" for _ in columns)

                query = """INSERT INTO {table_name} ({column_names}) VALUES ({values}) ON CONFLICT DO NOTHING""".format(
                    table_name=table,
                    column_names=column_names,
                    values=placeholder
                )
                if not isinstance(row, int):
                    self.cursor.execute(query, tuple(insert_item.__dict__.values()))
                else:
                    self.cursor.execute(query, (insert_item,))
            except Exception as e:
                print(e)
        return

    def create_raw_tables(self):
        create_raw_tables(self.cursor)

    def create_building_tables(self):
        create_building_tables(self.cursor)

    def create_pipe_tables(self):
        create_pipe_tables(self.cursor)

    def select_all_from(self, table):
        query = """SELECT * FROM {table_name}""".format(
            table_name=table
        )
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def delete_all_from(self, table):
        query = """TRUNCATE {table_name} CASCADE""".format(
            table_name=table
        )
        self.cursor.execute(query)