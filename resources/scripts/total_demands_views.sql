DROP VIEW IF EXISTS "Energiebedarf des Quartiers" CASCADE;
CREATE VIEW "Energiebedarf des Quartiers" AS
SELECT building_data.*,
       "Jährlicher Energiebedarf Heizung netto (MWh)" +
       "Jährlicher Energiebedarf Warmwasser netto (MWh)" AS "Jährlicher Gesamtenergiebedarf netto (MWh)",
       pipe_data."Jährlicher Energieverlust Netz (MWh)",
       ROUND(ROUND(pipe_data."Jährlicher Energieverlust Netz (MWh)", 2) /
             ROUND("Jährlicher Energiebedarf Heizung netto (MWh)" +
                   "Jährlicher Energiebedarf Warmwasser netto (MWh)" +
                   "Jährlicher Energieverlust Netz (MWh)", 2)
                 * 100.0, 2)                             AS "Anteil Energieverlust Netz (%)",
       "Jährlicher Energiebedarf Heizung netto (MWh)" +
       "Jährlicher Energiebedarf Warmwasser netto (MWh)" +
       "Jährlicher Energieverlust Netz (MWh)"            AS "Jährlicher Gesamtenergiebedarf brutto (MWh)"
FROM (SELECT ROUND(SUM("demandHeating") / 1000000.0, 2)  AS "Jährlicher Energiebedarf Heizung netto (MWh)",
             ROUND(SUM("demandHotWater") / 1000000.0, 2) AS "Jährlicher Energiebedarf Warmwasser netto (MWh)"
      FROM building) AS building_data,
     (SELECT ROUND(SUM((pipe."heatLossWinter" + pipe."heatLossSummer") / 2) * 8760.0 / 1000000.0,
                   2) AS "Jährlicher Energieverlust Netz (MWh)"
      FROM pipe) AS pipe_data;

DROP VIEW IF EXISTS "Leistungsbedarf des Quartiers" CASCADE;
CREATE VIEW "Leistungsbedarf des Quartiers" AS
SELECT building_data."Leistungsbedarf Heizung netto (kW)",
       building_data."Gleichzeitigkeit Heizung [20%] (kW)",
       building_data."Leistungsbedarf Heizung netto [80%] (kW)",
       pipe_data."Leistungsverlust Netz (kW)" AS "Leistungsverlust Netz Winter (kW)",
       ROUND(ROUND(pipe_data."Leistungsverlust Netz (kW)", 2) /
             ROUND(building_data."Leistungsbedarf Heizung netto [80%] (kW)" +
                   pipe_data."Leistungsverlust Netz (kW)", 2)
                 * 100.0, 2)                  AS "Anteil Leistungsverlust Netz Winter (%)",
       building_data."Leistungsbedarf Heizung netto [80%] (kW)" +
       pipe_data."Leistungsverlust Netz (kW)" AS "Gesamtleistungsbedarf Winter (kW)",

       building_data."Leistungsbedarf Warmwasser netto (kW)",
       building_data."Gleichzeitigkeit Warmwasser [20%] (kW)",
       building_data."Leistungsbedarf Warmwasser netto [80%] (kW)",
       pipe_data."Leistungsverlust Netz (kW)" AS "Leistungsverlust Netz Sommer (kW)",
       ROUND(ROUND(pipe_data."Leistungsverlust Netz (kW)", 2) /
             ROUND(building_data."Leistungsbedarf Warmwasser netto [80%] (kW)" +
                   pipe_data."Leistungsverlust Netz (kW)", 2)
                 * 100.0, 2)                  AS "Anteil Leistungsverlust Netz Sommer (%)",
       building_data."Leistungsbedarf Warmwasser netto [80%] (kW)" +
       pipe_data."Leistungsverlust Netz (kW)" AS "Gesamtleistungsbedarf Sommer (kW)"
FROM (SELECT ROUND(SUM("powerHeating") / 1000.0, 2)        AS "Leistungsbedarf Heizung netto (kW)",
             ROUND(SUM("powerHeating") * 0.2 / 1000.0, 2)  AS "Gleichzeitigkeit Heizung [20%] (kW)",
             ROUND(SUM("powerHeating") * 0.8 / 1000.0, 2)  AS "Leistungsbedarf Heizung netto [80%] (kW)",
             ROUND(SUM("powerHotWater") / 1000.0, 2)       AS "Leistungsbedarf Warmwasser netto (kW)",
             ROUND(SUM("powerHotWater") * 0.2 / 1000.0, 2) AS "Gleichzeitigkeit Warmwasser [20%] (kW)",
             ROUND(SUM("powerHotWater") * 0.8 / 1000.0, 2) AS "Leistungsbedarf Warmwasser netto [80%] (kW)"
      FROM building) AS building_data,
     (SELECT ROUND(SUM((pipe."heatLossWinter" + pipe."heatLossSummer") / 2) / 1000.0, 2) AS "Leistungsverlust Netz (kW)"
      FROM pipe) AS pipe_data;

SELECT *
FROM "Leistungsbedarf des Quartiers";

DROP VIEW IF EXISTS "Volllaststunden des Quartiers" CASCADE;
CREATE VIEW "Volllaststunden des Quartiers" AS
SELECT "Jährlicher Energiebedarf Heizung netto (MWh)",
       "Leistungsbedarf Heizung netto (kW)",
       "Jährlicher Energiebedarf Warmwasser netto (MWh)",
       "Leistungsbedarf Warmwasser netto (kW)",
       ROUND("Jährlicher Energiebedarf Heizung netto (MWh)" * 1000.0 / "Leistungsbedarf Heizung netto (kW)")
           AS "Volllaststunden Heizung",
       ROUND("Jährlicher Energiebedarf Warmwasser netto (MWh)" * 1000.0 / "Leistungsbedarf Warmwasser netto (kW)")
           AS "Volllaststunden Warmwasser"
FROM "Energiebedarf des Quartiers",
     "Leistungsbedarf des Quartiers";