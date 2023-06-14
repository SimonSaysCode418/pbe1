import json
import os

import fiona
import numpy
import pandas as pd
import geojson
from geopy.distance import geodesic
from geopy.util import pairwise
from pandas import DataFrame
from shapely import to_geojson, LineString
from shapely.geometry import Point

from database.postgresql import DataBaseService
from models.raw.building.RawBuildingAddress import RawBuildingAddress
from models.raw.building.RawBuildingHeight import RawBuildingHeight
from models.raw.building.RawBuildingThermosData import RawBuildingThermosData
from models.raw.pipe.PipePathRaw import RawPipePath
from models.raw.pipe.PipePointRaw import RawPipePoint
from repositories.RawDataRepository import RawDataRepository


class RawDataService:

    def __init__(self):
        self.dbs = DataBaseService()
        self.rdr = RawDataRepository(self.dbs)

    def __del__(self):
        del self.dbs
        del self.rdr

    def initializeDB(self):
        self.rdr.initialize()

    def import_building_data(self):
        dataset = pd.read_json(os.getcwd() + '\\resources\\buildings.json')
        elements = dataset['features']

        buildings = [element for element in elements if element['geometry']['type'] == 'Polygon']

        for building in buildings:
            coordinates_raw = building['geometry']['coordinates'][0]
            coordinates = numpy.sum(coordinates_raw, axis=0) / len(coordinates_raw)

            self.rdr.set_raw_data(RawBuildingThermosData(
                building['properties']['candidate/user-fields Category'],
                float("{:.8f}".format(coordinates[0])),
                float("{:.8f}".format(coordinates[1])),
                building['properties']['cooling/kwp'],
                building['properties']['demand/kwp'],
                building['properties']['cooling/kwh'],
                building['properties']['demand/kwh'],
                building['properties']['candidate/ground-area'],
                building['properties']['candidate/wall-area'],
                building['geometry']
            ))

    def import_address_data(self):
        with fiona.open(
                os.getcwd() + '\\resources\\Adressen.gpkg') as layer:
            for obj in layer:
                coordinates_raw = obj['geometry']['coordinates'][0][0]
                coordinates = numpy.sum(coordinates_raw, axis=0) / len(coordinates_raw)

                geometry = {'type': obj['geometry']['type'], 'coordinates': obj['geometry']['coordinates']}

                self.rdr.set_raw_data(RawBuildingAddress(
                    float("{:.8f}".format(coordinates[0])),
                    float("{:.8f}".format(coordinates[1])),
                    obj['properties']['addr:street'],
                    obj['properties']['addr:housenumber'],
                    obj['properties']['addr:postcode'],
                    obj['properties']['addr:city'],
                    geometry
                ))

    def import_height_data(self):
        dataset = pd.read_json(os.getcwd() + '\\resources\\onegeo.json')
        elements = dataset['features']

        for height_obj in elements:
            coordinates_raw = height_obj['geometry']['coordinates'][0]
            coordinates = numpy.sum(coordinates_raw, axis=0) / len(coordinates_raw)

            self.rdr.set_raw_data(RawBuildingHeight(
                float("{:.8f}".format(coordinates[0])),
                float("{:.8f}".format(coordinates[1])),
                height_obj['properties'].get('height'),
                height_obj['properties'].get('roofShape'),
                height_obj['geometry']
            ))

    def import_pipe_data(self):
        with open(os.getcwd() + '\\resources\\Rohrleitungen.geojson') as f:
            dataset = geojson.load(f)
        elements = dataset['features']

        sorted_elements = list(filter(
            lambda x: x['properties']['candidate/user-fields Category'] == 'Connector' or x['properties'][
                'candidate/user-fields Category'] == 'Source', elements))
        sorted_elements.sort(
            key=lambda o: o['properties']['candidate/user-fields Category'], reverse=False)
        sorted_elements.extend(list(filter(
            lambda x: x['properties']['candidate/user-fields Category'] != 'Connector' or x['properties'][
                'candidate/user-fields Category'] != 'Source', elements)))

        pipe_points = []
        pipe_paths = []

        for pipe_obj in sorted_elements:
            coordinates = pipe_obj['geometry']['coordinates']
            length = 0
            for (current, next_val) in pairwise(coordinates):
                length = length + geodesic((current[1], current[0]), (next_val[1], next_val[0])).m

            path_object = RawPipePath(length, json.loads(to_geojson(LineString(coordinates))))
            path_object.id = len(pipe_paths)

            for i in range(2):
                start_end_coordinate = coordinates[len(coordinates) * i - i]
                point_geo = Point(start_end_coordinate)

                if (len(pipe_points) == 0) | (not any(
                        point.geometry == point_geo for point in pipe_points)):
                    name = pipe_obj['properties']['candidate/user-fields Category']
                    if i == 0 and name == 'Connector':
                        name = 'Pre' + name
                    if i == 0 and name == 'Source' or name == 'Path':
                        name = 'Crossing'

                    pipe_point = RawPipePoint(name, point_geo)
                    pipe_point.id = len(pipe_points)
                    pipe_points.append(pipe_point)

                point = next((x for x in pipe_points if x.geometry == point_geo))
                if i == 0:
                    # path_object.start_point_obj = point
                    path_object.startPointId = point.id
                else:
                    # path_object.end_point_obj = point
                    path_object.endPointId = point.id

            pipe_paths.append(path_object)

        # pipe_paths = [delattr(path, 'start_point_obj') or path for path in pipe_paths]
        # pipe_paths = [delattr(path, 'end_point_obj') or path for path in pipe_paths]

        [self.rdr.set_raw_data(path) for path in pipe_paths]
        [self.rdr.set_raw_data(point) for point in pipe_points]

    def get_raw_building_data(self):
        raw_building_data = DataFrame.from_records(vars(o) for o in self.rdr.raw_building_data)
        raw_address_data = DataFrame.from_records(vars(o) for o in self.rdr.raw_address_data)
        raw_height_data = DataFrame.from_records(vars(o) for o in self.rdr.raw_height_data)

        return {'raw_building_data': raw_building_data,
                'raw_address_data': raw_address_data,
                'raw_height_data': raw_height_data}

    def import_data(self):
        self.dbs.create_raw_tables()

        self.import_building_data()
        self.import_address_data()
        self.import_height_data()

        self.import_pipe_data()

        self.rdr.persist()

    def get_raw_pipe_path_data(self):
        return DataFrame.from_records(vars(o) for o in self.rdr.raw_pipe_path_data)

    def get_raw_pipe_point_data(self):
        return DataFrame.from_records(vars(o) for o in self.rdr.raw_pipe_point_data)
