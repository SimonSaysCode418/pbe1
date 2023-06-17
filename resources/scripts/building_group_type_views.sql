DROP VIEW IF EXISTS "Wärme- und Leistungsbedarf (Gebäudegruppen)";
CREATE VIEW "Wärme- und Leistungsbedarf (Gebäudegruppen)" AS
SELECT CASE
           WHEN GROUPING(groupname) = 1
               THEN 'Gesamt'
           ELSE groupname
           END                                              AS "Gebäudegruppe",
       ROUND(SUM("demandHeating") / 1000 / 1000, 2)         AS "Agg. Wärmebedarf Heizung (MWh/a)",
       ROUND(SUM("demandHotWater") / 1000 / 1000, 2)        AS "Agg. Wärmebedarf Warmwasser (MWh/a)",
       ROUND(SUM("powerHeating") / 1000, 2)                 AS "Agg. Leistungsbedarf Heizung (kW)",
       ROUND(SUM("powerHotWater") / 1000, 2)                AS "Agg. Leistungsbedarf Warmwasser (kW)",
       ROUND(SUM("demandHeating") / SUM("powerHeating"), 2) AS "Volllastunden"
FROM building
GROUP BY
    ROLLUP (groupname)
ORDER BY groupname <> 'Gesamt', groupname;

DROP VIEW IF EXISTS "Wärme- und Leistungsbedarf (Gebäudetypen)";
CREATE VIEW "Wärme- und Leistungsbedarf (Gebäudetypen)" AS
SELECT CASE
           WHEN GROUPING("type") = 1
               THEN 'Gesamt'
           ELSE "type"
           END                                              AS "Gebäudetyp",
       ROUND(SUM("demandHeating") / 1000 / 1000, 2)         AS "Agg. Wärmebedarf Heizung (MWh/a)",
       ROUND(SUM("demandHotWater") / 1000 / 1000, 2)        AS "Agg. Wärmebedarf Warmwasser (MWh/a)",
       ROUND(SUM("powerHeating") / 1000, 2)                 AS "Agg. Leistungsbedarf Heizung (kW)",
       ROUND(SUM("powerHotWater") / 1000, 2)                AS "Agg. Leistungsbedarf Warmwasser (kW)",
       ROUND(SUM("demandHeating") / SUM("powerHeating"), 2) AS "Volllastunden"
FROM building
GROUP BY
    ROLLUP ("type")
ORDER BY "type" <> 'Gesamt', "type";

DROP VIEW IF EXISTS "Wohnfläche (Gebäudegruppen)";
CREATE VIEW "Wohnfläche (Gebäudegruppen)" AS
SELECT CASE
           WHEN GROUPING(groupname) = 1
               THEN 'Gesamt'
           ELSE groupname
           END           AS "Gebäudegruppe",
       SUM("livingArea") AS "Wohnfläche (m²)"
FROM building
WHERE "type" = 'Residential'
   OR "type" = 'Apartments'
GROUP BY
    ROLLUP (groupname)
ORDER BY groupname <> 'Gesamt', groupname;

DROP VIEW IF EXISTS "Arbeitsfläche (Gebäudegruppen)";
CREATE VIEW "Arbeitsfläche (Gebäudegruppen)" AS
SELECT CASE
           WHEN GROUPING(groupname) = 1
               THEN 'Gesamt'
           ELSE groupname
           END           AS "Gebäudegruppe",
       SUM("livingArea") AS "Arbeitsfläche (m²)"
FROM building
WHERE "type" = 'Commerce'
   OR "type" LIKE 'Fire%'
GROUP BY
    ROLLUP (groupname)
ORDER BY groupname <> 'Gesamt', groupname;

SELECT *
FROM "Wärme- und Leistungsbedarf (Gebäudegruppen)";

SELECT *
FROM "Wärme- und Leistungsbedarf (Gebäudetypen)";

SELECT *
FROM "Wohnfläche (Gebäudegruppen)";

SELECT *
FROM "Arbeitsfläche (Gebäudegruppen)";