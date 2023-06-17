DROP VIEW IF EXISTS "Gebäude";
CREATE VIEW "Gebäude" AS
SELECT "id"                         AS "ID",
       "street"                     AS "Straße",
       "housenumber"                AS "Hausnummer",
       "postcode"                   AS "PLZ",
       "city"                       AS "Ort",
       "type"                       AS "Gebäudetyp",
       "yearOfConstruction"         AS "Baujahr",
       "groupname"                  AS "Gebäudegruppe",
       "roof"                       AS "Dachform",
       "floors"                     AS "Etagen",
       ROUND("floorArea")           AS "Grundfläche (m²)",
       ROUND("energyReferenceArea") AS "Energiebezugsfläche (m²)",
       ROUND("livingArea")          AS "Beheizte Wohnfläche (m²)",
       ROUND("wallAreaPerFloor")    AS "Wandfläche je Etage (m²)",
       ROUND("wallArea")            AS "Wandfläche gesamt (m²)",
       ROUND("roofArea")            AS "Dachfläche (m²)",
       ROUND("surface")             AS "Hüllfläche (m²)",
       "volumeLivingArea"           AS "Volumen Wohnfläche (m³)",
       "transmissionSurface"        AS "Transmissionswärmeverlust Hüllfläche (W)",
       "transmission"               AS "Transmissionswärmeverlust (W)",
       "ventilationHeatLoss"        AS "Lüftungswärmeverlust (W)",
       "ventilationHeatLossComplex" AS "Lüftungswärmeverlust komplex (W)",
       "powerHeating"               AS "Leistungsbedarf Heizung (W)",
       "powerHotWater"              AS "Leistungsbedarf Warmwasser (W)",
       "demandHeating"              AS "Wärmebedarf Heizung (kWh/a)",
       "demandHotWater"             AS "Wärmebedarf Warmwasser (kWh/a)",
       "fullLoadHours"              AS "Volllaststunden",
       "geometry"
FROM building;

SELECT *
FROM "Gebäude";