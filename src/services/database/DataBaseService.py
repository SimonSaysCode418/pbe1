import copy
import os

import psycopg2
import shapely
from shapely import to_geojson

PYTHON_TO_POSTGRESQL_TYPES = {
    int: 'INTEGER',
    float: 'NUMERIC',
    str: 'CHARACTER VARYING',
    bool: 'BOOLEAN',
    shapely.Polygon: 'GEOMETRY',
    shapely.Point: 'GEOMETRY',
    shapely.LineString: 'GEOMETRY',
}

CLASS_REFERENCES = {
    'RawBuildingAddress': 'raw_building_address',
    'RawBuildingHeight': 'raw_building_height',
    'RawBuildingThermosData': 'raw_building_thermos_data',
    'RawPoint': 'raw_point',
    'RawPipe': 'raw_pipe',
    'Building': 'building',
    'Pipe': 'pipe',
    'Point': 'point',
    'ShortestPathConnector': 'shortest_path_connector',
}


def get_sql_table_by_classname(name):
    return next((class_name for key, class_name in CLASS_REFERENCES.items()
                 if key == name), None)


class DataBaseService:
    def __init__(self):
        self.connection = psycopg2.connect(user="pbe1",
                                           password="FH2023Aachen!",
                                           host="85.215.240.105",
                                           port="5432",
                                           database="miesheimer_weg")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def write_data_to_database(self, data: list):
        if not data:
            return

        columns = data[0].__dict__.keys()
        table_name = get_sql_table_by_classname(type(data[0]).__name__)
        insert_items = []

        for row in data:
            insert_item = copy.deepcopy(row)
            if hasattr(insert_item, 'geometry'):
                insert_item.geometry = to_geojson(insert_item.geometry)
            if not isinstance(insert_item, int):
                insert_items.append(tuple(insert_item.__dict__.values()))
            else:
                insert_items.append((insert_item,))

        try:
            column_names = ', '.join("\"{c}\"".format(c=c) for c in columns)
            values = tuple(item for item in insert_items)

            placeholder = ','.join(['%s'] * len(columns))

            args_str = ','.join(self.cursor.mogrify("({})".format(placeholder), x).decode('utf-8') for x in values)

            query = "INSERT INTO {table_name} ({column_names}) VALUES {args_str} ON CONFLICT DO NOTHING".format(
                table_name=table_name,
                column_names=column_names,
                args_str=args_str
            )

            self.cursor.execute(query)
        except Exception as e:
            print(e)

        return

    def create_table_from_class(self, object_class):
        columns = []
        for attr_name, attr_type in object_class.__annotations__.items():
            if not attr_name.startswith("__"):
                if attr_name == 'id':
                    columns.append(f"\"{attr_name}\" SERIAL PRIMARY KEY")
                else:
                    reference_class = get_sql_table_by_classname(attr_name) if attr_name.endswith('Id') else None
                    postgresql_type = PYTHON_TO_POSTGRESQL_TYPES.get(attr_type, 'TEXT')
                    attribute_sql = f"\"{attr_name}\" {postgresql_type}"
                    attribute_sql += f" REFERENCES {reference_class} (\"id\")" if reference_class else " NOT NULL"
                    columns.append(attribute_sql)

        table_name = ''.join(['_' + char.lower() if char.isupper() else char for char in object_class.__name__]).lstrip(
            '_')
        create_table_query = f"CREATE TABLE {table_name} ({', '.join(columns)}"
        create_table_query += f", CONSTRAINT unique_{table_name} UNIQUE (geometry)" if 'geomerty' in columns else ""
        create_table_query += ")"

        delete_query = f"DROP TABLE IF EXISTS {table_name} CASCADE"

        self.cursor.execute(delete_query)
        self.cursor.execute(create_table_query)
        print(f"Die Tabelle '{table_name}' wurde erfolgreich erstellt.")

    def run_sql_file(self, file):
        self.cursor.execute(open(os.getcwd() + file, "r", encoding='utf-8').read())

    def select_all_from(self, object_class):
        query = f"""SELECT * FROM {get_sql_table_by_classname(object_class.__name__)}"""
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def delete_all_from(self, object_class):
        query = f"""TRUNCATE {get_sql_table_by_classname(object_class.__name__)} CASCADE"""
        self.cursor.execute(query)
