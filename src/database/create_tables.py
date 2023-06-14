def create_raw_tables(cursor):
    create_raw_address(cursor)
    create_raw_building(cursor)
    create_raw_height(cursor)
    create_raw_pipe_point(cursor)
    create_raw_pipe_path(cursor)

def create_building_tables(cursor):
    create_building(cursor)

def create_pipe_tables(cursor):
    create_pipe_point(cursor)
    create_pipe_path(cursor)
    shortest_path_connector(cursor)


def create_raw_address(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.raw_address;
        CREATE TABLE IF NOT EXISTS public.raw_address
        (
            "id" serial PRIMARY KEY,
            "coordinateX" numeric NOT NULL,
            "coordinateY" numeric NOT NULL,
            "street" character varying COLLATE pg_catalog."default",
            "housenumber" character varying COLLATE pg_catalog."default" NOT NULL,
            "postcode" numeric,
            "city" character varying COLLATE pg_catalog."default",
            "geometry" geometry,
            CONSTRAINT unique_raw_address UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.raw_address
        OWNER to pbe1;
    ''')


def create_raw_building(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.raw_building;
        CREATE TABLE IF NOT EXISTS public.raw_building
        (
            "id" serial PRIMARY KEY,
            "type" character varying COLLATE pg_catalog."default" NOT NULL,
            "coordinateX" numeric NOT NULL,
            "coordinateY" numeric NOT NULL,
            "kwpCooling" numeric NOT NULL,
            "kwpDemand" numeric NOT NULL,
            "kwhCooling" numeric NOT NULL,
            "kwhDemand" numeric NOT NULL,
            "groundArea" numeric NOT NULL,
            "wallArea" numeric NOT NULL,
            "geometry" geometry,
            CONSTRAINT unique_raw_building UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.raw_building
            OWNER to pbe1;  
    ''')


def create_raw_height(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.raw_height;
        CREATE TABLE IF NOT EXISTS public.raw_height
        (
            "id" serial PRIMARY KEY,
            "coordinateX" numeric NOT NULL,
            "coordinateY" numeric NOT NULL,
            "height" numeric,
            "roof" character varying COLLATE pg_catalog."default",
            "geometry" geometry,
            CONSTRAINT unique_raw_height UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.raw_height
            OWNER to pbe1;  
    ''')


def create_building(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.building CASCADE;
        CREATE TABLE IF NOT EXISTS public.building
        (
            "id" serial PRIMARY KEY,
            "street" character varying COLLATE pg_catalog."default" NOT NULL,
            "housenumber" character varying COLLATE pg_catalog."default" NOT NULL,
            "postcode" numeric NOT NULL,
            "city" character varying COLLATE pg_catalog."default" NOT NULL,
            "type" character varying COLLATE pg_catalog."default" NOT NULL,
            "yearOfConstruction" numeric NOT NULL,
            "groupname" character varying COLLATE pg_catalog."default" NOT NULL,
            "roof" character varying COLLATE pg_catalog."default" NOT NULL,
            "floors" numeric NOT NULL,
            "groundArea" numeric NOT NULL,
            "energyReferenceArea" numeric NOT NULL,
            "livingArea" numeric NOT NULL,
            "wallAreaPerFloor" numeric NOT NULL,
            "wallArea" numeric NOT NULL,
            "roofArea" numeric NOT NULL,
            "surface" numeric NOT NULL,
            "volumeLivingArea" numeric NOT NULL,
            "transmissionSurface" numeric NOT NULL,
            "transmission" numeric NOT NULL,
            "ventilationHeatLoss" numeric NOT NULL,
            "ventilationHeatLossComplex" numeric NOT NULL,
            "powerHeating" numeric NOT NULL,
            "powerHotWater" numeric NOT NULL,
            "demandHeating" numeric NOT NULL,
            "demandHotWater" numeric NOT NULL,
            "fullLoadHours" numeric NOT NULL,
            "geometry" geometry,
            CONSTRAINT unique_building UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.building
            OWNER to pbe1;  
    ''')


def create_raw_pipe_point(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.raw_pipe_point CASCADE;
        CREATE TABLE IF NOT EXISTS public.raw_pipe_point
        (
            "id" integer PRIMARY KEY,
            "type" character varying COLLATE pg_catalog."default" NOT NULL,
            "name" character varying COLLATE pg_catalog."default",
            "geometry" geometry,
            CONSTRAINT unique_raw_pipe_point UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.raw_pipe_point
            OWNER to pbe1;  
    ''')


def create_raw_pipe_path(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.raw_pipe_path CASCADE;
        CREATE TABLE IF NOT EXISTS public.raw_pipe_path
        (
            "id" integer PRIMARY KEY,
            "startPointId" integer REFERENCES PUBLIC.raw_pipe_point("id") NOT NULL,
            "endPointId" integer REFERENCES PUBLIC.raw_pipe_point("id") NOT NULL,
            "length" numeric NOT NULL,
            "geometry" geometry,
            CONSTRAINT unique_raw_pipe_path UNIQUE ("startPointId", "endPointId")
        );
        ALTER TABLE IF EXISTS public.raw_pipe_path
            OWNER to pbe1;  
    ''')


def create_pipe_point(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.pipe_point CASCADE;
        CREATE TABLE IF NOT EXISTS public.pipe_point
        (
            "id" integer PRIMARY KEY,
            "type" character varying COLLATE pg_catalog."default" NOT NULL,
            "name" character varying COLLATE pg_catalog."default",
            "powerHeatingW" numeric NOT NULL,
            "powerHotWaterW" numeric NOT NULL,
            "massFlowRate" numeric,
            "geometry" geometry,
            CONSTRAINT unique_pipe_point UNIQUE ("geometry")
        );
        ALTER TABLE IF EXISTS public.pipe_point
            OWNER to pbe1;  
    ''')


def create_pipe_path(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.pipe_path CASCADE;
        CREATE TABLE IF NOT EXISTS public.pipe_path
        (
            "id" integer PRIMARY KEY,
            "startPointId" integer REFERENCES PUBLIC.pipe_point("id") NOT NULL,
            "endPointId" integer REFERENCES PUBLIC.pipe_point("id") NOT NULL,
            "length" numeric NOT NULL,
            "massFlowRate" numeric NOT NULL,
            "initialPipeDiameterFlow" numeric NOT NULL,
            "initialPipeTypeFlow" character varying COLLATE pg_catalog."default" NOT NULL,
            "initialPipeNominalSizeFlow" numeric NOT NULL,
            "initialPipeInsulationFlow" character varying COLLATE pg_catalog."default" NOT NULL,
            "initialPipeDiameterReturn" numeric NOT NULL,
            "initialPipeTypeReturn" character varying COLLATE pg_catalog."default" NOT NULL,
            "initialPipeNominalSizeReturn" numeric NOT NULL,
            "initialPipeInsulationReturn" character varying COLLATE pg_catalog."default" NOT NULL,
            "pipeTypeFlow" character varying COLLATE pg_catalog."default" NOT NULL,
            "pipeNominalSizeFlow" numeric NOT NULL,
            "pipeInsulationFlow" character varying COLLATE pg_catalog."default" NOT NULL,
            "pipeDiameterFlow" numeric NOT NULL,
            "pipeFlowVelocityFlow" numeric NOT NULL,
            "pipeReynoldFlow" numeric NOT NULL,
            "pipeLambdaFlow" numeric NOT NULL,
            "pipePressureLossFlow" numeric NOT NULL,
            "pipeSpecificPressureLossFlow" numeric NOT NULL,
            "pipeTypeReturn" character varying COLLATE pg_catalog."default" NOT NULL,
            "pipeNominalSizeReturn" numeric NOT NULL,
            "pipeInsulationReturn" character varying COLLATE pg_catalog."default" NOT NULL,
            "pipeDiameterReturn" numeric NOT NULL,
            "pipeFlowVelocityReturn" numeric NOT NULL,
            "pipeReynoldReturn" numeric NOT NULL,
            "pipeLambdaReturn" numeric NOT NULL,
            "pipePressureLossReturn" numeric NOT NULL,
            "pipeSpecificPressureLossReturn" numeric NOT NULL,
            "pipeHeatLossWinter" numeric NOT NULL,
            "pipeSpecificHeatLossWinter" numeric NOT NULL,
            "pipeHeatLossSummer" numeric NOT NULL,
            "pipeSpecificHeatLossSummer" numeric NOT NULL,
            "geometry" geometry,
            CONSTRAINT unique_pipe_path UNIQUE ("startPointId", "endPointId")
        );
        ALTER TABLE IF EXISTS public.pipe_path
            OWNER to pbe1;  
    ''')


def shortest_path_connector(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS public.shortest_path_connector CASCADE;
        CREATE TABLE IF NOT EXISTS public.shortest_path_connector
        (
            "id" serial PRIMARY KEY,
            "pointId" integer REFERENCES PUBLIC.pipe_point("id") NOT NULL,
            "pathId" integer REFERENCES PUBLIC.pipe_path("id") NOT NULL,
            CONSTRAINT unique_shortest_path_connector UNIQUE ("pointId", "pathId")
        );
        ALTER TABLE IF EXISTS public.shortest_path_connector
            OWNER to pbe1;  
    ''')