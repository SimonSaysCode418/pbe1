DROP VIEW IF EXISTS building_group_aggregation;
CREATE VIEW building_group_aggregation AS
SELECT CASE
           WHEN GROUPING(groupname) = 1
               THEN 'Gesamt'
           ELSE groupname
           END                                         AS "Gebäudegruppe",
       ROUND(SUM("demandHeatingWH") / 1000 / 1000, 2)  AS "Agg. Wärmebedarf Heizung (MWh/a)",
       ROUND(SUM("demandHotWaterWH") / 1000 / 1000, 2) AS "Agg. Wärmebedarf Warmwasser (MWh/a)",
       ROUND(SUM("powerHeatingW") / 1000, 2)           AS "Agg. Leistungsbedarf Heizung (kW)",
       ROUND(SUM("powerHotWaterW") / 1000, 2)          AS "Agg. Leistungsbedarf Warmwasser (kW)"
FROM building
GROUP BY
    ROLLUP (groupname)
ORDER BY groupname <> 'Gesamt', groupname;

SELECT *
FROM building_group_aggregation;

SELECT "Agg. Wärmebedarf Heizung (MWh/a)" + "Agg. Wärmebedarf Warmwasser (MWh/a)"     AS "Gesamtwärmebedarf (MWh)",
       "Agg. Leistungsbedarf Heizung (kW)" + "Agg. Leistungsbedarf Warmwasser (kW)"   AS "Gesamtleistung (kW)",
       ("Agg. Wärmebedarf Heizung (MWh/a)" + "Agg. Wärmebedarf Warmwasser (MWh/a)") /
       ("Agg. Leistungsbedarf Heizung (kW)" + "Agg. Leistungsbedarf Warmwasser (kW)") AS "Vollaststunden"
FROM building_group_aggregation
WHERE "Gebäudegruppe" = 'Gesamt';


SELECT CASE
           WHEN GROUPING(groupname) = 1
               THEN 'Gesamt'
           ELSE groupname
           END                       AS "Gebäudegruppe",
       ROUND(SUM("livingAreaQM"), 2) AS "Wohnfläche (m²)"
FROM building
GROUP BY
    ROLLUP (groupname)
ORDER BY groupname <> 'Gesamt', groupname;


DROP VIEW IF EXISTS building_type_aggregation;
CREATE VIEW building_type_aggregation AS
SELECT CASE
           WHEN GROUPING("type") = 1
               THEN 'Gesamt'
           ELSE "type"
           END                                                             AS "Gebäudetyp",
       ROUND(SUM("demandHeatingWH") / 1000 / 1000, 2)                      AS "Agg. Wärmebedarf Heizung (MWh/a)",
       ROUND(SUM("demandHotWaterWH") / 1000 / 1000, 2)                     AS "Agg. Wärmebedarf Warmwasser (MWh/a)",
       ROUND(SUM("demandHeatingWH" + "demandHotWaterWH") / 1000 / 1000, 2) AS "Agg. Wärmebedarf H+WW (MWh/a)",
       ROUND(SUM("powerHeatingW") / 1000, 2)                               AS "Agg. Leistungsbedarf Heizung (kW)",
       ROUND(SUM("powerHotWaterW") / 1000, 2)                              AS "Agg. Leistungsbedarf Warmwasser (kW)"
FROM building
GROUP BY
    ROLLUP ("type")
ORDER BY "type" <> 'Gesamt', "type";
SELECT *
FROM building_type_aggregation;